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

The first thing you will need to do is generate your API key. There are basically several methods to do this, one is to generate a personal key and the latter is to generate a buisness key. It just depends on what your end goal is. I will be using the buisness key.

```python
import requests

# API token from https://www.dropbox.com/developers/apps (I'm using a Dropbox Business API with Team member file access)
token = 'Your Key'

```
The Dropbox REST API documentation examples are in curl. We can use the very helpful [site](https://curl.trillworks.com/) to convert these examples in to Python requests.
