#!/usr/bin/env python
"""Security Data API SDK for redteam"""

import cPickle as pickle
import errno
import json
import os
import re
import urllib2

from datetime import datetime

import IncludeFuncs

__author__ = 'Jason Callaway'
__email__ = 'jasoncallaway@fedoraproject.org'
__license__ = 'GNU Public License v2'
__version__ = '0.3.4'
__status__ = 'alpha'


class SAPI(object):
    def __init__(self, **kwargs):
        self.cvrf = []
        self.rhsas = []

        self.funcs = IncludeFuncs.IncludeFuncs()

        self.cache_dir = os.getcwd() + '/sapi'
        if kwargs.get('cache_dir'):
            self.cache_dir = kwargs['cache_dir'] + '/sapi'

        self.debug = False
        if kwargs.get('debug'):
            self.debug = kwargs['debug']

        self.connected = True
        if kwargs.get('connected'):
            self.connected = kwargs['connected']

        self.redhat_sapi = 'https://access.redhat.com/labs/securitydataapi/'

        if kwargs.get('day'):
            self.day = kwargs['day']
        else:
            self.day = datetime.strftime(datetime.now(), '%Y%m%d')
        self.second = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')

        self.picklejar = self.cache_dir + '/picklejar'
        if kwargs.get('picklejar'):
            self.picklejar = kwargs['picklejar']

        try:
            self.funcs.mkdir_p(self.picklejar)
        except Exception as e:
            raise

    def cache_rhsas(self):
        self.cvrf = self.retrieve_redhat_cfrv()
        self.rhsas = self.generate_rhsas(self.cvrf)
        self.fresh_rhsa_pickles()

    def get_rhsa_pickle_directory(self, title):
        fields = re.split(':|-|\.', title)
        year = fields[1]
        number = fields[2][0]
        pickledir = self.picklejar + '/RHSA/' + year + '/' + number
        if not os.path.isdir(pickledir):
            os.makedirs(pickledir)
        return pickledir

    def retrieve_redhat_cfrv(self):
        cvrf = []
        today_pickle = self.picklejar + '/CVRF_' + self.day + '.pickle'
        if os.path.isfile(today_pickle):
            with open(today_pickle, 'rb') as p:
                cvrf = pickle.load(p)
        else:
            if self.connected:
                response = urllib2.urlopen(self.redhat_sapi + 'cvrf.json')
                cvrf = json.loads(response.read())
                with open(today_pickle, 'wb') as p:
                    pickle.dump(cvrf, p, -1)
            else:
                return ['disconnected with no pickle']
        return cvrf

    def retrieve_ovals(self):
        ovals = {}
        oval_pickles = self.picklejar + '/OVALS'
        if not os.path.isdir(oval_pickles):
            os.makedirs(oval_pickles)
        if self.connected:
            for rhsa in self.rhsas:
                title = rhsa['RHSA']
                this_pickle = oval_pickles + '/' + title + '.pickle'
                if os.path.isfile(this_pickle):
                    with open(this_pickle, 'rb') as p:
                        ovals[title] = pickle.load(p)
                        if self.debug:
                            print('+ unpickling OVAL for ' + title)
                else:
                    u = self.redhat_sapi + 'oval/' + title + '.json'
                    try:
                        response = urllib2.urlopen(u)
                        oval = json.loads(response.read())
                        with open(this_pickle, 'wb') as p:
                            pickle.dump(oval, p, -1)
                        ovals[title] = oval
                        if self.debug:
                            print('+ retrieved OVAL for ' + title)
                    except Exception as e:
                        ovals[title] = {'no oval': 'no oval'}
                        if self.debug:
                            print('+ no OVAL found for ' + title)
        else:
            for rhsa in self.rhsas:
                title = rhsa['RHSA']
                this_pickle = oval_pickles + '/' + title + '.pickle'
                if os.path.isfile(this_pickle):
                    with open(this_pickle, 'rb') as p:
                        ovals[title] = pickle.load(p)
                        if self.debug:
                            print('+ unpickling OVAL for ' + title)
        return ovals

    def retrieve_rhsa(self, title, resource_url):
        pickledir = self.get_rhsa_pickle_directory(title)
        this_pickle = pickledir + '/' + title + '.pickle'
        if os.path.isfile(this_pickle):
            with open(this_pickle, 'rb') as p:
                rhsa = pickle.load(p)
        else:
            if self.debug:
                print('+ pickling ' + title)
            response = urllib2.urlopen(resource_url)
            rhsa = json.loads(response.read())
            with open(this_pickle, 'wb') as p:
                pickle.dump(rhsa, p, -1)
        return rhsa

    def get_rhsa(self, title):
        try:
            pickledir = self.get_rhsa_pickle_directory(title)
            this_pickle = pickledir + '/' + title + '.pickle'
            if self.debug:
                print('+ unpickling ' + this_pickle)
            with open(this_pickle, 'rb') as p:
                rhsa = pickle.load(p)
        except Exception as e:
            return {'does not exist': 'does not exist'}
        return rhsa

    def fresh_rhsa_pickles(self):
        for rhsa in self.rhsas:
            title = rhsa['RHSA']
            resource_url = rhsa['resource_url']
            pickledir = self.get_rhsa_pickle_directory(title)
            this_pickle = pickledir + '/' + title + '.pickle'
            if not os.path.isfile(this_pickle):
                new_rhsa = self.retrieve_rhsa(title, resource_url)

    def generate_rhsas(self, cvrf):
        rhsas = []
        today_pickle = self.picklejar + '/RHSAS_' + self.day + '.pickle'
        if os.path.isfile(today_pickle):
            with open(today_pickle, 'rb') as p:
                rhsas = pickle.load(p)
        else:
            if self.connected:
                for entry in cvrf:
                    rhsa = {}
                    # Only keep entries with updated packages
                    if entry['released_packages']:
                        for tag in ['CVEs', 'RHSA', 'bugzillas',
                                    'released_on', 'released_packages',
                                    'resource_url', 'severity']:
                            if entry[tag]:
                                rhsa[tag] = entry[tag]
                        if entry['oval']['has_oval']:
                            rhsa['oval_resource_url'] = \
                                entry['oval']['resource_url']
                        rhsas.append(rhsa)
                with open(today_pickle, 'wb') as p:
                    pickle.dump(rhsas, p, -1)
            else:
                return ['disconnected with no pickle']
        return rhsas

    def index_by_rpm(self):
        if self.connected:
            with open(self.picklejar + '/index_by_rpm.pickle', 'wb') as p:
                index = {}
                for rhsa in self.rhsas:
                    for package in rhsa['released_packages']:
                        if index.get(package):
                            index[package].append(rhsa['RHSA'])
                        else:
                            index[package] = [rhsa['RHSA']]
                pickle.dump(index, p, -1)
        else:
            with open(self.picklejar + '/index_by_rpm.pickle', 'rb') as p:
                index = pickle.load(p)
        return index

    def get_cvrf(self):
        return self.cvrf

    def get_rhsas(self):
        return self.rhsas

    def get_rhsa_csv(self):
        csv = '"CVEs","RHSA","bugzillas","OVAL","Released","RPMs","URL","Severity"\n'
        for rhsa in self.rhsas:
            if not rhsa.get('CVEs'):
                rhsa['CVEs'] = []
            if not rhsa.get('bugzillas'):
                rhsa['bugzillas'] = []
            if not rhsa.get('oval_resource_url'):
                rhsa['oval_resource_url'] = ''
            # if not rhsa.get('released_packages)'):
            #     rhsa['released_packages'] = []
            line = "\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"\n" % (
                '\n'.join(rhsa['CVEs']),
                rhsa['RHSA'],
                '\n'.join(rhsa['bugzillas']),
                rhsa['oval_resource_url'],
                rhsa['released_on'].replace('+00:00', '').replace('T', ' '),
                '\n'.join(rhsa['released_packages']),
                rhsa['resource_url'],
                rhsa['severity'])
            csv += line
        return csv
