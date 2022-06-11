"""
Auth setup
1. Head to https://www.reddit.com/prefs/apps
2. Click "create another app"
3. Give it a name and description
4. Select "script"
5. Redirect to http://localhost:8080
6. Create file "credentials" with the format below
┌─────────────────────────────────────────────────────┐
│ [ID]        <-  Under "personal use script"         │
│ [Secret]                                            │
│ [Username]  <-  Must be a mod, don't do this if you │
│ [Password]  <-  don't know what you are doing.      │
└─────────────────────────────────────────────────────┘
7. Run Script

Running Script
1. Input the next ID to use
2. Manually resolve errors in manual_atlas.json
3   a. Use merge_out.py, or...
		b.  a. Copy temp_atlas.json entries into web/_js/atlas.js (mind the edits!)
				b. Copy read-ids-temp.txt IDs into data/read-ids.txt
5. Create a pull request
"""

import os
import praw
from psaw import PushshiftAPI
import json
import time
import re
from formatter import format_all, validate
from migrate_atlas_format import migrate_atlas_format

with open('temp_atlas.json', 'w', encoding='utf-8') as OUT_FILE, open('read-ids-temp.txt', 'w') as READ_IDS_FILE, open('manual_atlas.txt', 'w', encoding='utf-8') as FAIL_FILE:
	OUT_FILE_LINES = ['[\n']

	with open('credentials', 'r') as file:
		credentials = file.readlines()
		client_id = credentials[0].strip()
		client_secret = credentials[1].strip()
		username = credentials[2].strip() if len(credentials) > 3 else ""
		password = credentials[3].strip() if len(credentials) > 3 else ""

	reddit = praw.Reddit(
		client_id=client_id,
		client_secret=client_secret,
		username=username,
		password=password,
		user_agent='atlas_bot'
	)
	psawApi = PushshiftAPI(reddit)

	has_write_access = not reddit.read_only
	if not has_write_access:
		print("Warning: No write access. Post flairs will not be updated.")
		time.sleep(5)

	existing_ids = []
	atlas_all_entries = {}
	atlas_entries = {}

	with open(os.path.join('inspection', 'all_ids.txt'), 'r') as edit_ids_file:
		for id in [x.strip() for x in edit_ids_file.readlines()]:
			existing_ids.append(id)

	with open(os.path.join('inspection', 'atlas_all.json'), 'r+', encoding='UTF-8') as file:
		line = file.readline()
		while line:
			if not line.startswith('[') and not line.startswith(']'):
				line = line[:-1]
				if line.endswith(','):
					line = line[:-1]

				try:
					entry = json.loads(line)
					atlas_all_entries[entry['id']] = line

				except:
					pass

			line = file.readline()

	with open(os.path.join('..', 'web', 'atlas.json'), 'r+', encoding='UTF-8') as file:
		line = file.readline()
		while line:
			if not line.startswith('[') and not line.startswith(']'):
				line = line[:-1]
				if line.endswith(','):
					line = line[:-1]

				try:
					entry = json.loads(line)
					atlas_entries[entry['id']] = line

				except:
					pass

			line = file.readline()

	def set_flair(submission, flair):
		if has_write_access and submission.link_flair_text != flair:
			flair_choices = submission.flair.choices()
			flair = next(x for x in flair_choices if x["flair_text_editable"] and flair == x["flair_text"])
			submission.flair.select(flair["flair_template_id"])

	total_all_flairs = 0
	duplicate_count = 0
	failcount = 0
	successcount = 0
	totalcount = 0

	#for submission in psawApi.search_submissions(subreddit='placeAtlas2', limit=50000):
	#for submission in reddit.subreddit('placeAtlas2').search('flair:"New Entry"', syntax='lucene', limit=30000):
	for id in existing_ids:
		if id in atlas_all_entries:
			OUT_FILE_LINES.append(atlas_all_entries[id] + ',\n')
			continue
		try:
			submission = reddit.submission(id)

			if submission.link_flair_text == 'Rejected Entry':
				continue

			text = submission.selftext

			text = text.replace('\u200c', '')
			text = re.compile(r"(\{.+\})", re.DOTALL).search(text).group(0)
			# Test if it needs to escape the escape character. Usually happens on fancy mode.
			try: json.loads(text)
			except json.JSONDecodeError: text = re.sub(r"\\(.)", r"\1", text)
			print('Reading', id)
		except Exception as e:
			if e is KeyboardInterrupt:
				break
			if id in atlas_entries:
				OUT_FILE_LINES.append(atlas_entries[id] + ',\n')
			continue
		total_all_flairs += 1

		try:

			submission_json = json.loads(text)

			if submission_json:

				if submission_json["id"] != 0:

					#assert submission_json["id"] != 0, "Edit invalid because ID is tampered, it must not be 0!"

					submission_json_dummy = {"id": submission_json["id"], "edit": submission.id}

				else:

					#assert submission_json["id"] == 0, "Edit invalid because ID is tampered, it must be 0!"

					submission_json_dummy = {"id": submission.id}

				for key in submission_json:
					if not key in submission_json_dummy:
						submission_json_dummy[key] = submission_json[key];
				if 'links' not in submission_json_dummy:
					submission_json_dummy = migrate_atlas_format(submission_json_dummy)
				submission_json = format_all(submission_json_dummy, True)
				validation_status = validate(submission_json)

				assert validation_status < 3, \
					"Submission invalid after validation. This may be caused by not enough points on the path."

				OUT_FILE_LINES.append(json.dumps(submission_json, ensure_ascii=False) + ',\n')
				#READ_IDS_FILE.write(submission.id + '\n')
				successcount += 1

		except Exception as e:
			if e is KeyboardInterrupt:
				break
			failcount += 1

		totalcount += 1
		# if totalcount > 10:
		# 	break

	OUT_FILE_LINES.append(']\n')
	OUT_FILE.writelines(OUT_FILE_LINES)

print(f"\n\nTotal all flairs: {total_all_flairs}\nSuccess: {successcount}/{totalcount}\nFail: {failcount}/{totalcount}\nPlease check manual_atlas.txt for failed entries to manually resolve.")
