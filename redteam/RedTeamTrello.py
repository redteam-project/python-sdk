import yaml
import trello as pytrello
from jinja2 import Environment, BaseLoader
import os


class RedTeamTrello(object):
    def __init__(self, **kwargs):
        # Cards cache
        self.cards = {}

        # Get config values
        self.config = {}
        if kwargs.get('config'):
            self.config_yml = kwargs['config']
        else:
            self.config_yml = os.path.dirname(os.path.realpath(__file__)) + \
                          '/trello.yml'
        try:
            with open(self.config_yml) as f:
                self.config = yaml.safe_load(f.read())
        except IOError as e:
            raise IOError(e)

        # Get jinja templates
        if kwargs.get('templates'):
            self.template_dir = kwargs['templates']
        else:
            self.template_dir = \
                os.path.dirname(os.path.realpath(__file__)) + '/'
        self.template_curated = self.template_dir + 'curated.j2'
        self.template_mapped = self.template_dir + 'mapped.j2'
        try:
            with open(self.template_curated) as f:
                pass
            with open(self.template_mapped) as f:
                pass
        except IOError as e:
            raise IOError(e)

        # Get auth keys
        if kwargs.get('auth'):
            self.auth_yml = kwargs['auth']
            try:
                self.auth = yaml.safe_load(self.auth_yml)
            except Exception as e:
                raise Exception('redteam could not load the auth yml at ' +
                                self.auth_yml)
        else:
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

        # Fire up Trello client
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

    def get_extant_cards_in_list(self, cache=True, **kwargs):
        list_id = ''
        if kwargs.get('list_id'):
            list_id = kwargs['list_id']
        else:
            list_id = self.config['list_mapped_id']

        try:
            board = self.client.get_board(board_id=self.config['board_id'])
            list = board.get_list(list_id)
            cards = list.list_cards()
            if cache:
                for card in cards:
                    self.cards[card.name] = card.id
            return cards
        except Exception as e:
            raise Exception('redteam could not list cards in list ' +
                            list_id + ': ' + str(e))

    def render_description(self, state, values, **kwargs):
        if state == 'mapped' or state == 'curated':
            template = ''
            if kwargs.get('template'):
                template = kwargs['template']
            else:
                template = self.template_mapped
            try:
                jinja_template = Environment(loader=BaseLoader()).from_string(template)
                return jinja_template.render(values)
            except Exception as e:
                raise Exception('redteam could not get or render template ' +
                                template + ': ' + str(e))
        else:
            raise Exception('redteam render_description state must be ' +
                            '"mapped" or "curated"')

    def get_card_id(self, name, use_cache=True, **kwargs):
        list_id = ''
        if kwargs.get('list_id'):
            list_id = kwargs['list_id']
        else:
            list_id = self.config['list_mapped_id']

        try:
            if use_cache and self.cards:
                card_names = self.cards.keys()
                if name in card_names:
                    return self.cards[name]
                else:
                    return None
            else:
                cards = self.get_extant_cards_in_list(self.config['board_id'],
                                                      list_id=list_id)
                card_names = self.cards.keys()
                if name in card_names:
                    return cards[name]
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
        card_labels = None
        if kwargs.get('card_labels'):
            card_labels = kwargs['card_lables']
        try:
            board = self.client.get_board(board_id=self.config['board_id'])
            list = board.get_list(list_id)
            if card_labels:
                list.add_card(name=name, desc=desc, labels=card_labels)
            list.add_card(name=name, desc=desc)
        except Exception as e:
            raise Exception('redteam could not add card to list ' + list_id +
                            ' ' + str(e))




