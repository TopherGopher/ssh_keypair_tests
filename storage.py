#!/usr/local/bin/python
import yaml
import googleapiclient
from googleapiclient.discovery import build
from sys import exit
from os import environ
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from logger import logger
from config import config

gauth = GoogleAuth()
# Try to load saved client credentials
gauth.LoadCredentialsFile("creds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.CommandLineAuth()
    # TODO: Send email with URL needed to visit
    # Then come up with method for sending it back...endpoint? text? :-)
    # auth_url = gauth.GetAuthUrl() # Create authentication url user needs to visit
    # code = AskUserToVisitLinkAndGiveCode(auth_url) # Your customized authentication flow
    # gauth.Auth(code) # Authorize and build service from the c
elif gauth.access_token_expired:
    try:
        # Refresh them if expired
        gauth.Refresh()
    except pydrive.auth.RefreshError as e:
        logger.error(e)
        exit()
else:
    # Initialize the saved creds
    gauth.Authorize()

# TODO: Change to JSON
# Save the current credentials to a file
gauth.SaveCredentialsFile("creds.txt")

drive = GoogleDrive(gauth)
# print(dir(drive.ListFile()))


def get_file_id(fname):
    """
    Similar to list file, but this one returns IDs and None!
    Naive assumption to return first, I know, but screw it.
    """
    files = drive.ListFile({
        'q': "'root' in parents and trashed=false" +
             " and title='{0}'".format(fname),
        'maxResults': 1
    }).GetList()
    if len(files) == 0 or len(files) > 1:
        return None
    else:
        return files[0]['id']


def file_exists(fname):
    """
    Returns:
        bool: True if file exists
    """
    files = drive.ListFile({
        'q': "'root' in parents and trashed=false" +
             " and title='{0}'".format(fname),
        'maxResults': 1
    }).GetList()
    if len(files) == 0:
        return False
    else:
        return True


def create_file(fname, body, folder_name=None):
    """
    Returns:
        None or str: None when a file was not created
                     if creation success, file ID is returned
    """
    if not isinstance(fname, str) or not isinstance(body, str):
        raise Exception("Both params must be strings")

    if file_exists(fname):
        logger.error("File {0} exists".format(fname))
        return None

    file_props = {
        'title': fname
    }

    if folder_name is not None:
        folder_id = get_file_id(folder_name)
        assert folder_id is not None
        file_props['parents'] = [{'id': folder_id}]

    file = drive.CreateFile(file_props)
    file.SetContentString(body)
    file.Upload()
    assert 'id' in file
    return file['id']


def create_folder(fname):
    folder = drive.CreateFile({
        'title': fname,
        'mimeType': 'application/vnd.google-apps.folder'})
    folder.Upload()
    return folder

# Download file
# file3 = drive.CreateFile({'id': file2['id']})
# print('Downloading file %s from Google Drive' % file3['title']) # 'hello.png'
# file3.GetContentFile('world.png')  # Save Drive file as a local file
# GetContentString also works

if __name__ == '__main__':
    # TODO - don't use folder id, instead retrieve it
    create_file(fname="hello_world.txt",
                folder_name=config['folder_name'],
                body="Hi, hey, how are ya?")
