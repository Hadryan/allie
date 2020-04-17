'''
Make transformations in this order:

Feature scalers --> reduce dimensions --> select features.

A --> A`--> A`` --> A```

Can do this through scikit-leran pipelines.
'''

import json, os, sys
import numpy as np 
from sklearn import preprocessing
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from tqdm import tqdm
import pickle

def prev_dir(directory):
	g=directory.split('/')
	dir_=''
	for i in range(len(g)):
		if i != len(g)-1:
			if i==0:
				dir_=dir_+g[i]
			else:
				dir_=dir_+'/'+g[i]
	# print(dir_)
	return dir_

def get_classes():
	count=2
	classes=list()
	while True:
		try:
			class_=sys.argv[count]
			classes.append(class_)
			print(classes)
			count=count+1
		except:
			break

	return classes

def get_features(classes, problem_type):

	features=list()
	feature_labels=list()
	class_labels=list()
	curdir=os.getcwd()

	for i in range(len(classes)):

		print('----------LOADING %s----------'%(classes[i].upper()))
		os.chdir(curdir+'/'+classes[i])
		listdir=os.listdir()
		jsonfiles=list()

		for j in range(len(listdir)):
			if listdir[j].endswith('.json'):
				jsonfiles.append(listdir[j])

		g=json.load(open(jsonfiles[0]))
		feature_list=list(g['features'][problem_type])

		for j in tqdm(range(len(jsonfiles))):
			g=json.load(open(jsonfiles[j]))
			feature_=list()
			label_=list()
			try:
				for k in range(len(feature_list)):
					feature_=feature_+g['features'][problem_type][feature_list[k]]['features']
					label_=label_+g['features'][problem_type][feature_list[k]]['labels']

				# quick quality check to only add to list if the feature_labels match in length the features_
				if len(feature_) == len(label_):
					features.append(feature_)
					feature_labels.append(label_)
					class_labels.append(classes[i])
			except:
				print('error loading feature embedding: %s'%(feature_list[k].upper()))


	return features, feature_labels, class_labels 

################################################
##	    		Load main settings    		  ##
################################################

# directory=sys.argv[1]
basedir=os.getcwd()
settingsdir=prev_dir(basedir)
print(settingsdir)
settings=json.load(open(settingsdir+'/settings.json'))

# get all the important settings for the transformations 
scale_features=settings['scale_features']
reduce_dimensions=settings['reduce_dimensions']
select_features=settings['select_features']
default_scalers=settings['default_scaler']
default_reducers=settings['default_dimensionality_reducer']
default_selectors=settings['default_feature_selector']

print(scale_features)
print(reduce_dimensions)
print(select_features)
print(default_scalers)
print(default_reducers)
print(default_selectors)

os.chdir(basedir)

################################################
##	    	Now go featurize!                 ##
################################################

# get current directory 
curdir=os.getcwd()
basedir=prev_dir(curdir)
os.chdir(basedir+'/train_dir')
problem_type=sys.argv[1]

classes=get_classes()
features, feature_labels, class_labels = get_features(classes, problem_type)
X_train, X_test, y_train, y_test = train_test_split(features, class_labels, train_size=0.90, test_size=0.10)

print(features[0])
print(feature_labels[1])
print(class_labels[0])

component_num=int(len(features[0])/3)

# create a scikit-learn pipeline 
estimators = []

################################################
##	    	    Scale features               ##
################################################
if scale_features == True:
	import feature_scale as fsc_
	for i in range(len(default_scalers)):
		feature_scaler=default_scalers[i]
		print(feature_scaler.upper())
		scaler_model=fsc_.feature_scale(feature_scaler, X_train, y_train)
		# print(len(scaler_model))
		estimators.append((feature_scaler, scaler_model))

################################################
##	    	   Reduce dimensions              ##
################################################
if reduce_dimensions == True:
	import feature_reduce as fre_
	for i in range(len(default_reducers)):
		feature_reducer=default_reducers[i]
		print(feature_reducer.upper()+' - %s features'%(str(component_num)))
		dimension_model=fre_.feature_reduce(feature_reducer, X_train, y_train, component_num)
		# print(len(dimension_model))
		estimators.append((feature_reducer, dimension_model))

################################################
##	    	   Feature selection              ##
################################################
if select_features == True:
	import feature_select as fse_
	for i in range(len(default_selectors)):
		feature_selector=default_selectors[i]
		print(feature_selector.upper())
		selection_model=fse_.feature_select(feature_selector, X_train, y_train, int(component_num/2))
		estimators.append((feature_selector, selection_model))

print(estimators)
model=Pipeline(estimators)
model=model.fit(X_train, y_train)
print(len(X_test))
X_test=model.transform(X_test)
print(len(X_test))

# pickle me timbers
os.chdir(curdir)
print(os.getcwd())

try:
	os.chdir('%s_transformer'%(problem_type))
except:
	os.mkdir('%s_transformer'%(problem_type))
	os.chdir('%s_transformer'%(problem_type))

# get filename / create a unique file name
filename=problem_type

for i in range(len(classes)):
	filename=filename+'_'+classes[i]

# only add names in if True 
if scale_features == True:
	for i in range(len(default_scalers)):
		filename=filename+'_'+default_scalers[i]
if reduce_dimensions == True:
	for i in range(len(default_reducers)):
		filename=filename+'_'+default_reducers[i]
if select_features == True:
	for i in range(len(default_selectors)):
		filename=filename+'_'+default_selectors[i]

model_file=filename+'.pickle'
json_file=filename+'.json'

# create model
modelfile=open(model_file,'wb')
pickle.dump(model, modelfile)
modelfile.close()

print(type(X_train[0]))
print(type(y_train[0]))
print(type(X_test[0]))

# write json file 
data={'estimators': str(estimators),
	  'settings': settings,
	  'classes': list(set(y_test)),
	  'sample input X': X_train[0],
	  'sample input Y': y_train[0],
	  'sample transformed X': X_test[0].tolist(),
	  'sample transformed y': y_train[0],
	 }
jsonfile=open(json_file,'w')
json.dump(data,jsonfile)
jsonfile.close()