# Dropbox-PyTools
Helpful functions that leverage the Dropbox API v2 (HTTP endpoints). The main goal of this project was 
to download all users Dropbox data via the API. However, I've added tools for performing bulk restores
of deleted files. I will continue to add other functionality as needed.

  Get all Dropbox users  
  List all the contents of a users account with paignation (If needed)  
  Check if a list of files have been deleted  
  Download all the content from a users account  
  Download all the content for every user account (From function or CSV)  
  Restore all files specified in a CSV  
  
  Functions return JSON  
  
  Any tips or advice are much appreciated.  

## How to get started with Python and the Dropbox REST API

The first thing you will need to do is generate your [API key](https://www.dropbox.com/developers/apps). There are basically several methods to do this, one is to generate a personal key and the latter is to generate a buisness key. It just depends on what your end goal is. I will be using the buisness key.

The Dropbox REST API [documentation](https://www.dropbox.com/developers/documentation/http/teams) examples are in curl. We can use this very helpful [site](https://curl.trillworks.com/) to convert these examples in to Python requests.

Lets look at the below function which gets 1000 users and does not include removed users.

```python
import requests

# API token from https://www.dropbox.com/developers/apps
# (I'm using a Dropbox Business API with Team member file access)
token = 'Your Key'

# Endpoint documentation https://www.dropbox.com/developers/documentation/http/teams#team-members-list

def get_all_users():
    headers = {
        'Authorization': 'Bearer {}'.format(token),
        'Content-Type': 'application/json',
    }

    data = '{"limit": 1000,"include_removed": false}'

    response = requests.post('https://api.dropboxapi.com/2/team/members/list', headers=headers, data=data)
    json = response.json()
    return json['members']

get_all_users() # Run the above function
```

This function returns a dictonary of members which we then can iterate over to expose other details.
Keep in mind that if you have more users than the current set limit "1000", you will need to paginate.

```python
users = get_all_users()

for user in users:
  print(user['dbmid'])
```

Here is an example in which pagination was needed. You will need to pass the dbmid in order for this function to work.
The json['cursor'] value lets us know if we need to keep calling the list_folder/continue endpoint to get more data.

```python
import requests

# API token from https://www.dropbox.com/developers/apps
# (I'm using a Dropbox Business API with Team member file access)
token = 'Your Key'

def get_user_files(dbmid):
    alluserfiles = []	
	
    headers = {
        'Authorization': 'Bearer {}'.format(token),
        'Content-Type': 'application/json; charset=utf-8',
        'Dropbox-API-Select-User': dbmid
    }

    data = '{"path": "","recursive": true,"include_media_info": false,"include_deleted": false,"include_has_explicit_shared_members": false,"include_mounted_folders": true}'

    response = requests.post('https://api.dropboxapi.com/2/files/list_folder', headers=headers, data=data)
    json = response.json()

    for i in json['entries']:
        alluserfiles.append(i)
    
    while json['has_more']:

                cursorline = json['cursor']
                cursor = '{"cursor": "' + cursorline + '"}'
                data = '{}'.format(cursor)

                headers = {
                    'Authorization': 'Bearer {}'.format(token),
                    'Content-Type': 'application/json; charset=utf-8',
                    'Dropbox-API-Select-User': dbmid
                }
            
                response = requests.post('https://api.dropboxapi.com/2/files/list_folder/continue', headers=headers, data=data)
                
                if response.status_code == requests.codes.ok: # Keep trying to process the results of the response variable
                # until we are successfull
                    print('Status was okay. {}'.format(response.status_code))
                    
                    json = response.json()
                    for i in json['entries']:
                        alluserfiles.append(i)
    return(alluserfiles)

user_files = get_user_files(dbmid)
```