import requests

# API token from https://www.dropbox.com/developers/apps (I'm using a Dropbox Business API with Team member file access)
token = 'Your Key'

# Returns a list of user attributes. If you have more users than 1000 you will need to paiginate, see mass_user_download_csv.py script for ideas on that process.
def get_all_users():
    headers = {
        'Authorization': 'Bearer {}'.format(token),
        'Content-Type': 'application/json',
    }

    data = '{"limit": 1000,"include_removed": false}'

    response = requests.post('https://api.dropboxapi.com/2/team/members/list', headers=headers, data=data)
    json = response.json()
    return json['members']
