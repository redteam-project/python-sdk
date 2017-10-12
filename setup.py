from distutils.core import setup
import setuptools
setup(name='redteam',
      packages=['redteam'],
      install_requires=['PyYAML', 'py-trello', 'BeautifulSoup', 'HTMLParser',
                        'requests', 'jinja2', 'fake-useragent'],
      version='0.1',
      description='Red team SDK for Python.',
      author='Jason Callaway',
      author_email='jasoncallaway@fedoraproject.org',
      license='GPLv2',
      url='https://github.com/fedoraredteam/python-sdk',
      download_url='https://github.com/fedoraredteam/python-sdk/archive/0.1.tar.gz',
      keywords=['cve', 'exploit', 'linux', 'red team', 'pen testing'],
      classifiers=[
            'Development Status :: 4 - Beta',
            'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
            'Programming Language :: Python :: 2.7',
      ],
      platforms=['Linux'])