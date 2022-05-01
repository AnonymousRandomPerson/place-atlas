import json
import os

path = os.path.join('.', 'atlas_all.json')

ids = set()

with open(path, 'r+', encoding='UTF-8') as file:
  line = file.readline()
  while line:
    line = line[:-1]
    if line.endswith(','):
      line = line[:-1]

    try:
      entry = json.loads(line)
      id = entry['id']
      if id in ids:
        print(id)
      else:
        ids.add(id)

    except:
      pass

    line = file.readline()
