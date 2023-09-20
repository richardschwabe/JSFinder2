<div align="center">
    <h1>JSFinder2</h1>
    <p>Find subdomains and urls in js files</p>

![GitLab last commit](https://img.shields.io/gitlab/last-commit/richardschwabe/JSFinder2)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

</div>

<h1>Table of Contents</h1>

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
  - [Deep check of url](#deep-check-of-url)
  - [Check urls from file](#check-urls-from-file)
  - [Custom User-Agent and Cookies](#custom-user-agent-and-cookies)
  - [Verbose output](#verbose-output)
  - [Results location](#results-location)
- [Todo](#todo)
- [License](#license)
- [Contributing](#contributing)

# Introduction

Rewrite & loosely based on [JSFinder](https://github.com/Threezh1/JSFinder/blob/master/JSFinder.py).

This allows bug bounty hunters to find references, that you might not otherwise find in SSL cert scraping or similar.

Allows to recursively check for subdomains & urls in JS files. i.e.

Open `a.js` finds references to `hub.foo.bar`, opens `hub.foo.bar` and finds `b.js`, checks `b.js` and finds `zoo.foo.bar`, goes to `zoo.foo.bar` etc...

Should be used together with other tools in automation. Though be aware, there might be a lot of false positives URLs. The tool uses regex, which is orginally from [LinkFinder](https://github.com/GerbenJavado/LinkFinder/blob/095bb6218faca9e00169357f663feba0a84202a5/linkfinder.py#L29). (Though [issue 59](https://github.com/GerbenJavado/LinkFinder/issues/59) has been applied.)

Furthermore, a couple of domains are blacklisted, such as:

```python
    "twitter.com",
    "youtube.com",
    "pinterest.com",
    "facebook.com",
    "w3.org",
    "vimeo.com",
    "redditstatic.com",
    "reddit.com",
    "schema.org",
    "unpkg.com",
    "gitter.im",
    "cookielaw.org",
```

Furthermore if any of the following words appear in the url, they will not be saved:

```python
"jquery",
"node_modules"
```

You won't find any of these in the urls.

# Installation

Preferred via pipx

```
pipx install JSFinder2
```

or a simple pip command

```
pip install JSFinder2
```

The pip page is: https://pypi.org/project/JSFinder2/

# Usage

```
python -m jsfinder2 -h
usage: jsfinder2 [-h] [-v] [--debug] [--deep] [-os [OUTPUT_FILE_SUBDOMAINS]] [-ou [OUTPUT_FILE_URLS]] [-c [COOKIE]] [-ua [USER_AGENT]] [-u [REMOTE_JS_FILE_URL] | -f [LOCAL_URL_LIST_FILE]]

Examples:
            jsfinder2 -u https://www.example.com/js/main.js

options:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity (> INFO)
  --debug               sets output to very verbose
  --deep                sets to crawl very deep
  -os [OUTPUT_FILE_SUBDOMAINS], --output-sub [OUTPUT_FILE_SUBDOMAINS]
                        Specify the output file otherwise subdomains.txt is used in ~/jsfinder2
  -ou [OUTPUT_FILE_URLS], --output-url [OUTPUT_FILE_URLS]
                        Specify the output file otherwise urls.txt is used in ~/jsfinder2
  -c [COOKIE], --cookie [COOKIE]
                        Optional Cookie
  -ua [USER_AGENT], --user-agent [USER_AGENT]
                        Optional custom User-Agent
  -u [REMOTE_JS_FILE_URL], --url [REMOTE_JS_FILE_URL]
                        Specify the url to a JS file
  -f [LOCAL_URL_LIST_FILE], --file [LOCAL_URL_LIST_FILE]
                        Specify a local file with URLs

```

## Deep check of url

Follows subdomains and looks for script tags

```
jsfinder2 --deep -u https://www.tesla.com/
```

## Check urls from file

```
jsfinder2 -f myurls.txt
```

## Custom User-Agent and Cookies

To specify the user agent and/or cookie use
`-ua` for the User Agent and `-c` for the Cookie.

## Verbose output

You can use `--debug` to show more developer infos and `-v` for more console output (this might be a lot, as all urls and subdomains are shown!)

## Results location

By default all findings are stored in the home directory of the user in the domains folder i.e.:

```bash
# Linux
cat ~/jsfinder2/tesla.com/urls.txt
cat ~/jsfinder2/tesla.com/subdomains.txt

# Windows
type C:\Users\<USERNAME>\jsfinder2\tesla.com\urls.txt
type C:\Users\<USERNAME>\jsfinder2\tesla.com\subdomains.txt
```

You can adjust the file location via `-os` for subdomains and `-ou` for urls.

# Todo

- [x] create a subfolder for each domain
- [x] add option to load urls from file
- [ ] support flag that url is a js file
- [ ] crawl subdomains for more js files
- [ ] threading ?
- [ ] json output file ?

# License

[MIT](LICENSE)

# Contributing

Feel free to open an issue with any feedback, a PR or similar.

It would also help to star the project!
