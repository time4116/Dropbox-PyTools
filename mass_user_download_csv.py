import requests, os, logging, csv, shutil

# Make sure to set the below vars before running the script!!
# See line 36 & 57 (download_user_files()) to specify any top level folders to exclude, or just comment it out.

# Helpful resources:
# https://www.dropbox.com/developers/documentation/http/overview
# https://www.dropboxforum.com/t5/Developer-Community-API-Support/ct-p/101000041

root = 'C:\\'
domain = '@YourCompany.com'  # Removes the domain from the email address (Used to create the folder)
logName = 'dropbox_download.log'
logFile = root + logName

# API token from https://www.dropbox.com/developers/apps (I'm using a Dropbox Business API with Team member file access)
token = 'Your Key'

# Logging stuff
logging.basicConfig(filename=logFile, level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Retrieves all files for the user except for any exclusions. See line 36 & 57.
def get_user_files(dbmid):
    alluserfiles = []	
	
    headers = {
        'Authorization': 'Bearer {}'.format(token),
        'Content-Type': 'application/json; charset=utf-8',  # Changed this char set
        'Dropbox-API-Select-User': dbmid
    }

    data = '{"path": "","recursive": true,"include_media_info": false,"include_deleted": false,"include_has_explicit_shared_members": false,"include_mounted_folders": true}'

    response = requests.post('https://api.dropboxapi.com/2/files/list_folder', headers=headers, data=data)
    json = response.json()
    for i in json['entries']:
	# Do not do this >> if '/_Teams1' not in i['path_display'] or '/_Teams2' not in i['path_display']
	# Instead create another elsif statement...
        if '/_Teams1' not in i['path_display']:
            alluserfiles.append(i)
    
    while json['has_more']:

                cursorline = json['cursor']
                cursor = '{"cursor": "' + cursorline + '"}'
                data = '{}'.format(cursor)

                headers = {
                    'Authorization': 'Bearer {}'.format(token),
                    'Content-Type': 'application/json; charset=utf-8',  # Changed this char set
                    'Dropbox-API-Select-User': dbmid
                }
            
                response = requests.post('https://api.dropboxapi.com/2/files/list_folder/continue', headers=headers, data=data)
                
                if response.status_code == requests.codes.ok:
                    print('Status was okay. {}'.format(response.status_code))
                    json = response.json()
                    for i in json['entries']:
			# See line 39
                        if '/_Teams1' not in i['path_display']:
                            alluserfiles.append(i)

                else:
                    pass
                    #print('Text in error. {}'.format(response.text))
                    #print('Status code from (else)... {}'.format(response.status_code))

    return alluserfiles

# Downloads all of the contents of a users Dropbox account and retains the folder hierarchy (Except if the full path exceeds 255 characters. Windows limitation)
# Chunk size allows for better performance when downloading large files.
def download_user_files(dbmid, username, root):
    data = get_user_files(dbmid)
    do_not_dl = []

    for content in data:

        filename = content['name']
        tag = content['.tag']
        fullpath = content['path_display']
        f_root = fullpath.split('/')
        f_root = '/' + f_root[1]

        owner = True

        try:
            shared_id = content['shared_folder_id']
        except KeyError:
            shared_id = False
            pass

        if shared_id:
            try:

                headers = {
                    'Authorization': 'Bearer {}'.format(token),
                    'Content-Type': 'application/json',
                    'Dropbox-API-Select-User': dbmid
                }

                data = '{"shared_folder_id": "' + shared_id + '","actions": []}'

                response = requests.post('https://api.dropboxapi.com/2/sharing/get_folder_metadata', headers=headers,
                                         data=data)
                json_metadata = response.json()
                if 'owner' not in json_metadata['access_type']['.tag']:

                    owner = False
                    do_not_dl.append(fullpath)
                    #print('Not the owner of this shared folder, skipping: {}'.format(fullpath))
                    
                    dest = root + username + fullpath
                    dest = dest.replace("/", "\\")

                    if os.path.isdir(dest) == True:

                        try:
			    print('Removing as the user is not the owner of this shared folder: {}'.format(dest.encode("utf-8")))
                            shutil.rmtree(dest)                            
                            logging.debug("{} Removing as the user is not the owner of this shared folder.".format(dest.encode("utf-8")))

                        except Exception as e:
                            print('Could not delete {}'.format(dest.encode("utf-8")))
                            logging.debug("{} Could not download! {}".format(dest.encode("utf-8"),e.encode("utf-8"))
            except:
                pass
        #print('current blacklist: {}'.format(do_not_dl))
        if "folder" in tag or not owner:
            pass
            # Folders are just pointers and can not actually be downloaded. Do not download any shares of which the target
			# User is not the owner.

        elif f_root in do_not_dl:
            pass
            # Exclude all items specified in the do_not_dl list.

        else:
            size = content['size']            
            orgpath = content['id']
            dest = root + username + fullpath
            dest = dest.replace("/", "\\")

            # Renames invalid character ':' or '**' to '-'. Place exceptions in this if statement.
            # Certain characters are not permitted depending on the operating system.
            dirsplit = dest.split('\\')
            dirlen = len(dirsplit)
            for i in range(1, dirlen):  # Set to 1 to skip the ':' in the root path C:\\ etc...
                if ':' in dirsplit[i]:
                    badchar = dirsplit[i].replace(':', '-')
                    dest = dest.replace(dirsplit[i], badchar)

                    dest = dest + '\\' + filename
                    logging.debug("____ {} File name had a bad char in it and was renamed. '-'".format(dest.encode("utf-8")))
				
		elif '*' in dirsplit[i]:
                    badchar = dirsplit[i].replace('*', '-')
                    dest = dest.replace(dirsplit[i], badchar)

                    dest = dest+'\\'+filename
                    logging.debug("____ {} File name had a bad char in it and was renamed. '-'".format(dest.encode("utf-8")))

                else:
                    pass

            if len(dest) >= 255:
                dest = root + username + '\\255\\' + filename
                logging.debug("____ {} Exceeded Windows 255 char limit and was renamed a moved to 255 folder".format(dest.encode("utf-8")))
                # Write to log file the orginal dropbox path of this folder as it may exceed the windows 255 char limit
            else:
                pass

            dir = os.path.dirname(dest)

            if os.path.isdir(dir) == False:
                os.makedirs(dir)
            else:
                pass
                # print("{} already exists!".format(dir))

            if size >= 524288000 and os.path.isfile(dest) != True:

                logging.debug("DropBox: {} (Large File) Downloading...".format(fullpath.encode("utf-8")))
                DropboxAPIArg = '{"path": "' + orgpath + '"}'

                headers = {
                    'Authorization': 'Bearer {}'.format(token),
                    'Dropbox-API-Arg': '{}'.format(DropboxAPIArg),
                    'Dropbox-API-Select-User': dbmid
                }

                response = requests.post('https://content.dropboxapi.com/2/files/download', headers=headers,
                                         stream=True)

                try:
                    handle = open(dest, "wb")
                    for chunk in response.iter_content(chunk_size=10485760):  # 10485760 (10 MB)
                        if chunk:  # filter out keep-alive new chunks
                            handle.write(chunk)

                    logging.debug("{} File successfully downloaded.".format(dest.encode("utf-8")))

                except WindowsError:

                    logging.debug("{} Could not download!".format(dest.encode("utf-8")))

            elif os.path.isfile(dest) != True:

                logging.debug("DropBox: {} Downloading...".format(fullpath.encode("utf-8")))
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

                    logging.debug("{} File successfully downloaded.".format(dest.encode("utf-8")))

                except WindowsError:

                    logging.debug("{} Could not download!".format(dest.encode("utf-8")))

            else:

                logging.debug("{} File has already been downloaded...".format(dest.encode("utf-8")))

# Performs the download function for each user in a CSV. Adjust the headers according to your CSV file.
def mass_user_download_csv(csv_path):
    global root
    global domain

    with open(csv_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip first row (Headers)
        content = csv_reader

        for line in content:

            # Make sure to adjust if needed!!
            status = str(line[4])  # Status header is in postion 4 of my CSV
            dbmid = line[0]  # dbmid header is in postion 0 of my CSV
            email = line[2]  # email header is in postion 2 of my CSV
            username = email.replace(domain, '')

            # logging.debug("Starting download function for the following status: {}".format(status))
            if 'active' in status:
                print("Starting on download on: {}".format(username))
                logging.debug("Starting download function for the following dbmid: {}".format(dbmid))
                logging.debug("Starting download function for the following user: {}".format(username))
                download_user_files(dbmid, username, root)
                print("Download complete for: {}".format(username))

    print("All Done!")
    logging.debug("Script has completed. (See log for errors)")
