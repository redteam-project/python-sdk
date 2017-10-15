#!/usr/bin/env python
"""Include functions for redteam SDK"""

import os
import subprocess
import yaml

__author__ = 'Jason Callaway'
__email__ = 'jasoncallaway@fedoraproject.org'
__license__ = 'GNU Public License v2'
__version__ = '0.3.4'
__status__ = 'alpha'


class IncludeFuncs(object):
    def __init__(self):
        pass

    @staticmethod
    def parse_yaml(filename):
        return yaml.safe_load(filename)

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

    @staticmethod
    def is_executable(absolute_path):
        if os.path.isfile(absolute_path) and \
                os.access(absolute_path, os.X_OK):
            return True
        else:
            return False

    def which(self, program):
        import os

        for path in os.environ["PATH"].split(os.pathsep):
            absolute_path = os.path.join(path, program)
            if self.is_executable(absolute_path):
                return absolute_path

        return None
