#!/usr/bin/env python
"""SDK for redteam"""

import os
import shutil
import EDB, RedTeamTrello, SAPI

__author__ = 'Jason Callaway'
__email__ = 'jasoncallaway@fedoraproject.org'
__license__ = 'GNU Public License v2'
__version__ = '0.3'
__status__ = 'alpha'


class RedTeam(object):

    @staticmethod
    def mkdir_p(path):
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno == 17 and os.path.isdir(path):
                pass
            else:
                raise

    def setup(self, **kwargs):
        source_dir = os.path.dirname(os.path.realpath(__file__))

        cache_dir = self.cache_dir
        if '~' in cache_dir:
            cache_dir = os.path.expanduser(cache_dir)

        try:
            for new_dir in ['edb', 'trello', 'sapi', 'sapi/picklejar']:
                self.mkdir_p(cache_dir + '/' + new_dir)
                if self.debug:
                    print('+ made directory: ' + cache_dir + '/' + new_dir)

            # setup trello files
            for filename in ['curated.j2', 'mapped.j2', 'trello.yml']:
                shutil.copy2(source_dir + '/defaults/trello/' + filename,
                             cache_dir + '/trello')
                if self.debug:
                    print('+ copied ' + source_dir + '/' + filename +
                          ' to ' + cache_dir + '/trello')
        except Exception as e:
            raise

    def __init__(self, **kwargs):
        self.dest_dir = None
        self.cache_dir = os.getcwd()
        if kwargs.get('cache_dir'):
            self.cache_dir = kwargs['cache_dir']

        self.debug = False
        if kwargs.get('debug'):
            self.debug = kwargs['debug']

        try:
            self.setup()
            # Todo: add support in this constructor for subclass arguments

            self.EDB = EDB.EDB(cache_dir=self.cache_dir)

            # self.connect_to_trello = True
            # if kwargs.get('connect_to_trello'):
            #     self.connect_to_trello = kwargs['connect_to_trello']
            # if self.connect_to_trello:
            #     self.RedTeamTrello = \
            #         RedTeamTrello.RedTeamTrello(cache_dir=self.cache_dir)

            self.SAPI = SAPI.SAPI(debug=self.debug, cache_dir=self.cache_dir)
        except Exception as e:
            raise
