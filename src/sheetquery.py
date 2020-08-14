"""
sheetquery.py

Copyrighted (c)2020Dallas Makerspace. All Rights Reserved.

Loads and marks google sheets associated with quiz results.

"""
from os.path import path
from json import load
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
LASTCHECK_ID = 1337
RANGE = 'Form Responses 1!A:D'


class SheetQuery():
    ''' SheetQuery - Communicates with google sheets '''

    def __init__(self, credentials, sheetid):
        if path.isfile(credentials):
            creds = service_account.Credentials.from_service_account_file( \
                credentials, \
                scopes=SCOPES)
        else:
            service_account_info = load(credentials)
            creds = service_account.Credentials.from_service_account_info(service_account_info)

        service = build('sheets', 'v4', credentials=creds)
        self._sheet = service.spreadsheets()
        self._sheetid = sheetid
        self._lastcheck = None

    def _make_create_body(self, value):
        return {
            'requests': [{
                'createDeveloperMetadata':{
                    'developerMetadata': self._create_metadata(value)
                }
            }]
        }

    def _create_metadata(self, value):
        return {
            'metadataId':LASTCHECK_ID,
            'metadataKey':'lastCheck',
            'metadataValue':value,
            'location': {'spreadsheet':True},
            'visibility':'DOCUMENT'
        }

    def _make_update_body(self, value):
        return {
            'requests': [{
                'updateDeveloperMetadata': {
                    'dataFilters':[{
                        'developerMetadataLookup':{
                            'locationType':'SPREADSHEET',
                            'metadataId':LASTCHECK_ID
                        }
                    }],
                    'developerMetadata':self._create_metadata(value),
                    'fields': 'metadataValue'
                }
            }]
        }

    def _create_lastcheck(self, value):
        self._sheet.batchUpdate( \
            spreadsheetId=self._sheetid,
            body=self._make_create_body(value)) \
            .execute()

    def _update_lastcheck(self, value):
        self._sheet.batchUpdate( \
            spreadsheetId=self._sheetid,
            body=self._make_update_body(value)) \
            .execute()

    def _check_lastcheck(self):
        self._lastcheck = None
        try:
            resp = self._sheet.developerMetadata() \
                .get( \
                    spreadsheetId=self._sheetid,
                    metadataId=LASTCHECK_ID) \
                .execute()
            if resp:
                self._lastcheck = resp.get('metadataValue')
        except HttpError:
            pass

        return self._lastcheck


    def get_last_changed(self):
        '''
        get_last_changed
        Retrieves the last time we retrieved the sheet data
        '''
        return self._check_lastcheck()

    def update_last_changed(self, value=None):
        """
        update_last_changed
        Updated when we last retrieved data from the sheet
        """
        value = value or datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        self._check_lastcheck()
        if self._lastcheck is None:
            self._create_lastcheck(value)
        else:
            self._update_lastcheck(value)


    def get_values(self):
        """
        get_values
        get the values from the sheet
        """
        return self._sheet.values().get( \
            spreadsheetId=self._sheetid, \
            range=RANGE) \
            .execute()
