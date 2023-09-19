# Based on https://github.com/Threezh1/JSFinder/blob/master/JSFinder.py

import re
import sys
import argparse

from bs4 import BeautifulSoup

from .utils import exctract_url, get_url, process_url_infos
import jsfinder2.settings as settings


class JSFinder2:
    _parser: argparse.ArgumentParser
    args = None
    config: dict = {
        "url": "",
        "cookie": "",
        "user_agent": "",
        "local_file": "",
        "deep": True,
        "output_files": {
            "urls": "",
            "subdomains": "",
        },
    }

    def setup_folders(self):
        self.debug("Checking for and maybe creating results folder in homedirectory")
        settings.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        # Todo: Create a random name for the project?

    def maybe_print(self, msg):
        if self.args:
            if self.args.verbose:
                print(msg)

    def debug(self, msg):
        if self.args:
            if self.args.debug:
                print(f"[DEBUG] {msg}")

    def setup_args(self):
        main_description = """
        Examples:
            jsfinder2 -f local_js_file.js
            jsfinder2 -u https://www.example.com/js/main.js
"""
        self._parser = argparse.ArgumentParser(
            prog="jsfinder2",
            description=main_description.strip(),
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        self._parser.add_argument(
            "-v",
            "--verbose",
            help="increase output verbosity (> INFO)",
            action="store_true",
        )
        self._parser.add_argument(
            "--debug", help="sets output to very verbose", action="store_true"
        )

        self._parser.add_argument(
            "--deep", help="sets to crawl very deep", action="store_true"
        )

        self._parser.add_argument(
            "-os",
            "--output-sub",
            metavar="OUTPUT_FILE_SUBDOMAINS",
            action="store",
            dest="output_file_subdomains",
            const="",
            nargs="?",
            help="Specify the output file otherwise subdomains.txt is used in ~/jsfinder2",
        )

        self._parser.add_argument(
            "-ou",
            "--output-url",
            metavar="OUTPUT_FILE_URLS",
            action="store",
            dest="output_file_urls",
            const="",
            nargs="?",
            help="Specify the output file otherwise urls.txt is used in ~/jsfinder2",
        )

        self._parser.add_argument(
            "-c",
            "--cookie",
            metavar="COOKIE",
            action="store",
            dest="cookie",
            const="",
            nargs="?",
            help="Optional Cookie",
        )
        self._parser.add_argument(
            "-ua",
            "--user-agent",
            metavar="USER_AGENT",
            action="store",
            dest="user_agent",
            const="",
            nargs="?",
            help="Optional custom User-Agent",
        )

        action_group = self._parser.add_mutually_exclusive_group()
        action_group.title = "action_group"
        action_group.add_argument(
            "-f",
            "--file",
            metavar="LOCAL_JS_FILE_PATH",
            action="store",
            dest="js_file_path",
            const="",
            nargs="?",
            help="Specify the local path to a JS file",
        )
        action_group.add_argument(
            "-u",
            "--url",
            metavar="REMOTE_JS_FILE_URL",
            action="store",
            dest="js_file_url",
            const="",
            nargs="?",
            help="Specify the url to a JS file",
        )

    def work_on_url(self):
        self.debug(f"Working with: {self.config['url']}")

    def work_on_local_file(self):
        self.debug(f"Working with: {self.config['local_file']}")

    def run(self):
        self.setup_folders()
        self.setup_args()
        self.args, _ = self._parser.parse_known_args()
        self.maybe_print("JSFinder2 Starting...")
        self.debug(sys.argv)

        self.config = {
            "url": self.args.js_file_url,
            "cookie": self.args.cookie or "",
            "user_agent": self.args.user_agent or "",
            "local_file": self.args.js_file_path,
            "deep": self.args.deep,
            "output_files": {
                "urls": self.args.output_file_urls or settings.HOME_DIR / "urls.txt",
                "subdomains": self.args.output_file_subdomains
                or settings.HOME_DIR / "subdomains.txt",
            },
        }

        self.debug(self.config)

        if self.config["url"]:
            self.work_on_url()
        elif self.config["local_file"]:
            self.work_on_local_file()
        else:
            print(
                "Exiting. You need to specify either a url or local file path. Use --help for more info!"
            )
            return
