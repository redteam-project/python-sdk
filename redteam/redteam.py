#!/usr/bin/env python
"""SDK for redteam"""

import EDB, RedTeamTrello, SAPI

__author__ = 'Jason Callaway'
__email__ = 'jasoncallaway@fedoraproject.org'
__license__ = 'GNU Public License v2'
__version__ = '0.2'
__status__ = 'alpha'


class RedTeam(object):

    def __init__(self, **kwargs):
        self.debug = False
        if kwargs.get('debug'):
            self.debug = kwargs['debug']

        # Todo: add support in this constructor for subclass arguments
        self.EDB = EDB.EDB()

        # Todo: this next part is dumb. fix it.
        # self.connect_to_trello = True
        # if kwargs.get('connect_to_trello'):
        #     self.connect_to_trello = kwargs['connect_to_trello']
        # if self.connect_to_trello:
        #     self.RedTeamTrello = RedTeamTrello.RedTeamTrello()

        self.SAPI = SAPI.SAPI(debug=self.debug)