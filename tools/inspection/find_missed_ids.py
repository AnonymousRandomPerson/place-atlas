import json
import os

path = os.path.join('.', 'atlas_all.json')
read_ids = os.path.join('..', '..', 'data', 'read-ids.txt')
missed_ids = os.path.join('.', 'missed-ids.txt')

ids = set()

with open(path, 'r+', encoding='UTF-8') as file:
  line = file.readline()
  while line:
    line = line[:-1]
    if line.endswith(','):
      line = line[:-1]

    try:
      entry = json.loads(line)
      ids.add(entry['id'])

    except:
      pass

    line = file.readline()


with open(missed_ids, 'w', encoding='UTF-8') as missed_file:
  with open(read_ids, 'r+', encoding='UTF-8') as read_file:
    line = read_file.readline()
    while line:
      line = line[:-1]
      if line not in ids:
        print(line)
        missed_file.write(line + '\n')
      line = read_file.readline()
