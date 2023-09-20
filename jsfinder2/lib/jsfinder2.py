import sys
import argparse

from bs4 import BeautifulSoup
import tldextract

from .utils import exctract_url, get_url, process_url_infos
import jsfinder2.settings as settings


class JSFinder2:
    _parser: argparse.ArgumentParser
    args = None
    config: dict = {
        "url": "",
        "cookie": "",
        "user_agent": "",
        "output_files": {
            "urls": "",
            "subdomains": "",
        },
    }

    blacklisted_domains = [
        "twitter.com",
        "youtube.com",
        "pinterest.com",
        "facebook.com",
        "w3.org",
        "vimeo.com",
        "redditstatic.com",
        "reddit.com",
        "schema.org",
    ]

    blacklisted_words = ["jquery.js", "node_modules"]

    all_urls = list()
    all_subdomains = list()

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
        # get the url data
        html_body = get_url(self.config["url"])
        if not html_body:
            msg = f"Cannot get HTML Body! for {self.config['url']}"
            raise Exception(msg)
        # parse in bs4
        soup = BeautifulSoup(html_body, "html.parser")
        # find all the script tags
        html_scripts = soup.findAll("script")
        # parse all the src attributes
        scripts_links = list()
        for html_script in html_scripts:
            script_src = html_script.get("src")
            processed_url = process_url_infos(self.config["url"], script_src)
            if not processed_url:
                continue

            # check if we have some useless urls, like jquery.js or node_module reference
            ignore = False
            for blacklist_item in self.blacklisted_words:
                if blacklist_item in processed_url:
                    ignore = True
                    break
            if ignore:
                continue

            if processed_url not in self.all_urls:
                self._add_url_result(processed_url)
                scripts_links.append(processed_url)

        for script_url in scripts_links:
            temporary_urls = exctract_url(get_url(script_url))
            if not temporary_urls:
                continue
            for url in temporary_urls:
                self._add_url_result(process_url_infos(script_url, url))

        # extract subdomains
        self._analyse_subdomains()

    def _add_url_result(self, url):
        domain = ".".join(tldextract.extract(url)[1:])
        if domain in self.blacklisted_domains:
            return

        if url not in self.all_urls:
            self.all_urls.append(url)

    def _analyse_subdomains(self):
        """Goes over the added urls and finds subdomains"""
        original_domain = ".".join(tldextract.extract(self.config["url"])[1:])
        for url in self.all_urls:
            url_data = tldextract.extract(url)
            full_subdomain = ".".join(url_data)
            if full_subdomain[:1] == ".":
                full_subdomain = full_subdomain[1:]
            if (
                full_subdomain not in self.all_subdomains
                and original_domain in full_subdomain
            ):
                self.all_subdomains.append(full_subdomain)

    def run(self):
        self.setup_folders()
        self.setup_args()
        self.args, _ = self._parser.parse_known_args()
        self.maybe_print("JSFinder2 Starting...")
        self.debug(sys.argv)

        original_domain = ".".join(tldextract.extract(self.args.js_file_url)[1:])
        project_path = settings.RESULTS_DIR / original_domain
        project_path.mkdir(parents=True, exist_ok=True)

        self.config = {
            "url": self.args.js_file_url,
            "cookie": self.args.cookie or "",
            "user_agent": self.args.user_agent or "",
            "output_files": {
                "urls": self.args.output_file_urls or project_path / "urls.txt",
                "subdomains": self.args.output_file_subdomains
                or project_path / "subdomains.txt",
            },
        }

        self.debug(self.config)

        if self.config["url"]:
            self.work_on_url()
        else:
            print("Exiting. You need to specify a url.Use --help for more info!")
            return

        # Write files
        with open(self.config["output_files"]["urls"], mode="w") as url_file:
            for url in self.all_urls:
                print(url)
                url_file.write(url + "\n")

        with open(
            self.config["output_files"]["subdomains"], mode="w"
        ) as subdomain_file:
            for subdomain in self.all_subdomains:
                print(subdomain)
                subdomain_file.write(url + "\n")

        # print summary
        print(f"Found {len(self.all_urls)} URLS:")
        print(f"Found {len(self.all_subdomains)} Subdomains:")
