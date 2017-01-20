import glob
import os
import subprocess
from multiprocessing import Pool

source_directory = 'Source'

def find_images(source_directory):
	files_path = os.path.join(source_directory, '*.jpg')
	return glob.glob(files_path)

def create_thumbnail(filename, new_size = '200', destination_directory = 'resize'):
	if not(os.path.exists(destination_directory)):
		os.mkdir(destination_directory)
	destination_file_name = os.path.join(destination_directory, os.path.basename(filename))
	subprocess.run(['convert', filename, '-resize', new_size, destination_file_name])

if __name__ == '__main__':
	
	files = find_images(source_directory)

	# Один поток
	#for f in files:
	#	create_thumbnail(f)

	# Многопоточность (4)
	pool = Pool(4)
	pool.map(create_thumbnail, files)
	pool.close()
	pool.join()