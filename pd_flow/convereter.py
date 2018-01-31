# converter to feed into pd flow

import cv2
import glob
import numpy as np 
import scipy.ndimage
from scipy.ndimage import imread
import tqdm
import os 

def load_xyz(filename):
	"""Return image data from a PGM file generated by blensor. """
	fx = 472.92840576171875
	fy = fx 
	with open(filename, 'rb') as f:
		f.readline()
		f.readline()
		width_height = f.readline().strip().split()
		if len(width_height) > 1:
		  width, height = map(int,width_height)
		  value_max_range = float(f.readline())
		  image_ = [float(line.strip()) for line in f.readlines()]
		  if len(image_) == height * width:
			nx,ny = (width,height)
			x_index = np.linspace(0,width-1,width)
			y_index = np.linspace(0,height-1,height)
			xx,yy = np.meshgrid(x_index,y_index)
			xx -= float(width)/2
			yy -= float(height)/2
			xx /= fx
			yy /= fy

			cam_z = np.reshape(image_,(height, width))
			cam_z = cam_z / value_max_range * 1.5
			cam_x = xx * cam_z 
			cam_y = yy * cam_z
			image_z = np.flipud(cam_z)
			image_y = np.flipud(cam_y)
			image_x = np.flipud(cam_x)

			zoom_scale = 0.5
			image_x = scipy.ndimage.zoom(image_x, zoom_scale, order=1)
			image_y = scipy.ndimage.zoom(image_y, zoom_scale, order=1)
			image_z = scipy.ndimage.zoom(image_z, zoom_scale, order=1)
			image = np.dstack((image_x,image_y,image_z))
			return image

	return np.zeros((h,w,3))

# // MAIN

for i in tqdm.tqdm(range(8500)):
	dir = '../'+str(i)
	# dir = '../174'
	print dir 

	for file in glob.glob(dir  +'/frame80*.pgm'):
		z1 = load_xyz(file)[:,:,2]
		z1 = z1*5000
		z1 = z1.astype(np.uint16)
		cv2.imwrite(dir +'/z1_80.png',z1)
		# print z1.shape
		# print z1.dtype
		

	for file in glob.glob(dir +'/frame20*.pgm'):
		z2 = load_xyz(file)[:,:,2]
		z2 = z2*5000
		z2 = z2.astype(np.uint16)
		cv2.imwrite(dir +'/z2_20.png',z2)
		# print z2.shape
		# print z2.dtype
		

	for file in glob.glob(dir +'/frame80*.png'):
		i1 = cv2.imread(file,0)
		i1 = cv2.resize(i1,(320,240))
		cv2.imwrite(dir +'/i1_80.png',i1)
		# print i1.shape
		# print i1.dtype

	for file in glob.glob(dir +'/frame20*.png'):
		i2 = cv2.imread(file,0)
		i2 = cv2.resize(i2,(320,240))
		cv2.imwrite(dir +'/i2_20.png',i2)
		# print i2.shape
		# print i2.dtype

	cmd = 'mkdir -p '+ str(i)
	os.system(cmd)
	init_dir = os.getcwd()
	os.chdir(init_dir+'/' + str(i))
	dir = '../'+dir
	cmd = './../../../PD-Flow/build/Scene-Flow-Impair --i1 ' +\
			dir + '/i1_80.png --i2 ' + dir + '/i2_20.png --z1 '\
			 + dir + '/z1_80.png --z2 ' + dir + '/z2_20.png'
	cmd = cmd + ' --out ' + str(i) +' --no-show '
	os.system(cmd)	
	os.chdir(init_dir)
