import requests, os, logging

# Make sure to set the below vars before running the script!! Also make sure to set limit in getAllUSers() the max and default is 1000.
# See line 94 (downloadUserFolder()) to specify any top level folders to exclude, or just comment it out.

# Helpful resources:
# https://www.dropbox.com/developers/documentation/http/overview
# https://www.dropboxforum.com/t5/Developer-Community-API-Support/ct-p/101000041

root = 'E:\\'
domain = '@yourcompany.com' # Removes the domain from the email address (Used to create the folder)
logName = 'dropbox_download.log'
logFile = root + logName

# API token from https://www.dropbox.com/developers/apps (I'm using a Dropbox Business API with Team member file access)
token = 'Your Key'

# Logging stuff
logging.basicConfig(filename=logFile, level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Returns a dictionary of user attributes
def getAllUsers():
    headers = {
        'Authorization': 'Bearer {}'.format(token),
        'Content-Type': 'application/json',
    }

    data = '{"limit": 1000,"include_removed": false}'

    response = requests.post('https://api.dropboxapi.com/2/team/members/list', headers=headers, data=data)
    json = response.json()
    return json['members']

# Lists the contents of a users folders. If the result's listFolderResult.has_more field is true, call list_folder/continue (or listUserFolderContinue) with the returned ListFolderResult.cursor to retrieve more entries.
def listUserFolder(dbmid):
    global allFiles

    headers = {
        'Authorization': 'Bearer {}'.format(token),
        'Content-Type': 'application/json; charset=utf-8', #Changed this char set
        'Dropbox-API-Select-User': dbmid
    }

    data = '{"path": "","recursive": true,"include_media_info": false,"include_deleted": false,"include_has_explicit_shared_members": false,"include_mounted_folders": true}'

    response = requests.post('https://api.dropboxapi.com/2/files/list_folder', headers=headers, data=data)
    json = response.json()
    allFiles += json['entries']
    return json

# Paginate and return a complete list of file\folder contents for a users folder.
def listUserFolderContinue(dbmid):
    global allFiles

    json = listUserFolder(dbmid)

    while json['has_more'] == True:

        cursorline = json['cursor']
        cursor = '{"cursor": "' + cursorline + '"}'
        data = '{}'.format(cursor)

        headers = {
            'Authorization': 'Bearer {}'.format(token),
            'Content-Type': 'application/json; charset=utf-8', #Changed this char set
            'Dropbox-API-Select-User': dbmid
        }

        response = requests.post('https://api.dropboxapi.com/2/files/list_folder/continue', headers=headers, data=data)
        json = response.json()
        allFiles += json['entries']
        return allFiles

# Downloads all of the contents of a users folder and retains the folder hierarchy (Except if the full path exceeds 255 characters. Windows limitation)
# Teams folders are also excluded from this function. Chunk size allows for better performance when downloading large files.
def downloadUserFolder(dbmid, username, root):
    global allFiles

    allFiles = []

    data = listUserFolderContinue(dbmid)

    for content in data:

        filename = content['name']
        tag = content['.tag']
        fpath = content['path_display']

        if "folder" in tag:
            pass
            # Folders are just pointers and can not actually be downloaded. The full path is needed.

        # elif '/_Teams1' in fpath or '/_Teams2' in fpath or '/_Teams3' in fpath:
            # pass
            # # Exclude all teams folders from being downloaded.

        else:
            size = content['size']
            fullpath = content['path_display']
            orgpath = content['id']
            dest = root + username + fullpath
            dest = dest.replace("/","\\")

            if len(dest) >= 255:
                dest = root+username+'\\255\\'+filename
                logging.debug("____ {} Exceeded Windows 255 char limit and was renamed a moved to 255 folder".format(dest))
                # Write to log file the orginal dropbox path of this folder as it may exceed the windows 255 char limit
            else:
                pass

            dir = os.path.dirname(dest)

            if os.path.isdir(dir) == False:
                os.makedirs(dir)
            else:
                pass
                #print("{} already exists!".format(dir))

            if size >= 524288000 and os.path.isfile(dest) != True:

                logging.debug("DropBox: {} (Large File) Downloading...".format(fullpath))
                DropboxAPIArg = '{"path": "'+orgpath+'"}'

                headers = {
                    'Authorization': 'Bearer {}'.format(token),
                    'Dropbox-API-Arg': '{}'.format(DropboxAPIArg),
                    'Dropbox-API-Select-User': dbmid
                }

                response = requests.post('https://content.dropboxapi.com/2/files/download', headers=headers, stream=True)

                try:
                    handle = open(dest, "wb")
                    for chunk in response.iter_content(chunk_size=10485760): # changed from 512 to 10485760 (10 MB)
                        if chunk:  # filter out keep-alive new chunks
                            handle.write(chunk)

                    logging.debug("{} File successfully downloaded.".format(dest))

                except WindowsError:

                    logging.debug("{} Could not download!".format(dest))

            elif os.path.isfile(dest) != True:

                logging.debug("DropBox: {} Downloading...".format(fullpath))
                DropboxAPIArg = '{"path": "' + orgpath + '"}'

                headers = {
                    'Authorization': 'Bearer {}'.format(token),
                    'Dropbox-API-Arg': '{}'.format(DropboxAPIArg),
                    'Dropbox-API-Select-User': dbmid
                }

                response = requests.post('https://content.dropboxapi.com/2/files/download', headers=headers)
                try:

                    with open(dest, 'wb') as f:
                        f.write(response.content)

                    logging.debug("{} File successfully downloaded.".format(dest))

                except WindowsError:

                    logging.debug("{} Could not download!".format(dest))

            else:

                logging.debug("{} File has already been downloaded...".format(dest))

# Performs the download function for each user returned via getAllUsers(). Remember to set the limit value in that function
# as it can be set to a max of 1000 (Which is the default) if there are ever more users than that
# a new function similar to listFolderContinue() will need to be created to paginate the results of getAllUsers().
def MassUserCopy():
    global root
	global domain

    content = getAllUsers()
    for user in content:

        status = str(user['profile']['status'])
        dbmid = user['profile']['team_member_id']
        email = user['profile']['email']
        username = email.replace(domain,'')

        #logging.debug("Starting download function for the following status: {}".format(status))
        if 'active' in status:
                logging.debug("Starting download function for the following dbmid: {}".format(dbmid))
                logging.debug("Starting download function for the following user: {}".format(username))
                downloadUserFolder(dbmid, username, root)

    logging.debug("Script has completed. (See log for errors)")