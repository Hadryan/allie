import os, json, wget, sys
import csv_features as cf
import os, wget, zipfile 
import shutil

##################################################
##				Helper functions.    			##
##################################################
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

def make_features(sampletype):

	# only add labels when we have actual labels.
	features={'audio':dict(),
			  'text': dict(),
			  'image':dict(),
			  'video':dict(),
			  'csv': dict(),
			  }

	transcripts={'audio': dict(),
				 'text': dict(),
				 'image': dict(),
				 'video': dict(),
				 'csv': dict()}

	models={'audio': dict(),
		 'text': dict(),
		 'image': dict(),
		 'video': dict(),
		 'csv': dict()}
	
	data={'sampletype': sampletype,
		  'transcripts': transcripts,
		  'features': features,
	      	  'models': models,
		  'labels': []}

	return data

def transcribe_csv(csv_file):
	transcript=open(csv_file).read()
	return transcript 

##################################################
##				   Main script  		    	##
##################################################

basedir=os.getcwd()
help_dir=basedir+'/helpers'
prevdir=prev_dir(basedir)

foldername=sys.argv[1]
os.chdir(foldername)

# get class label from folder name 
labelname=foldername.split('/')
if labelname[-1]=='':
	labelname=labelname[-2]
else:
	labelname=labelname[-1]

listdir=os.listdir()
cur_dir=os.getcwd()

# settings 
g=json.load(open(prev_dir(prevdir)+'/settings.json'))
csv_transcribe=g['transcribe_csv']
default_csv_transcriber=g['default_csv_transcriber']
feature_set=g['default_csv_features']

###################################################

# featurize all files accoridng to librosa featurize
for i in range(len(listdir)):

	# make audio file into spectrogram and analyze those images if audio file
	if listdir[i][-4:] in ['.csv']:
		#try:
		csv_file=listdir[i]
		sampletype='csv'
		# I think it's okay to assume audio less than a minute here...
		if listdir[i][0:-4]+'.json' not in listdir:
			# make new .JSON if it is not there with base array schema.
			basearray=make_features(sampletype)

			# get the csv transcript  
			if csv_transcribe==True:
				transcript = transcribe_csv(csv_file)
				transcript_list=basearray['transcripts']
				transcript_list['csv'][default_csv_transcriber]=transcript 
				basearray['transcripts']=transcript_list

			# featurize the csv file 
			features, labels = cf.csv_featurize(csv_file, cur_dir)
			try:
				data={'features':features.tolist(),
					  'labels': labels}
			except:
				data={'features':features,
					  'labels': labels}

			print(features)
			csv_features=basearray['features']['csv']
			csv_features[feature_set]=data
			basearray['features']['csv']=csv_features
			basearray['labels']=[labelname]

			# write to .JSON 
			jsonfile=open(listdir[i][0:-4]+'.json','w')
			json.dump(basearray, jsonfile)
			jsonfile.close()

		elif listdir[i][0:-4]+'.json' in listdir:
			# load the .JSON file if it is there 
			basearray=json.load(open(listdir[i][0:-4]+'.json'))
			transcript_list=basearray['transcripts']

			# only transcribe if you need to (checks within schema)
			if csv_transcribe==True and default_csv_transcriber not in list(transcript_list['csv']):
				transcript = transcribe_csv(csv_file)
				transcript_list['csv'][default_csv_transcriber]=transcript 
				basearray['transcripts']=transcript_list
			else:
				transcript = transcript_list['csv'][default_csv_transcriber]

			# only re-featurize if necessary (checks if relevant feature embedding exists)
			if feature_set not in list(basearray['features']['csv']):
				features, labels = cf.csv_featurize(csv_file, cur_dir)
				print(features)

				try:
					data={'features':features.tolist(),
						  'labels': labels}
				except:
					data={'features':features,
						  'labels': labels}
				
				basearray['features']['audio'][feature_set]=data

			# only add the label if necessary 
			label_list=basearray['labels']
			if labelname not in label_list:
				label_list.append(labelname)
			basearray['labels']=label_list
			transcript_list=basearray['transcripts']

			# overwrite .JSON 
			jsonfile=open(listdir[i][0:-4]+'.json','w')
			json.dump(basearray, jsonfile)
			jsonfile.close()

		#except:
			#print('error')
