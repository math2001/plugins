import os
import os.path
import urllib3
from concurrent.futures import ThreadPoolExecutor
from base64 import b64encode
from urllib.parse import urljoin

class FetchFavicons:

    def __init__(self, cache_path):
        print("cache path:", cache_path)
        os.makedirs(cache_path)
        self.cache_path = cache_path
        self.thread_pool = ThreadPoolExecutor(5);
        self.connection_manager = urllib3.PoolManager(maxsize=5)
        self.downloading = []
        self.failed_urls = []

    def get_favicon_for_url(self, url):
        """ returns paths to the image from the url if it loaded, or none
        """
        if url in self.failed_urls:
            # we tried once, but it didn't work, so we give up
            print("{!r}: failed url".format(url))
            return None

        filepath = os.path.join(self.cache_path, base64_encode(url))
        if os.path.exists(filepath):
            print("{!r}: return from cache".format(url))
            return filepath

        if url in self.downloading:
            print("{!r}: downlading right now".format(url))
            return None

        self.downloading.append(url)
        self.thread_pool.submit(self.fetch_html, url, self.connection_manager)

    def fetch_html(self, url, manager):
        print('{!r} fetching html'.format(url))
        # download the html
        # find the favicon
        # if we can't find the favicon, add it to failed_urls
        # otherwise download it and save it as a file
        response = manager.request('GET', url)
        if response.status != 200:
            self.failed_urls.append(url)
            print('{!r}: invalid response'.format(url))
            print(response.s)
            return

        try:
            rel_favicon_url = parse_favicon_url(response.data.decode('utf-8'))
        except ValueError as e:
            print('{!r}: failed parsing html {}'.format(url, e))
            return

        abs_favicon_url = urljoin(url, rel_favicon_url)

        print('{!r}: fetching favicon for'.format(url))

        # load the favicon
        response = manager.request('GET', abs_favicon_url)
        if response.status != 200:
            self.failed_urls.append(url)
            return

        print('{!r}: got favicon'.format(url))
        filepath = os.path.join(self.cache_path, base64_encode(url))
        with open(filepath, 'wb') as fp:
            fp.write(response.data) # streams? naah, just read the whole thing

        self.downloading.remove(url)
        print("{!r}: done".format(url))

def parse_favicon_url(content):
    catches = [
        'icon',
        'shortcut icon',
        'apple-touch-icon',
        'apple-touch-icon-precomposed',
    ]

    for line in content.splitlines():
        for catch in catches:
            if 'rel="{}"'.format(catch) not in line \
                and "rel='{}'".format(catch) not in line:
                continue
            index = line.find('href="')
            if index == -1:
                raise ValueError("found link tag, not href")

            start = index + len('href="')
            end = start + 1
            while end < len(line) and line[end] != '"':
                end += 1
            return line[start:end]

        if '</head>' in line:
            raise ValueError('saw end of head, stop searching')

    raise ValueError("searched the whole thing, found nothing")

def base64_encode(string):
    return b64encode(string.encode()).decode('utf-8')

def parse_favicon_url_in_file(filepath):
    with open(filepath) as fp:
        return parse_favicon_url(fp.read())

if __name__ == "__main__":
    # assert parse_favicon_url_in_file("tests/github.html") == "https://github.githubassets.com/favicons/favicon.svg"
    # assert parse_favicon_url_in_file("tests/stack.html") == "https://cdn.sstatic.net/Sites/stackoverflow/Img/favicon.ico?v=ec617d715196"
    # assert parse_favicon_url_in_file("tests/python.html") == "../_static/py.svg"

    # assert urljoin("http://foo.com/bar/baz", "../foobar") == "http://foo.com/foobar"
    # assert urljoin("http://foo.com/bar/baz", "http://bar.com/foobar") == "http://bar.com/foobar"

    f = FetchFavicons("/tmp/foo")
    print(f.get_favicon_for_url("https://github.com/scottwernervt/favicon/blob/master/src/favicon/favicon.py"))
    print(f.get_favicon_for_url("https://urllib3.readthedocs.io/en/stable/user-guide.html"))
    import time; time.sleep(2)
    print(f.get_favicon_for_url("https://github.com/scottwernervt/favicon/blob/master/src/favicon/favicon.py"))
    print(f.get_favicon_for_url("https://urllib3.readthedocs.io/en/stable/user-guide.html"))