import requests, csv

"""
This is a small script created to perform bulk restores of deleted files from Dropbox.
You will need to provide the full file path in Dropbox format. Example: '/MyFolder/myfile.txt'

Helpful resources:
https://www.dropbox.com/developers/documentation/http/overview
"""

# API token from https://www.dropbox.com/developers/apps (I'm using a Dropbox Business API with Team member file access)
token = 'Your Key'

# This needs to be the dbmid of someone who has access to the folder
dbmid = 'dbmid:yourid'

# Get the revision id of the file. This is needed to restore the file
def get_rev_id(full_path):

    headers = {
        'Authorization': 'Bearer {}'.format(token),
        'Content-Type': 'application/json',
        'Dropbox-API-Select-User': dbmid
    }

    data = '{"path": "' + full_path + '","mode": "path","limit": 10}'

    response = requests.post('https://api.dropboxapi.com/2/files/list_revisions', headers=headers, data=data)
    json = response.json()
    return json['entries']

# Restore the actual file
def restore_file(full_path):

    content = get_rev_id(full_path)
    for item in content:
        rev = item['rev']

    headers = {
        'Authorization': 'Bearer {}'.format(token),
        'Content-Type': 'application/json',
        'Dropbox-API-Select-User': dbmid
    }

    data = '{"path": "' + full_path + '","rev": "' + rev +'"}'

    response = requests.post('https://api.dropboxapi.com/2/files/restore', headers=headers, data=data)
    return response

# Gets file attributes etc..
def check_file_metadata(full_path):

    headers = {
        'Authorization': 'Bearer {}'.format(token),
        'Content-Type': 'application/json',
        'Dropbox-API-Select-User': dbmid
    }

    data = '{"path": "' + full_path + '","include_media_info": false,"include_deleted": true,"include_has_explicit_shared_members": false}'

    response = requests.post('https://api.dropboxapi.com/2/files/get_metadata', headers=headers, data=data)
    json = response.json()
    return json

# Iterates through a CSV file and prints out the paths that have been flagged as deleted.  Make sure to edit the delimiter if needed.
def mass_file_checker_csv(csv_path):

    with open(csv_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file,delimiter='|')
        next(csv_reader)  # Skip first row (Headers)
        content = csv_reader

        for line in content:
            full_path = str(line[0])
            #print(full_path)
            data = check_file_metadata(full_path)

            try:
                is_deleted = data['.tag']
            except KeyError:
                is_deleted = 'not deleted'
                pass

            if is_deleted == 'deleted':
                print('{} was deleted and needs to be restored.'.format(full_path))

# Iterates through a CSV file and restores each file. Make sure to edit the delimiter if needed.
def mass_file_restore_csv(csv_path):

    with open(csv_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file,delimiter='|')
        next(csv_reader)  # Skip first row (Headers)
        content = csv_reader

        for line in content:
            full_path = str(line[0])
            #print(full_path)
            restore_file(full_path)
