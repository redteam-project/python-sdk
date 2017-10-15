#!/usr/bin/env python
"""Exploit-DB helper functions for redteam"""

import calendar
import os
import time

import requests
from fake_useragent import UserAgent

__author__ = 'Jason Callaway'
__email__ = 'jasoncallaway@fedoraproject.org'
__license__ = 'GNU Public License v2'
__version__ = '0.3.4'
__status__ = 'alpha'


class EDB(object):
    def __init__(self, **kwargs):
        self.dir = kwargs['cache_dir'] + '/edb'
        self.filescsv = self.dir + '/files.csv'
        self.filescsv_url = 'https://raw.githubusercontent.com/' + \
                            'offensive-security/exploit-database/' + \
                            'master/files.csv'
        self.edb_url = 'https://www.exploit-db.com/exploits/'
        self.ua = UserAgent()
        self.headers = {'User-Agent': str(self.ua.chrome)}
        self.metadata = self.parse_filescsv()

    def download_filescsv(self, **kwargs):
        filename = self.filescsv
        if kwargs.get('output'):
            filename = kwargs['output']

        try:
            response = requests.get(self.filescsv_url)
            with open(filename, 'w') as f:
                f.write(response.content)
        except Exception as e:
            raise Exception('redteam.EDB could not get new files.csv: ' +
                            str(e))

    def refresh_filescsv(self, force=False):
        if os.path.isfile(self.filescsv):
            s = os.stat(self.filescsv)
            now = calendar.timegm(time.gmtime())
            if now - s.st_mtime > 86400 or force:
                try:
                    self.download_filescsv()
                except Exception as e:
                    raise e
        else:
            try:
                self.download_filescsv()
            except Exception as e:
                raise e

    def parse_filescsv(self):
        self.refresh_filescsv()
        exploits = {}
        try:
            with open(self.filescsv) as f:
                for line in f.readlines()[1:]:
                    edb_id = ''
                    exploit = {}
                    fields =  line.split(',')
                    edb_id = fields[0]
                    exploit['filename'] = fields[1]
                    exploit['description'] = fields[2]
                    exploit['date'] = fields[3]
                    exploit['author'] = fields[4]
                    exploit['platform'] = fields[5]
                    exploit['os_type'] = fields[6]
                    exploit['port'] = fields[7]
                    exploit['edb_url'] = self.edb_url + edb_id
                    exploits[edb_id] = exploit
        except Exception as e:
            raise Exception('redteam.EDB could not parse files.csv: ' +
                            str(e))
        return exploits

    def get_title(self, edb_id):
        if self.metadata.get(edb_id):
            return self.metadata[edb_id]['description']
        else:
            raise Exception('no exploit found for EDB ID: ' + edb_id)

    def get_url(self, edb_id):
        return self.edb_url + edb_id



