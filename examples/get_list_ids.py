#!/usr/bin/env python
"""Examples of how to use the redteam SDK"""

import sys
import traceback

sys.path.append('..')
from redteam import redteam

__author__ = 'Jason Callaway'
__email__ = 'jasoncallaway@fedoraproject.org'
__license__ = 'GNU Public License v2'

# Initialize our redteam SDK
r = redteam.RedTeam()
trello = r.RedTeamTrello

for l in trello.get_lists():
    print(l.name + '\t' + l.id)
