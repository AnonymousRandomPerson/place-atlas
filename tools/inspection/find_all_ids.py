import json
import os

all_ids = os.path.join('.', 'all_ids.txt')
atlas_all = os.path.join('.', 'atlas_all.json')
atlas = os.path.join('..', '..', 'web', 'atlas.json')
read_ids = os.path.join('..', '..', 'data', 'read-ids.txt')
missed_ids = os.path.join('.', 'missed-ids.txt')

ids = set()

for atlas_path in [atlas_all, atlas]:
  with open(atlas_path, 'r+', encoding='UTF-8') as file:
    line = file.readline()
    while line:
      if not line.startswith('[') and not line.startswith(']'):
        line = line[:-1]
        if line.endswith(','):
          line = line[:-1]

        try:
          entry = json.loads(line)
          ids.add(entry['id'])

        except:
          pass

      line = file.readline()

with open(read_ids, 'r+', encoding='UTF-8') as read_file:
  for line in read_file.readlines():
    ids.add(line[:-1])

with open(missed_ids, 'r+', encoding='UTF-8') as missed_file:
  for line in missed_file.readlines():
    ids.add(line[:-1])

with open(all_ids, 'w', encoding='UTF-8') as all_file:
  for id in sorted(ids):
    all_file.write(id + '\n')
