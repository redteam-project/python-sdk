# python-sdk
Fedora Red Team Python SDK

## Examples

See the ```examples``` directory for instructions on how to use the SDK.

```python
# virtualenv redteam
# source redteam/bin/activate
# pip install redteam

from redteam import redteam
r = redteam.RedTeam(debug=True)
sapi = r.SAPI
edb = r.EDB
trello = r.RedTeamTrello
```

Note that if you want your installation to persist, you can specify a non-local cache directory like your home directory.

```python
r = redteam.RedTeam(debug=True, cache_dir='~/.redteam')
```

## Philosophy

Just notes on the development of this SDK
* Re-use: if something's useful for other redteam projects, it probably belongs in the SDK so it can be more easily reused
* Everything has to happen in a virtualenv
  * Pen testers might want to use this SDK during an engagement, so it has to be easy to clean up
* If you have to call out, try to do it only once
  * Then pickle the results, or save them in native format and re-reference