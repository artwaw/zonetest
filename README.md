## ZONETEST(.py)

Simple tool for testing if DNS zone has been migrated successfully.

#Requirements:
- Python 3.x (it may run on 2.x after some corrections, I don't intend to test it)
- dnspython python3 module
- argparse python3 module (this is default package but still worth mentioning)
- ipaddress python3 module (as above)

#Parameters:
./zonetest.py zonefile targetNS [--coma] [--sub filename]

- zonefile - DNS zone as downloaded from the "old" server. Assumed Bind RFC compat.
- targetNS - our "new" name server onto which the zone has been migrated. Can be IP or URL.
- --coma - optional switch allowing to parse csv files (default format is TAB separated)
- --sub filename - use additional nameservers to query for selected subdomains.
					File can be any text file, content should be formatted one subdomain per file:
					subdomain:nameserver
					Nameserver can be IP or URL. 

#Troubleshooting

1) Script complains about missing dnspython

Do `pip3 install dnspython`.
Do not do pip3 as a root!

2) pip3 fails with `ModuleNotFoundError: No module named 'pip._internal.cli.main'` or similar

You are likely running system that provides Python without pip. There are some ways this can be corrected
but the most recommended is via [pyenv](https://github.com/pyenv/pyenv) (this can be also done via Homebrew,
please read the link!) 

After installing pyenv just:

`pyenv install [version]` - i.e. `pyenv install 3.9.0`
`pyenv shell 3.9.0`

All is in the docs.

Further reading on python versions management:

https://opensource.com/article/19/5/python-3-default-mac

