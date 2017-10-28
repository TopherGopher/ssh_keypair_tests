#!/usr/local/bin/python
"""
storage.py
Because for some friggin' reason, the 'friendly' wrapper around
python-google-api-client needed another wrapper to make it consumable.
And it's not just inherently threadsafe, even though it supports it?
Look at that garbage in the constructor where I have to actually go into
the auth object and suck out the raw http object and pass that so that
you don't attempt to re-authenticate in every. single. thread?
I called the main class storeIt but I really wanted to call it <-REDACTED->
"""

from config import config
from logging import DEBUG
from logging import Formatter
from logging import StreamHandler
from logging import getLogger
from pydrive.auth import GoogleAuth
from pydrive.auth import RefreshError
from pydrive.drive import GoogleDrive
from pydrive.files import ApiRequestError
from random import randrange
from sys import stdout
from sys import exit
from time import sleep


class StoreIt():
    def __init__(self, retries=20, sleep_time_between_retries=10):
        self.drive = self.auth_drive()
        # Create httplib.Http() object.
        # Thread safe love :-)
        self.http = self.drive.auth.Get_Http_Object()
        self.retries = retries
        self.sleep_time = sleep_time_between_retries
        self.init_logger()

    def get_folder_id(self, folder_name):
        """
        A wrapper around get_file_id... 'cause.
        """
        return self.get_file_id(folder_name)

    def init_logger(self):
        self.logger = getLogger(__name__)
        FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() PID %(process)d] %(message)s"
        self.logger.setLevel(DEBUG)
        ch = StreamHandler(stdout)
        ch.setLevel(DEBUG)
        ch.setFormatter(Formatter(FORMAT))
        self.logger.addHandler(ch)

    def auth_drive(self):
        """
        Returns GoogleDrive object
        """
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
            except RefreshError as e:
                self.logger.error(e)
                exit()
        else:
            # Initialize the saved creds
            gauth.Authorize()

        # TODO: Change to JSON
        # Save the current credentials to a file
        gauth.SaveCredentialsFile("creds.txt")

        return GoogleDrive(gauth)
    # print(dir(drive.ListFile()))

    def get_file_id(self, fname):
        """
        Similar to list file, but this one returns IDs and None!
        Naive assumption to return first, I know, but screw it.
        """
        files = self.drive.ListFile({
            'q': "'root' in parents and trashed=false" +
                 " and title='{0}'".format(fname),
            'maxResults': 1
        }).GetList()
        if len(files) == 0 or len(files) > 1:
            return None
        else:
            return files[0]['id']

    def file_exists(self, fname):
        """
        Returns:
            bool: True if file exists
        """
        files = self.drive.ListFile({
            'q': "'root' in parents and trashed=false" +
                 " and title='{0}'".format(fname),
            'maxResults': 1
        }).GetList()
        if len(files) == 0:
            return False
        else:
            return True

    def create_file(self, fname, body, folder_id=None):
        """
        Returns:
            None or str: None when a file was not created
                         if creation success, file ID is returned
        """
        if not isinstance(fname, str) or not isinstance(body, str):
            raise Exception("Both params must be strings")

        # if self.file_exists(fname):
        #     self.logger.error("File {0} exists".format(fname))
        #     return None

        file_props = {
            'title': fname
        }
        if folder_id is not None:
            file_props['parents'] = [{'id': folder_id}]

        file = self.drive.CreateFile(file_props)
        file.SetContentString(body)
        # +1 for off by 1
        for i in range(1, self.retries + 1):
            try:
                file.Upload(param={'http': self.http})
                self.logger.info("Uploaded {0}".format(fname))
                break
            except ApiRequestError as e:
                self.logger.error(e)
                # Why +1 you ask? Because randrange blows up otherwise.
                # BACK OFF BRO.
                sleep_with_backoff = randrange(
                    self.sleep_time, self.sleep_time * (i + 1))
                self.logger.info("Sleeping for {n} secs".format(
                    n=sleep_with_backoff))
                sleep(sleep_with_backoff)
        assert 'id' in file
        return file['id']

    def create_folder(self, fname):
        folder = self.drive.CreateFile({
            'title': fname,
            'mimeType': 'application/vnd.google-apps.folder'})
        folder.Upload(param={'http': self.http})
        return folder

# Download file
# file3 = drive.CreateFile({'id': file2['id']})
# print('Downloading file %s from Google Drive' % file3['title']) # 'hello.png'
# file3.GetContentFile('world.png')  # Save Drive file as a local file
# GetContentString also works

# Advanced users: Google Drive is known to add BOM (Byte Order Marks) to
# the beginning of some files, such as Google Documents downloaded as text
# files. In some cases confuses parsers and leads to corrupt files.
# PyDrive can remove the BOM from the beginning of a file when it
# is downloaded. Just set the remove_bom parameter in GetContentString()
# or GetContentFile() - see examples/strip_bom_example.py in the GitHub
# repository for an example.


if __name__ == '__main__':
    data_store = StoreIt()
    data_store.create_file(fname="hello_world.txt",
                           folder_name=config['folder_name'],
                           body="Hi, hey, how are ya?")
