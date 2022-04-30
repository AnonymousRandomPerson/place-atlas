import json
import os

path = os.path.join('.', 'atlas_all.json')

single_point = True
target_point = (50, 50)
target_point_min = (1, 1)
target_point_max = (50, 50)

if single_point:
  target_point_min = target_point
  target_point_max = target_point

found_points = []
with open(path, 'r+', encoding='UTF-8') as file:
  line = file.readline()
  while line:
    line = line[:-1]
    if line.endswith(','):
      line = line[:-1]

    try:
      entry = json.loads(line)
      min_point = (float('inf'), float('inf'))
      max_point = (0, 0)
      for point in entry['path']:
        point = [int(p) for p in point]
        min_point = (min(point[0], min_point[0]), min(point[1], min_point[1]))
        max_point = (max(point[0], max_point[0]), max(point[1], max_point[1]))
        
      size = (max_point[0] - min_point[0]) * (max_point[1] - min_point[1])

      if target_point_max[0] >= min_point[0] and target_point_max[1] >= min_point[1] and target_point_min[0] <= max_point[0] and target_point_min[1] <= max_point[1]:
        center = [int(p) for p in entry['center']]
        print_string = 'ID: %s | Name: %s | Description: %s | Center: %s | Size: %s | Min: %s | Max: %s' % (entry['id'], entry['name'], entry['description'], center, size, min_point, max_point)
        found_points.append((size, print_string))

    except:
      pass

    line = file.readline()
    
for found_point in sorted(found_points, key=lambda point: point[0]):
  print(found_point[1])