# [r/CompetitiveOverwatch](https://reddit.com/r/competitiveoverwatch) Flair Spritesheet Generator

## Running
1. `pip3 install -r requirements.txt`
2. Start script with `python3 flairSheets.py <spritesheet>`
3. Output in output folder: `flair-<spritesheet>.png`, `flair-<spritesheet>-2x.png`, `flair-<spritesheet>.json` 

## Create new Spritesheet
1. Create new folder with the same name as the spritesheet
2. Add flair images
3. Create `flairlist.json` in that folder containing a list of dictionaries with flair-ID `id` (same as image filename!) and full name `name` entries.

## Add new flair to existing Spritesheet
1. Add image to spritesheet folder
2. Append entry to `flairlist.json` in that folder with flair-ID `id` (same as image filename!) and full name `name`.
