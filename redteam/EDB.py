
from fake_useragent import UserAgent
import requests
from BeautifulSoup import BeautifulSoup
from HTMLParser import HTMLParser


class EDB(object):
    def __init__(self):
        self.edb_url = 'https://www.exploit-db.com/exploits/'
        self.ua = UserAgent()
        self.headers = {'User-Agent': str(self.ua.chrome)}

    def get_title(self, edb_id, **kwargs):
        edb_url = ''
        headers = ''
        if kwargs.get('edb_url'):
            edb_url = kwargs['edb_url']
        else:
            edb_url = self.edb_url
        if kwargs.get('headers'):
            headers = kwargs['headers']
        else:
            headers = self.headers

        try:
            edb_html = requests.get(edb_url,
                                    headers=headers)
            parser = HTMLParser()
            soup = BeautifulSoup(edb_html.content)
            title_tag = soup.findAll('h1', itemprop='headline')
            title = parser.unescape(title_tag[0].contents[0])
        except Exception as e:
            raise Exception('redteam could not get EDB title: ' + str(e))

        return title



