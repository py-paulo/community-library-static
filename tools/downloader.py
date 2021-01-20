import re
import os
import sys
import glob
import pathlib
import logging
import datetime
import urllib.request

from typing import List, Tuple, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


BASE_DIR = pathlib.Path(__file__).parent

DEBUG_CUSTOM_LOG = 'log-debug.txt'

BASE_WEB_SERVER = 'http://localhost:5000/'

DIR_JS = BASE_DIR / '..' / 'web' / 'dist' / 'js'
DIR_CSS = BASE_DIR / '..' / 'web' / 'dist' / 'css'

if not DIR_JS.is_dir():
    sys.exit('err... not found dir %s' % DIR_JS)

if not DIR_CSS.is_dir():
    sys.exit('err... not found dir %s' % DIR_CSS)


def log_debug(msg: str) -> None:
    with open(DEBUG_CUSTOM_LOG, 'a+') as fp:
        fp.write('[%s] %s\n' % (datetime.datetime.now(), msg))


def downloader(ext: str, line: str, debug: bool = True) -> List[Tuple[bool, Any]]:
    pattern = r'src=[\'"]?([^\'" >]+)' if ext == '.js' else r'href=[\'"]?([^\'" >]+)'
    urls = re.findall(pattern, line)

    if not urls:
        return [(False, '')]

    results = []

    for url in urls:
        err_flag = 0

        if not (ext in url):
            continue

        if debug:
            log_debug('%s try download %s' % (ext, url))

        nurl = url
        if '?ver=' in url:
            nurl = url.split('?')[:-1][0]

        tmp_file_name = DIR_CSS / nurl.split('/')[-1] if \
            ext == '.css' else \
        DIR_JS / nurl.split('/')[-1]

        if tmp_file_name.exists():
            os.remove(tmp_file_name.absolute().__str__())

        with open(tmp_file_name, 'a+') as fp:

            if url.startswith('//'):
                url = 'http:' + url

            req = urllib.request.Request(url)
            try:
                with urllib.request.urlopen(req) as response:
                    fp.write(response.read().decode('utf-8'))
            except urllib.error.HTTPError as err:
                logger.error('Err... as download file "%s". %s' % (url, err))
                err_flag = 1
                results.append((False, tmp_file_name.__str__()))
            else:
                logger.info('Download (%s) file %s' % (ext, url))
                results.append((True, (tmp_file_name.__str__(), url)))

        if err_flag == 1:
            os.remove(tmp_file_name.absolute().__str__())

        return results


if __name__ == '__main__':
    htdocs_dir = BASE_DIR / 'htdocs'

    htmls = glob.glob(htdocs_dir.absolute().__str__() + '/*.html')

    for html in htmls:
        tmp_html_file_name = BASE_DIR / 'htdocs' / html.split('/')[-1].replace('raw-', '')

        if tmp_html_file_name.exists():
            os.remove(tmp_html_file_name.absolute().__str__())

        with open(tmp_html_file_name, 'a+') as nfp:
            html_text = open(html).read()
            with open(html) as fp:
                for line in fp.readlines():
                    results = downloader('.css', line)
                    results = [] if results is None else results
                    for result in results:
                        if not result[0]:
                            continue

                        if results[0]:
                            html_text = html_text.replace(
                                result[1][1],
                                BASE_WEB_SERVER + result[1][0].replace('web/', '').replace('../', '').replace('dist/', ''))

                    results = downloader('.js', line)
                    results = [] if results is None else results
                    for result in results:
                        if not result[0]:
                            continue

                        if results[0]:
                            html_text = html_text.replace(
                                result[1][1],
                                BASE_WEB_SERVER + result[1][0].replace('web/', '').replace('../', '').replace('dist/', ''))

            nfp.write(html_text)
