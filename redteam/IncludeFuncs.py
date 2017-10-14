#!/usr/bin/env python
"""Include functions for redteam SDK"""

import os
import subprocess

__author__ = 'Jason Callaway'
__email__ = 'jasoncallaway@fedoraproject.org'
__license__ = 'GNU Public License v2'
__version__ = '0.3'
__status__ = 'alpha'


class IncludeFuncs(object):
    def __init__(self):
        pass

    @staticmethod
    def run_command(cmd, description):
        try:
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
            results = p.communicate()[0]
        except Exception as e:
            raise Exception(description + ' failed: ' + str(e))
        return results

    @staticmethod
    def mkdir_p(path):
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno == 17 and os.path.isdir(path):
                pass
            else:
                raise
