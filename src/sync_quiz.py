#!/usr/bin/env python3
"""
sync_quiz.py

Copyrighted (c)2020 Dallas Makerspace. All Rights Reserved.

Take google quiz results and adds users to appropriate AD groups if
they've passed.
"""

from dateutil import parser as dtparser
from ldap3 import Server, Connection, ALL
from srvlookup import SRVQueryFailure, lookup as dnssd
from sheetquery import SheetQuery
from quizresult import QuizResult

SAMPLE_SPREADSHEET_ID = '1u80WhL5TQdGIj8Sl1ItFoaqrc3fGixwGEj6AnYrjVcg'

def run():
    """ run """

    sheets = SheetQuery( \
        credentials='../credentials.json', \
        sheetid=SAMPLE_SPREADSHEET_ID)
    last_check = sheets.get_last_changed()


    # if there is a lastcheck, filter data
    result = sheets.get_values()

    values = result.get('values', [])

    if not values:
        print('No data found.')
        return

    header = values[0]
    values = values[1:]

    quizzes = QuizResult.loader(header, values)
    if last_check is not None:
        check = dtparser.parse(last_check)
        quizzes = [q for q in quizzes if q.timestamp >= check]

    # Scenarios - 100% only, >x%,

    # connect to AD

    # get user

    # add to group if necessary

    # Connect to DB to log users being added

    # update sheet value
