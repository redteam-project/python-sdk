#!/usr/bin/env python
"""SDK for redteam"""

import os
import shutil
import subprocess
import EDB, RedTeamTrello, SAPI, IncludeFuncs

__author__ = 'Jason Callaway'
__email__ = 'jasoncallaway@fedoraproject.org'
__license__ = 'GNU Public License v2'
__version__ = '0.3.5'
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

        if kwargs.get('init_trello'):
            if kwargs['init_trello'] is True:
                try:
                    self.setup_trello()
                    # Todo: this seems broken. Fix it, for now commented out
                    # self.connect_to_trello = True
                    # if kwargs.get('connect_to_trello'):
                    #     self.connect_to_trello = kwargs['connect_to_trello']
                    # if self.connect_to_trello:
                    #     self.RedTeamTrello = \
                    #         RedTeamTrello.RedTeamTrello(cache_dir=self.cache_dir)
                except Exception as e:
                    raise
        if kwargs.get('init_edb'):
            if kwargs['init_edb'] is True:
                try:
                    self.EDB = EDB.EDB(cache_dir=self.cache_dir)
                except Exception as e:
                    raise

        if kwargs.get('init_sapi'):
            if kwargs['init_sapi'] is True:
                try:
                    self.SAPI = SAPI.SAPI(debug=self.debug,
                                          cache_dir=self.cache_dir)
                except Exception as e:
                    raise

    def setup_trello(self, **kwargs):
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
            need_to_untar = False
            for filename in ['curated.j2', 'mapped.j2', 'trello.yml']:
                new_file = self.cache_dir + '/trello/' + filename
                if not os.path.isfile(new_file):
                    need_to_untar = True
                    # shutil.copy2(source_dir + '/defaults/trello/' + filename,
                    #              new_file)
                    # if self.debug:
                    #     print('+ copied ' + source_dir + '/' + filename +
                    #           ' to ' + new_file)
            if need_to_untar:
                tar = self.funcs.which('tar')
                r = self.funcs.run_command('(cd ' + self.cache_dir + '; ' +
                                           tar + ' xzf' + source_dir +
                                           '/trello.tar.gz)', 'Trello')
                if self.debug:
                    print('+ untarred ' + source_dir + '/trello.tar.gz')

        except Exception as e:
            raise

