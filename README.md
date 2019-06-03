# Weaver - Web Directory Bruteforcer
![python](https://img.shields.io/pypi/pyversions/Django.svg)
![size](https://img.shields.io/github/size/ak-wa/weaver/weaver.py.svg)
![lastcommit](https://img.shields.io/github/last-commit/ak-wa/weaver.svg)
![follow](https://img.shields.io/github/followers/ak-wa.svg?label=Follow&style=social)

![](spider.gif)

* Configurable queue threading
* Progressbar without modules
* 404 Counter
* Adds entries of robots.txt to the wordlist, if existing
* Written as class, can be used in other projects

### Usage:
`python weaver.py <url> <dir_list> <threads>`  
#### example:  
`python weaver.py https://example.com /usr/share/wordlists/dirb/common.txt 30`
