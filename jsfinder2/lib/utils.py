import pathlib
import re
from urllib.parse import urlparse

import httpx


# Regular expression comes from https://github.com/GerbenJavado/LinkFinder
def exctract_url(javascript_code: str):
    regex_str = r"""
  (?:"|')                               # Start newline delimiter

  (
    ((?:[a-zA-Z]{1,10}://|//)           # Match a scheme [a-Z]*1-10 or //
    [^"'/]{1,}\.                        # Match a domainname (any character + dot)
    [a-zA-Z]{2,}[^"']{0,})              # The domainextension and/or path

    |

    ((?:/|\.\./|\./)                    # Start with /,../,./
    [^"'><,;| *()(%%$^/\\\[\]]          # Next character can't be...
    [^"'><,;|()]{1,})                   # Rest of the characters can't be

    |

    ([a-zA-Z0-9_\-/]{1,}/               # Relative endpoint with /
    [a-zA-Z0-9_\-/]{1,}                 # Resource name
    \.(?:[a-zA-Z]{1,4}|action)          # Rest + extension (length 1-4 or action)
    (?:[\?|#][^"|']{0,}|))              # ? or # mark with parameters

    |

    ([a-zA-Z0-9_\-/]{1,}/               # REST API (no extension) with /
    [a-zA-Z0-9_\-/]{3,}                 # Proper REST endpoints usually have 3+ chars
    (?:[\?|#][^"|']{0,}|))              # ? or # mark with parameters

    |

    ([a-zA-Z0-9_\-.]{1,}                 # filename
    \.(?:php|asp|aspx|jsp|json|
         action|html|js|txt|xml)        # . + extension
    (?:[\?|#][^"|']{0,}|))              # ? or # mark with parameters

  )

  (?:"|')                               # End newline delimiter

"""
    javascript_code = javascript_code.replace(";", ";\r\n").replace(",", ",\r\n")
    pattern = re.compile(regex_str, re.VERBOSE)
    result = re.finditer(pattern, javascript_code)
    if result == None:
        return None
    js_url = []
    return [
        match.group().strip('"').strip("'")
        for match in result
        if match.group() not in js_url
    ]


def get_url(
    url: str,
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36",
    cookie: str = "",
) -> str:
    """Returns the body of a URL or an empty string

    Args:
        url (str): URL
        user_agent (str, optional): Possible Custom User-Agent. Defaults to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36".
        cookie (str, optional): Cookie. Defaults to "".

    Returns:
        str: body of url
    """
    try:
        headers = {"User-Agent": user_agent}
        if cookie:
            headers.update({"Cookie": cookie})

        r = httpx.get(url, headers=headers, timeout=10.0, follow_redirects=True)

        return r.text
    except Exception as e:
        print(e)
        return ""


def process_url_infos(original_url: str, found_url: str) -> str:
    """Processes a URL and returns a full url with protoctol, host and full path

    Args:
        original_url (str): _description_
        found_url (str): Might be a relative URL

    Returns:
        str: Full URL
    """
    blacklisted = ["javascript:"]

    url_data = urlparse(original_url)

    network_location = url_data.netloc
    protocol = url_data.scheme
    if not found_url:
        return ""

    if found_url[:2] == "//":
        result = f"{protocol}:{found_url}"
    elif found_url[:4] == "http":
        result = found_url
    elif found_url[:2] == "ws":
        result = found_url
    elif found_url[:3] == "ftp":
        result = found_url
    elif found_url[:2] != "//" and found_url not in blacklisted:
        if found_url[:1] == "/":
            result = f"{protocol}://{network_location}{found_url}"
        else:
            if found_url[:1] == ".":
                if found_url[:2] == "..":
                    result = f"{protocol}://{network_location}{found_url[2:]}"
                else:
                    result = f"{protocol}://{network_location}{found_url[1:]}"
            else:
                result = f"{protocol}://{network_location}/{found_url}"
    else:
        result = original_url
    return result
