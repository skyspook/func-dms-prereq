import os.path
import pprint
import ipdb
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import dateutil.parser


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1u80WhL5TQdGIj8Sl1ItFoaqrc3fGixwGEj6AnYrjVcg'
SAMPLE_RANGE_NAME = 'Form Responses 1!A:D'
LASTCHECK_ID=1337


def create_metadata_body():
   return {
        'requests': [
        {
            'createDeveloperMetadata':{
                'developerMetadata': create_metadata()
            }
        }]
    }

def create_metadata():
    return {
        'metadataId':LASTCHECK_ID,
        'metadataKey':'lastCheck',
        'metadataValue':datetime.now().strftime('%m/%d/%Y %H:%M:%S'),
        'location': {'spreadsheet':True},
        'visibility':'DOCUMENT'
    }

def create_updatemeta_body():
    return {
        'requests': [
        {
            'updateDeveloperMetadata':
            {
                'dataFilters':[ {'developerMetadataLookup':{ 'locationType':'SPREADSHEET', 'metadataId':LASTCHECK_ID}} ],
                'developerMetadata':create_metadata(),
                'fields': 'metadataValue'
            }
        }]
    }



def create_lastcheck(sheet):
    resp = sheet.batchUpdate( \
        spreadsheetId = SAMPLE_SPREADSHEET_ID,
        body = create_metadata_body()
    ).execute()

def check_lastcheck(sheet):
    try:
        resp = sheet.developerMetadata() \
            .get( \
                spreadsheetId=SAMPLE_SPREADSHEET_ID,
                metadataId=LASTCHECK_ID) \
            .execute()
        if resp:
            return resp.get('metadataValue')
    except HttpError:
        create_lastcheck(sheet)
        return None

def loader(header, values):
    timestamp_col = -1
    email_col = -1
    score_col = -1
    for i in range(len(header)):
        if header[i].lower() == 'timestamp':
            timestamp_col = i
        elif header[i].lower() == 'email address':
            email_col = i
        elif header[i].lower() == 'score':
            score_col = i
    
    return [ QuizResult( x[email_col], x[score_col], x[timestamp_col]) for x in values]



class QuizResult(object):
    def __init__(self, email, score, timestamp):
        self.email = email
        self.score = score
        self.timestamp = timestamp
        
    @property
    def timestamp(self):
        return self._timestamp
    
    @timestamp.setter
    def timestamp(self,value):
        if isinstance(value,datetime):
            self._timestamp = value
        
        value = str(value)
        self._timestamp = dateutil.parser.parse(value)

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self,value):
        s = str(value)
        res = s.split('/')
        self._total_score = int(res[1])
        self._score = int(res[0])
        self._percentage = float(res[0]) / float(res[1]) * 100

    @property
    def total_score(self):
        return self._total_score

    @property
    def percentage(self):
        return self._percentage

    @property
    def username(self):
        if self._email is None:
            return None
        else:
            return self._email.split("@")[0]
    
    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self,value):
        self._email = value

def main():
    creds = None

    #Needs a project and service account created with API key. Then going into google sheets API and activating
    #Share the sheet with the service account for access
    creds = service_account.Credentials.from_service_account_file( 'credentials.json', scopes=SCOPES )
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    lastCheck = check_lastcheck(sheet)

    # if there is a lastcheck, filter data
    result = sheet.values().get( \
        spreadsheetId=SAMPLE_SPREADSHEET_ID, \
        range=SAMPLE_RANGE_NAME).execute()


    values = result.get('values',[])

    if not values:
        print('No data found.')
        return

    for row in values:
        pprint.pprint(row)

    header = values[0]
    values = values[1:]
    ipdb.set_trace()
    quizzes = loader(header,values)

    check = dateutil.parser.parse(lastCheck)
    quizzes = [q for q in quizzes if q.timestamp >= check ]


if __name__ == '__main__':
    main()