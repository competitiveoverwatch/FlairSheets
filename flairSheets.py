from PIL import Image, ImageEnhance
import os, json, sys

 
def makeSpritesheet(sheet, size=(22,22), suffix=None, writejson=True):
	# get flairlist
	with open(os.path.join(sheet, 'flairlist.json')) as flairfile:
		flairlist = sorted(json.load(flairfile), key=lambda k: k['id']) 
		
	# create spritesheet basestring
	rows = int((len(flairlist)-1)/10) + 1
	spritesheetSize = (10*size[0],rows*size[1])
	spritesheet = Image.new('RGBA', spritesheetSize)

	flairinfos = dict()
	for index, flair in enumerate(flairlist):
		flairinfo = dict()
		flairinfo['name'] = flair['name']
	
		# open image
		image = Image.open(os.path.join(sheet, flair['id'] + '.png'))
		image = image.convert('RGBA')
		image.thumbnail(size, Image.ANTIALIAS)
		imageSize = image.size
		
		# calculate row, column
		row = int(index/10)
		col = index%10
		
		# calculate offset
		offsetX = ((size[0] - imageSize[0]) / 2)  +  col * size[0]
		offsetY = ((size[1] - imageSize[1]) / 2)  +  row * size[1]
		offset = (int(offsetX), int(offsetY)) 
		
		if not flair['active']:
			# desaturate
			colorConverter = ImageEnhance.Color(image)
			image = colorConverter.enhance(0.1)
			# 50% transparency
			bands = list(image.split())
			if len(bands) == 4:
				# Assuming alpha is the last band
				bands[3] = bands[3].point(lambda x: x*0.5)
			image = Image.merge(image.mode, bands)
			
		
		# insert image
		spritesheet.paste(image, offset)
		
		# update flair
		flairinfo['row'] = '%02d' % (row + 1)
		flairinfo['col'] = '%02d' % (col + 1)
		flairinfo['sheet'] = sheet
		flairinfos[flair['id']] = flairinfo
		
	# output spritesheet
	filename = 'flair-' + sheet
	if suffix:
		filename += '-' + suffix
	filename += '.png'
	spritesheet.save(os.path.join('output', filename), quality=95)
	
	# save flairlist
	if writejson:
		# write flairinfo
		filename = 'flair-' + sheet + '.json'
		with open(os.path.join('output', filename), 'w') as flairfile:
			json.dump(flairinfos, flairfile, indent=4)
		# rewrite flairlist
		with open(os.path.join(sheet, 'flairlist.json'), 'w') as flairfile:
			json.dump(flairlist, flairfile, indent=4)

if len(sys.argv) != 2:
	quit()
			
makeSpritesheet(sys.argv[1], size=(22,22))
makeSpritesheet(sys.argv[1], size=(44,44), suffix='2x', writejson=False)