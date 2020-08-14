"""
quizresult.py

Meant to parse out an array of he
"""

from datetime import datetime
from dateutil import parser

VALID_DOMAINS = ['dallasmakerspace.org']
HEADER_TIMESTAMP = ['timestamp']
HEADER_EMAIL = ['email address']
HEADER_SCORE = ['score']

class QuizResult():
    """ QuizResult """
    def __init__(self, email, score, timestamp):
        self.email = email
        self.score = score
        self.timestamp = timestamp

    @staticmethod
    def loader(header, values):
        ''' loads values from array '''
        timestamp_col = -1
        email_col = -1
        score_col = -1
        for i in range(len(header)):
            if header[i].lower() in HEADER_TIMESTAMP:
                timestamp_col = i
            elif header[i].lower() in HEADER_EMAIL:
                email_col = i
            elif header[i].lower() in HEADER_SCORE:
                score_col = i

        return [QuizResult(x[email_col], x[score_col], x[timestamp_col]) for x in values]

    @property
    def timestamp(self):
        ''' timestamp of entry '''
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        ''' set timestamp '''
        if isinstance(value, datetime):
            self._timestamp = value

        value = str(value)
        self._timestamp = parser.parse(value)

    @property
    def score(self):
        ''' get point score '''
        return self._score

    @score.setter
    def score(self, value):
        ''' set from point string ## / ## '''
        res = str(value).split('/')
        self._total_score = int(res[1])
        self._score = int(res[0])
        self._percentage = float(res[0]) / float(res[1]) * 100

    @property
    def total_score(self):
        ''' get total possible score '''
        return self._total_score

    @property
    def percentage(self):
        ''' get percentage out of 100 '''
        return self._percentage

    @property
    def username(self):
        ''' DMS username (from email) '''
        if self._email is None:
            return None

        return self._email.split("@")[0]

    @property
    def email(self):
        ''' full email of result '''
        return self._email

    @email.setter
    def email(self, value):
        ''' set email '''
        self._email = value

    @property
    def is_dms_user(self):
        ''' is email from dms '''
        return self._email.split("@")[1].lower() in VALID_DOMAINS
