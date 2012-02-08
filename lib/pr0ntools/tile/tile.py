#!/usr/bin/python
'''
pr0ntile: IC die image stitching and tile generation
Copyright 2012 John McMaster <JohnDMcMaster@gmail.com>
Licensed under a 2 clause BSD license, see COPYING for details
'''

import sys 
import os.path
import pr0ntools.pimage
from pr0ntools.pimage import PImage
from pr0ntools.pimage import TempPImage
from pr0ntools.stitch.wander_stitch import WanderStitch
from pr0ntools.stitch.grid_stitch import GridStitch
from pr0ntools.stitch.fortify_stitch import FortifyStitch
from pr0ntools.execute import Execute
import Image

'''
Take a single large image and break it into tiles
'''
class ImageTiler:
	def __init__(self, image, x0 = None, x1 = None, y0 = None, y1 = None, tw = 256, th = 256):
		self.image = image
		
		if x0 is None:
			x0 = 0
		self.x0 = x0
		if x1 is None:
			x1 = i.width()
		self.x1 = x1
		if y0 is None:
			y0 = 0
		self.y0 = y0
		if y1 is None:
			y1 = i.height()
		self.y1 = y1
		
		self.tw = tw
		self.th = th
		self.out_dir = None

	# FIXME / TODO: this isn't the google reccomended naming scheme, look into that more	
	# part of it was that I wanted them to sort nicely in file list view
	def get_name(self, row, col):
		out_dir = ''
		if self.out_dir:
			out_dir = '%s/' % self.out_dir
		return '%sy%03d_x%03d%s' % (out_dir, row, col, out_extension)
		
	def make_tile(self, x, y, row, col):
		xmin = x
		ymin = y
		xmax = min(xmin + self.tw, self.x1)
		ymax = min(ymin + self.th, self.y1)
		nfn = self.get_name(row, col)

		print '%s: (x %d:%d, y %d:%d)' % (nfn, xmin, xmax, ymin, ymax)
		ip = i.subimage(xmin, xmax, ymin, ymax)
		'''
		Images must be padded
		If they aren't they will be stretched in google maps
		'''
		if ip.width() != t_width or ip.height() != t_height:
			print 'WARNING: %s: expanding partial tile (%d X %d) to full tile size' % (nfn, ip.width(), ip.height())
			ip.set_canvas_size(t_width, t_height)
		ip.image.save(nfn)
		
	def run(self):
		'''
		Namer is a function that accepts the following arguments and returns a string:
		namer(row, col)
	
		python can bind objects to functions so a user parameter isn't necessary?
		'''
	
		if namer is None:
			namer = google_namer

		col = 0
		for x in xrange(self.x0, self.x1, self.tw):
			row = 0
			for y in xrange(self.y0, self.y1, self.th):
				self.make_tile(x, y, row, col)
				row += 1
			col += 1

'''
Creates smaller tiles from source tiles
'''
class TileTiler:
	def __init__(self, file_names, max_level, min_level = 0, out_dir_base=None):
		self.map = ImageCoordinateMap.from_tagged_file_names(file_names)
		self.max_level = max_level
		self.min_level = min_level
		self.out_dir_base = out_dir_base
		self.out_extension = '.jpg'
		self.zoom_factor = 2
		#self.out_extension = '.png'

	def prep_out_dir_base(self):
		if self.out_dir_base is None:
			self.out_dir_base = 'tiles_out/'
		if os.path.exists(out_dir_base):
			os.system('rm -rf %s' % out_dir_base)
		os.mkdir(out_dir_base)

	def get_old(self, col, row):
		return self.map.get_image(col, row)

	def get_fn(self, row, col):
		return '%s/%d/y%03d_x%03d%s' % (self.out_dir_base, self.zoom_level, row, col, self.out_extension)

	def run(self):
		self.prep_out_dir_base()
		t_width = 256
		t_height = 256
		
		for self.zoom_level in xrange(max_level, min_level - 1, -1):
			print
			print '************'
			print 'Zoom level %d' % zoom_level
			out_dir = '%s/%d' % (out_dir_base, zoom_level)
			if os.path.exists(out_dir):
				os.system('rm -rf %s' % out_dir)
			os.mkdir(out_dir)
			
			# For the first level we copy things over
			if zoom_level == max_level:
				for (img_fn, row, col) in self.map.images():
					dst = self.get_fn(row, col)
					shutil.copy(img_fn, dst)
			# Additional levels we take the image coordinate map and shrink
			else:
				# Prepare a new image coordinate map so we can form the next tile set
				new_cols = math.ceil(self.map.width() / self.zoom_factor)
				new_rows = math.ceil(self.map.height() / self.zoom_factor)
				new_map = ImageCoordinateMap(new_cols, new_rows)
				for new_row in new_rows:
					old_row = new_row * self.zoom_factor
					for col in new_cols:
						old_col = new_col * self.zoom_factor
						# Paste the old (4) images together
						imgp = PImage.from_filename_array([[self.get_old(old_row + 0, old_col + 0), self.get_old(old_row + 0, old_col + 1)],
								[self.get_old(old_row + 1, old_col + 0), self.get_old(old_row + 1, old_col + 1)]])
						if imgp.width() != t_width * self.zoom_factor or imgp.height() != t_height * self.zoom_factor:
							raise Exception('Combined image incorrect size')
						scaled = imgp.get_scaled(0.5, file=Image.ANTIALIAS)
						if scaled.width() != t_width or scaled.height() != t_height:
							raise Exception('Scaled image incorrect size')
						
						new_fn = self.get_fn(new_row, new_col)
						new_map.set_image(new_col, new_row)
				# Next shrink will be on the previous tile set, not the original
				self.map = new_map
# replaces from_single
class SingleTiler:
	def __init__(self, fn, max_level, min_level = 0, out_dir_base=None):
		self.fn = fn
		self.max_level = max_level
		self.min_level = min_level
		self.out_dir_base = out_dir_base

	def run(self):
		fn = self.fn
		max_level = self.max_level
		min_level = self.min_level
		out_dir_base = self.out_dir_base
	
	
		t_width = 256
		t_height = 256
		out_extension = '.jpg'
		#out_extension = '.png'
		'''
		Expect that will not need images larger than 1 terapixel in the near future
		sqrt(1 T / (256 * 256)) = 3906, in hex = 0xF42
		so three hex digits should last some time
		'''
		if out_dir_base is None:
			out_dir_base = 'tiles_out/'
	
		'''
		Test file is the carved out metal sample of the 6522
		It is 5672 x 4373 pixels
		I might do a smaller one first
		'''
		i = PImage.from_file(fn)
		if os.path.exists(out_dir_base):
			os.system('rm -rf %s' % out_dir_base)
		os.mkdir(out_dir_base)
		for zoom_level in xrange(max_level, min_level - 1, -1):
			print
			print '************'
			print 'Zoom level %d' % zoom_level
			out_dir = '%s/%d' % (out_dir_base, zoom_level)
			if os.path.exists(out_dir):
				os.system('rm -rf %s' % out_dir)
			os.mkdir(out_dir)
		
			tiler = ImageTiler(i)
			tiler.run()
		
			if zoom_level != min_level:
				# Each zoom level is half smaller than previous
				i = i.get_scaled(0.5)
				if 0:
					i.save('test.jpg')
					sys.exit(1)


