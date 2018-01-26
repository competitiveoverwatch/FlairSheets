from PIL import Image, ImageEnhance
import os, json, sys, tinify
 
tinify.key = 'I6ImYtMy1dzeC6mOpo2kJMNCw4TvuL33'
  
  
def resize(matrix, size):
    current_size = len(matrix)
    additional_size = size - current_size
    # resize existing rows
    for row in matrix:
        row.extend([None] * additional_size)
    # add aditional rows
    matrix.extend([[None] * size] * additional_size)

def makeSpritesheet(sheet, size=(22,22), suffix=None, writejson=True, optimize=False):
    # get flairlist
    with open(os.path.join(sheet, 'flairlist.json')) as flairfile:
        flairlist = json.load(flairfile)
        
    spreadsheet_size = 0
    flair_matrix = [[None]]
        
    # situate all flairs
    unplaced_flairs = []
    for index, flair in enumerate(flairlist):
        if 'row' in flair and 'col' in flair:
            # calculate new spreadsheet size if necessary
            new_size = 0
            if flair['row'] > spreadsheet_size:
                new_size = flair['row']
            if flair['col'] > spreadsheet_size and flair['col'] > new_size:
                new_size = flair['col']
            # resize if necessary
            if new_size > 0:
                resize(flair_matrix, new_size + 1)
                spreadsheet_size = new_size
            
            # add the flair
            flair_matrix[flair['row']][flair['col']] = flair
            
        else:
            unplaced_flairs.append(flair)
         
         
    for index, flair in enumerate(unplaced_flairs):
        # try to find a place for the flair
        found_place = False
        for row in range(len(flair_matrix)):
            for col in range(len(flair_matrix)):
                if flair_matrix[row][col] == None:
                    flair['col'] = col
                    flair['row'] = row
                    flair_matrix[row][col] = flair
                    found_place = True
                    break
            if found_place:
                break
        # increase size if no space
        if not found_place:
            resize(flair_matrix, len(flair_matrix)+1)
            spreadsheet_size = len(flair_matrix)
            flair['col'] = len(flair_matrix)-1
            flair['row'] = 0
            flair_matrix[0][len(flair_matrix)-1] = flair
       
    
    # create spritesheet from flair matrix
    spreadsheet_size += 1
    spritesheet_size = (spreadsheet_size*size[0],spreadsheet_size*size[1])
    spritesheet = Image.new('RGBA', spritesheet_size)
    
    flairinfos = dict()
    flairlist = []
    for row in flair_matrix:
        for flair in row:
            if not flair:
                continue
            flairinfo = dict()
            flairinfo['name'] = flair['name']
            
            # open image
            image = Image.open(os.path.join(sheet, flair['id'] + '.png'))
            image = image.convert('RGBA')
            image.thumbnail(size, Image.ANTIALIAS)
            imageSize = image.size
            
            # calculate row, column
            row = flair['row']
            col = flair['col']
            
            # calculate offset
            offsetX = ((size[0] - imageSize[0]) / 2)  +  col * size[0]
            offsetY = ((size[1] - imageSize[1]) / 2)  +  row * size[1]
            offset = (int(offsetX), int(offsetY)) 
            
            # faded flair
            if not flair['active']:
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
            
            # update flair information
            flairinfo['row'] = '%02d' % (row + 1)
            flairinfo['col'] = '%02d' % (col + 1)
            flairinfo['sheet'] = sheet
            flairinfo['active'] = flair['active']
            flairinfos[flair['id']] = flairinfo
            flairlist.append(flair)
    
    # output spritesheet
    filename = 'flairs-' + sheet
    if suffix:
        filename += '-' + suffix
    filename += '.png'
    path = os.path.join('output', filename)
    spritesheet.save(path, quality=95, optimize=True)
    
    # optimize
    if optimize and os.path.getsize(path) > 500000:
        tinify.from_file(path).to_file(path)
    
    # save flairlist
    if writejson:
        # write flairinfo
        filename = 'flairs-' + sheet + '.json'
        with open(os.path.join('output', filename), 'w') as flairfile:
            json.dump(flairinfos, flairfile, indent=4)
        # rewrite flairlist
        with open(os.path.join(sheet, 'flairlist.json'), 'w') as flairfile:
            json.dump(flairlist, flairfile, indent=4)
    
    
            
if len(sys.argv) < 2:
    quit()

optimize = False
if len(sys.argv) == 3 and sys.argv[2] == 'optimize':
    optimize = True
           
makeSpritesheet(sys.argv[1], size=(128,128), optimize=optimize)