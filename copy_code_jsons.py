import os
import json
import shutil

PROCESSED_DIR = 'processed code'
STORIES_DIR = 'stories'

txt_files = [f for f in os.listdir(PROCESSED_DIR) if f.endswith('.txt')]
story_folders = [f for f in os.listdir(STORIES_DIR) if os.path.isdir(os.path.join(STORIES_DIR, f))]
folder_got_code = {folder: False for folder in story_folders}
copied_count = 0
error_files = []

def try_open_json(path):
    # Try utf-8, then cp1252
    for enc in ['utf-8-sig', 'cp1252']:
        try:
            with open(path, 'r', encoding=enc) as f:
                return json.load(f)
        except UnicodeDecodeError:
            continue
        except json.JSONDecodeError:
            return None
    return None

for txt_file in txt_files:
    txt_path = os.path.join(PROCESSED_DIR, txt_file)
    data = try_open_json(txt_path)
    if data is None:
        error_files.append(txt_file)
        continue
    title = data.get('Title')
    if not title and 'The Complete Story' in data:
        title = data['The Complete Story'].get('Title')
    if not title:
        error_files.append(txt_file)
        continue
    folder_name = title.replace(' ', '_')
    dest_folder = os.path.join(STORIES_DIR, folder_name)
    if os.path.isdir(dest_folder):
        dest_file = os.path.join(dest_folder, f'{title}.code.json')
        shutil.copyfile(txt_path, dest_file)
        folder_got_code[folder_name] = True
        copied_count += 1

missed_folders = [f for f, got in folder_got_code.items() if not got]

print(f'Copied {copied_count} files.')
print(f'{len(missed_folders)} story folders did not get a .code.json file:')
for folder in missed_folders:
    print(f'- {folder}')
if error_files:
    print(f'\nFiles with errors ({len(error_files)}):')
    for ef in error_files:
        print(f'- {ef}')
