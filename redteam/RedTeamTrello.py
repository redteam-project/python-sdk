#!/usr/bin/env python
"""Trello exploit crowdwourcing SDK for redteam"""

import os

import trello as pytrello
import yaml
from jinja2 import Environment, FileSystemLoader

__author__ = 'Jason Callaway'
__email__ = 'jasoncallaway@fedoraproject.org'
__license__ = 'GNU Public License v2'
__version__ = '0.3.4'
__status__ = 'alpha'


class RedTeamTrello(object):
    def __init__(self, **kwargs):
        # Cards cache. We'll try to use this instead of getting the same card
        # lists for subsequent calls of list functions
        self.cards_by_name = {}
        self.cards_by_id = {}

        self.cache_dir = os.getcwd() + '/trello'
        if kwargs.get('cache_dir'):
            self.cache_dir = kwargs['cache_dir'] + '/trello'

        # Get config values
        self.config = {}
        if kwargs.get('config'):
            # If a different yml config is specified, we'll use that
            self.config_yml = kwargs['config']
        else:
            # Otherwise, go with the default config file
            self.config_yml = self.cache_dir + '/trello.yml'
        try:
            with open(self.config_yml) as f:
                self.config = yaml.safe_load(f.read())
        except IOError as e:
            raise IOError(e)

        # Get jinja templates
        self.template_dir = self.cache_dir
        if kwargs.get('templates'):
            # if a different path to j2 templates is specified, use it
            self.template_dir = kwargs['templates']
        # We currently only have 'mapped' and 'curated' exploit states, with a
        # jinja2 template for each
        self.template_curated = self.template_dir + '/curated.j2'
        self.template_mapped = self.template_dir + '/mapped.j2'
        try:
            with open(self.template_curated) as f:
                pass
            with open(self.template_mapped) as f:
                pass
        except IOError as e:
            raise IOError('redteam could not read the jinja templates at ' +
                          self.template_dir + ': ' + str(e))

        # Get auth keys, either from a yml file, dict,  or environment
        # variables
        auth_yml = self.cache_dir + '/trello/auth.yml'
        if os.path.isfile(auth_yml):
            try:
                self.auth = yaml.safe_load(auth_yml)
            except Exception as e:
                raise Exception('redteam could not load the auth yml at ' +
                                auth_yml)
        elif kwargs.get('auth'):
            # If auth is specified in the constructor, use that absolute path
            self.auth = kwargs['auth']
        else:
            # The default is to look at the calling environment variables for
            # our auth data
            trello_auth_values = ['REDTEAM_TRELLO_API_KEY',
                                  'REDTEAM_TRELLO_API_SECRET',
                                  'REDTEAM_TRELLO_TOKEN',
                                  'REDTEAM_TRELLO_TOKEN_SECRET']
            auth = {}
            for v in trello_auth_values:
                if os.environ.get(v) is None:
                    raise Exception('redteam needs ' + v + ' environment ' +
                                    'variable to be set')
                auth[v] = os.environ.get(v)
            self.auth = auth

        # Create a connection to the Trello API

        try:
            self.client = pytrello.TrelloClient(
                api_key=self.auth['REDTEAM_TRELLO_API_KEY'],
                api_secret=self.auth['REDTEAM_TRELLO_API_SECRET'],
                token=self.auth['REDTEAM_TRELLO_TOKEN'],
                token_secret=self.auth['REDTEAM_TRELLO_TOKEN_SECRET']
            )

        except Exception as e:
            raise Exception('redteam could not initilize the py-trello ' +
                            'client: ' + str(e))

    @staticmethod
    def parse_exploits(csv):
        """Parse `elem assess` output in the form of a csv file"""

        # Note, this is brittle and depends on elem output
        exploits = {}
        try:
            with open(csv) as f:
                for line in f.readlines():
                    # If there are more than two values, the EDB ID has been
                    # curated.
                    if len(line.split(',')) > 2:
                        edb_id, cve_id, cpe, scoring, score = line.split(',')
                        # Have we seen this EDB ID before? If so, just append
                        # the CVE IDs
                        if exploits.get(edb_id):
                            exploits[edb_id]['cve_ids'] = \
                                exploits[edb_id]['cve_ids'] + ', ' + \
                                cve_id.rstrip()
                        # If not, make a new EDB dict
                        else:
                            exploits[edb_id] = {}
                            exploits[edb_id]['edb_id'] = edb_id
                            exploits[edb_id]['cve_ids'] = cve_id.rstrip()
                            exploits[edb_id]['cpe'] = cpe
                            exploits[edb_id]['scoring'] = scoring
                            exploits[edb_id]['score'] = score
                            exploits[edb_id]['curated'] = True
                    # If there are only two values, the EDB ID has been mapped
                    else:
                        edb_id, cve_id = line.split(',')
                        # We check to see if we already have this EDB ID in
                        # the dict. If so, append the CVE IDs
                        if exploits.get(edb_id):
                            exploits[edb_id]['cve_ids'] = \
                                exploits[edb_id]['cve_ids'] + ', ' + \
                                cve_id.rstrip()
                        else:
                            exploits[edb_id] = {}
                            exploits[edb_id]['edb_id'] = edb_id
                            exploits[edb_id]['cve_ids'] = cve_id.rstrip()
        except IOError as e:
            raise IOError('redteam could not parse the CVE csv input: ' +
                          str(e))

        return exploits

    def get_lists(self, **kwargs):
        """Get list names and IDs from a board"""

        board_id = self.config['board_id']
        if kwargs.get('board_id'):
            # Check to see if a board_id was explicitly specified
            board_id = kwargs['board_id']

        board = self.client.get_board(board_id=board_id)
        return board.open_lists()

    def update_cards_cache(self, **kwargs):
        """Get the Trello cards in list_id and return a list of names"""

        # These are too variable to pickle, so we reach out to the API each
        # time.

        list_id = self.config['list_mapped_id']
        if kwargs.get('list_id'):
            # Check to see if a list_id was explicitly specified
            list_id = kwargs['list_id']
        # Todo: add support for explicit board_id

        try:
            # Get the board and list objects from the Trello SDK and create a
            # list of card objects
            board = self.client.get_board(board_id=self.config['board_id'])
            board_list = board.get_list(list_id)
            cards = board_list.list_cards()
            for card in cards:
                # Update the cards cache, both by name and id
                self.cards_by_name[card.name] = card.id
                self.cards_by_id[card.id] = card.name
        except Exception as e:
            raise Exception('redteam could update cards cache ' +
                            list_id + ': ' + str(e))

    def render_description(self, state, values):
        """Render a card's description based on a jinja2 template"""

        # Validate that we're dealing with an accepted state
        if state == 'mapped' or state == 'curated':
            try:
                # Render and return the template
                jinja_env = \
                    Environment(loader=FileSystemLoader(self.template_dir))
                return jinja_env.get_template(state + '.j2').render(values)
            except Exception as e:
                raise Exception('redteam could not get or render template ' +
                                state + '.j2: ' + str(e))
        else:
            raise Exception('redteam render_description state must be ' +
                            '"mapped" or "curated"')

    def get_card_id(self, name, use_cache=False, **kwargs):
        """Get a Trello card's ID by its name"""

        # Load the default list_id
        list_id = self.config['list_mapped_id']
        if kwargs.get('list_id'):
            # Check to see if a list_id was explictly set
            list_id = kwargs['list_id']

        try:
            if not use_cache:
                # Normally we use the cards cache, but we update it if
                # use_cache is set to false
                self.update_cards_cache(list_id=list_id)
            if name in self.cards_by_name.keys():
                # If the card exists, return its ID
                return self.cards_by_name[name]
            else:
                return None
        except Exception as e:
            raise Exception('redteam cannot get_card_id for name ' +
                            name + ' in list ' + list_id + ' ' + str(e))

    def get_mapped_list_id(self):
        return self.config['list_mapped_id']

    def get_curated_list_id(self):
        return self.config['list_curated_id']

    def add_card(self, list_id, name, desc, **kwargs):
        """Use the Trello SDK to create a new card"""

        # By default we don't use any labels, but we'll check for explictly
        # set ones
        card_labels = None
        if kwargs.get('card_labels'):
            card_labels = kwargs['card_lables']
        try:
            # Get the board object
            board = self.client.get_board(board_id=self.config['board_id'])
            # Get the list object from the board
            board_list = board.get_list(list_id)
            if card_labels:
                # If there are labels set, create the card with labels
                board_list.add_card(name=name, desc=desc, labels=card_labels)
            else:
                # Otherwise, create the card without labels
                board_list.add_card(name=name, desc=desc)
        except Exception as e:
            raise Exception('redteam could not add card to list ' + list_id +
                            ' ' + str(e))




