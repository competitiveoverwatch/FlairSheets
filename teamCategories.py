import os, json

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

teamCategories = dict()
teamCategories['categories'] = []

activeDict = dict()
activeDict['title'] = "Team Flairs"
activeDict['items'] = active
inactiveDict = dict()
inactiveDict['title'] = "Legacy Team Flairs"
inactiveDict['items'] = inactive

teamCategories['categories'].append(activeDict)
teamCategories['categories'].append(inactiveDict)

with open(os.path.join('output', 'teamCategories.json'), 'w') as flairfile:
    json.dump(teamCategories, flairfile, indent=4)