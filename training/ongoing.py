'''
PLDA implementation from
https://github.com/RaviSoji/plda/blob/master/mnist_demo/mnist_demo.ipynb
'''

import os, sys, pickle, json
import numpy as np
import matplotlib.pyplot as plt

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

def get_folders(listdir):
	folders=list()
	for i in range(len(listdir)):
		if listdir[i].find('.') < 0:
			folders.append(listdir[i])

	return folders 

def classifyfolder(listdir):
	filetypes=list()
	for i in range(len(listdir)):
		if listdir[i].endswith(('.mp3', '.wav')):
			filetypes.append('audio')
		elif listdir[i].endswith(('.png', '.jpg')):
			filetypes.append('image')
		elif listdir[i].endswith(('.txt')):
			filetypes.append('text')
		elif listdir[i].endswith(('.mp4', '.avi')):
			filetypes.append('video')
		elif listdir[i].endswith(('.csv')):
			filetypes.append('csv')

	counts={'audio': filetypes.count('audio'),
			'image': filetypes.count('image'),
			'text': filetypes.count('text'),
			'video': filetypes.count('video'),
			'csv': filetypes.count('.csv')}

	# get back the type of folder (main file type)
	countlist=list(counts)
	countvalues=list(counts.values())
	maxvalue=max(countvalues)
	maxind=countvalues.index(maxvalue)
	return countlist[maxind]

# load the default feature set 
cur_dir = os.getcwd()
prevdir= prev_dir(cur_dir)
sys.path.append(prevdir+'/train_dir')
settings=json.load(open(prevdir+'/settings.json'))

# get all the default feature arrays 
default_audio_features=settings['default_audio_features']
default_text_features=settings['default_text_features']
default_image_features=settings['default_image_features']
default_video_features=settings['default_video_features']
default_csv_features='csv'

# prepare training and testing data (should have been already featurized) - # of classes/folders
os.chdir(prevdir+'/train_dir')

data_dir=os.getcwd()
listdir=os.listdir()
folders=get_folders(listdir)

# now assess folders by content type 
data=dict()
for i in range(len(folders)):
	os.chdir(folders[i])
	listdir=os.listdir()
	filetype=classifyfolder(listdir)
	data[folders[i]]=filetype 
	os.chdir(data_dir)

# now ask user what type of problem they are trying to solve 
problemtype=input('what problem are you solving? (1-audio, 2-text, 3-image, 4-video, 5-csv)\n')
while problemtype not in ['1','2','3','4','5']:
	print('answer not recognized...')
	problemtype=input('what problem are you solving? (1-audio, 2-text, 3-image, 4-video, 5-csv)\n')

if problemtype=='1':
	problemtype='audio'
elif problemtype=='2':
	problemtype='text'
elif problemtype=='3':
	problemtype='image'
elif problemtype=='4':
	problemtype='video'
elif problemtype=='5':
	problemtype=='csv'

print('\n OK cool, we got you modeling %s files \n'%(problemtype))
count=0
availableclasses=list()
for i in range(len(folders)):
    if data[folders[i]]==problemtype:
    	availableclasses.append(folders[i])
    	count=count+1
classnum=input('how many classes would you like to model? (%s available) \n'%(str(count)))
print('these are the available classes: ')
print(availableclasses)
probtype=input('is this a classification (c) or regression (r) problem?')
while probtype not in ['c','r']:
	print('input not recognized...')
	probtype=input('is this a classification (c) or regression (r) problem?')

# now run train_audioclassify.py | train_audioTPOT.py | train_ludwig.py 
# now run train_audioregression.py | train_audioTPOT.py | train_ludwig.py
