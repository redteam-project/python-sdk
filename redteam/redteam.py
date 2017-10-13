#!/usr/bin/env python
"""SDK for redteam"""

import EDB, RedTeamTrello

__author__ = 'Jason Callaway'
__email__ = 'jasoncallaway@fedoraproject.org'
__license__ = 'GNU Public License v2'
__version__ = '0.2'
__status__ = 'alpha'

class RedTeam(object):

    def __init__(self):
        # Todo: add support in this constructor for subclass arguments
        self.EDB = EDB.EDB()
        self.RedTeamTrello = RedTeamTrello.RedTeamTrello()