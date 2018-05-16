from PIL import Image, ImageEnhance
import os, json, sys, csv, pprint, tinify

tinify.key = 'I6ImYtMy1dzeC6mOpo2kJMNCw4TvuL33'

def resize(matrix, row, col=0):
	"""resize the matrix to requried size"""
	current_size = len(matrix)
	new_size = (row if row > col else col) + 1
	if new_size > current_size:
		new_matrix = [[None for x in range(new_size)] for y in range(new_size)]
		for i in range(len(matrix)):
			for j in range(len(matrix[i])):
				new_matrix[i][j] = matrix[i][j]
		return new_matrix
	return matrix

def place_flair(matrix, id):
	# try to place in current matrix
	for i in range(len(matrix)):
		for j in range(len(matrix[i])):
			if matrix[i][j] == None:
				matrix[i][j] = id
				return (matrix,i+1,j+1)
	# could not place -> increase matrix size
	matrix = resize(matrix, len(matrix))
	matrix[0][len(matrix)-1] = id
	return (matrix,1,len(matrix))

def make_spritesheet(sheet, size=(22,22), suffix=None):
	# get flairlist
	with open(os.path.join(sheet, 'flairlist.json')) as flairfile:
		flairlist = json.load(flairfile)

	# create matrix with known flairs
	flair_matrix = []
	for index, flair_id in enumerate(flairlist):
		row = int(flairlist[flair_id]['row']) - 1
		col = int(flairlist[flair_id]['col']) - 1		
		flair_matrix = resize(flair_matrix, row, col)
		flair_matrix[row][col] = flair_id

	# update with csv sheet
	with open(os.path.join(sheet, '_flairsheet.csv')) as csvfile:
		csvlist = csv.reader(csvfile, delimiter=',')
		next(csvlist) #skip first line (header)
		for row in csvlist:
			flair_id = row[1]
			active = True
			if row[2] == 'FALSE':
				active = False
			# new flair
			if flair_id not in flairlist:
				# place in matrix
				flair_matrix, row_num, col_num =  place_flair(flair_matrix, flair_id)
				flairlist[flair_id] = {'name': row[0], 'active': active, 'sheet': sheet, 'row': '%02d' % row_num, 'col': '%02d' % col_num}
			# update old flair
			else:
				flairlist[flair_id]['active'] = active
				flairlist[flair_id]['name'] = row[0]



	# create spritesheet basestring
	spritesheet_size = (len(flair_matrix)*size[0],len(flair_matrix)*size[1])
	spritesheet = Image.new('RGBA', spritesheet_size)

	for i in range(len(flair_matrix)):
		for j in range(len(flair_matrix[i])):
			flair_id = flair_matrix[i][j]
			if not flair_id:
				continue

			# open image
			image = Image.open(os.path.join(sheet, flair_id + '.png'))
			image = image.convert('RGBA')
			image.thumbnail(size, Image.ANTIALIAS)
			imageSize = image.size

			# calculate row, column
			row_num = int(flairlist[flair_id]['row']) - 1
			col_num = int(flairlist[flair_id]['col']) - 1

			# calculate offset
			offsetX = ((size[0] - imageSize[0]) / 2)  +  col_num * size[0]
			offsetY = ((size[1] - imageSize[1]) / 2)  +  row_num * size[1]
			offset = (int(offsetX), int(offsetY)) 

			# faded flair
			if not flairlist[flair_id]['active']:
				# desaturate
				colorConverter = ImageEnhance.Color(image)
				image = colorConverter.enhance(0.2)
				# 50% transparency
				bands = list(image.split())
				if len(bands) == 4:
					# Assuming alpha is the last band
					bands[3] = bands[3].point(lambda x: x*0.5)
				image = Image.merge(image.mode, bands)
                
			# insert image
			spritesheet.paste(image, offset)

	# output spritesheet
	filename = 'flairs-' + sheet + '.png'
	path = os.path.join('output', filename)
	spritesheet.save(path, quality=95, optimize=True)

	# optimize
	if os.path.getsize(path) > 500000:
		tinify.from_file(path).to_file(path)

	# write flairinfo
	filename = 'flairs-' + sheet + '.json'
	with open(os.path.join('output', filename), 'w') as flairfile:
		json.dump(flairlist, flairfile, indent=4)
	with open(os.path.join(sheet, 'flairlist.json'), 'w') as flairfile:
		json.dump(flairlist, flairfile, indent=4)

def make_team_categories(categories):
	with open(os.path.join('output', 'flairs-teams.json')) as flairfile:
		flairlist = json.load(flairfile)
    
	active = []
	inactive = []
	for key, value in flairlist.items():
		if value['active']:
			active.append(key)
		else:
			inactive.append(key)
			
	active.sort()
	inactive.sort()        

	activeDict = dict()
	activeDict['title'] = "Team Flairs"
	activeDict['items'] = active
	inactiveDict = dict()
	inactiveDict['title'] = "Legacy Team Flairs"
	inactiveDict['items'] = inactive

	categories.append(activeDict)
	categories.append(inactiveDict)
	return categories

def make_flairs_json():
	flairs = dict()
	all_flairs = dict()
	for file in os.listdir('output'):
		if file.endswith('.json') and 'flairs-' in file:
			with open(os.path.join('output', file)) as jsonfile:
				flairs_json = json.load(jsonfile)
				all_flairs.update(flairs_json)

	with open('categories.json') as categories_json:
		categories = json.load(categories_json)

	categories = make_team_categories(categories)

	with open('specials.json') as specials_json:
		specials = json.load(specials_json)

	flairs['categories'] = categories
	flairs['specials'] = specials
	flairs['flairs'] = all_flairs
	flairs['ranks'] = {'title': 'Rank', 'items': ['bronze', 'silver', 'gold', 'platinum', 'diamond', 'master', 'grandmaster']}

	with open(os.path.join('output', 'flairs.json'), 'w') as flairfile:
		json.dump(flairs, flairfile, indent=4)

if len(sys.argv) < 2:
	quit()

for sheet in sys.argv[1:]:
	make_spritesheet(sheet, size=(128,128))

make_flairs_json()