#!/usr/bin/env python
"""SDK for redteam"""

import os
import shutil
import subprocess
import EDB, RedTeamTrello, SAPI, IncludeFuncs

__author__ = 'Jason Callaway'
__email__ = 'jasoncallaway@fedoraproject.org'
__license__ = 'GNU Public License v2'
__version__ = '0.3.2'
__status__ = 'alpha'


class RedTeam(object):
    def __init__(self, **kwargs):
        self.dest_dir = None
        self.cache_dir = os.getcwd()
        if kwargs.get('cache_dir'):
            self.cache_dir = kwargs['cache_dir']

        self.funcs = IncludeFuncs.IncludeFuncs()

        self.debug = False
        if kwargs.get('debug'):
            self.debug = kwargs['debug']

        try:
            self.setup()
            # Todo: add support in this constructor for subclass arguments

            self.EDB = EDB.EDB(cache_dir=self.cache_dir)

            # Todo: this seems broken. Fix it, for now commented out
            # self.connect_to_trello = True
            # if kwargs.get('connect_to_trello'):
            #     self.connect_to_trello = kwargs['connect_to_trello']
            # if self.connect_to_trello:
            #     self.RedTeamTrello = \
            #         RedTeamTrello.RedTeamTrello(cache_dir=self.cache_dir)

            self.SAPI = SAPI.SAPI(debug=self.debug, cache_dir=self.cache_dir)
        except Exception as e:
            raise

    def setup(self, **kwargs):
        source_dir = os.path.dirname(os.path.realpath(__file__))

        if '~' in self.cache_dir:
            self.cache_dir = os.path.expanduser(self.cache_dir)

        try:
            for new_dir in ['edb', 'trello', 'sapi', 'sapi/picklejar']:
                dir_name = self.cache_dir + '/' + new_dir
                if not os.path.isdir(dir_name):
                    self.funcs.mkdir_p(dir_name)
                    if self.debug:
                        print('+ made directory: ' + dir_name)

            # setup trello files
            for filename in ['curated.j2', 'mapped.j2', 'trello.yml']:
                new_file = self.cache_dir + '/trello/' + filename
                if not os.path.isfile(new_file):
                    shutil.copy2(source_dir + '/defaults/trello/' + filename,
                                 new_file)
                    if self.debug:
                        print('+ copied ' + source_dir + '/' + filename +
                              ' to ' + new_file)
        except Exception as e:
            raise

