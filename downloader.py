import argparse
import calendar
import datetime
import os
import sys

import requests
import urllib3


class Downloader:

    @classmethod
    def download_file(cls, url, dist_dir):
        file_name = os.path.basename(url)
        with open(os.path.join(dist_dir, file_name), "wb") as f:
            response = requests.get(url, stream=True)
            content_length = response.headers.get('content-length')
            if content_length is None:  # no content length header
                print("no content length header")
                f.write(response.content)
            else:
                finished = 0
                content_length = int(content_length)
                for data in response.iter_content(chunk_size=4096):
                    finished += len(data)
                    f.write(data)
                    done = int(20 * finished / content_length)
                    sys.stdout.write(
                        "\r Downloading %s: %d%% [%s%s] %d/%d" % (file_name,
                                                                  float(finished) / float(content_length) * 100,
                                                                  '=' * done, ' ' * (20 - done), finished,
                                                                  content_length))
                    sys.stdout.flush()
        print("\r Downloading %s ... ok" % file_name)


def init_argparse():
    parser = argparse.ArgumentParser(description='question_b')
    parser.add_argument('--url', metavar='url', type=str, nargs='?',
                        help='download url')
    parser.add_argument('--dist_dir', metavar='dist_dir', type=str, nargs='?',
                        help='download dist_dir')
    return parser.parse_args()


if __name__ == '__main__':
    args = init_argparse()
    arg_url = args.url
    arg_dist_dir = args.dist_dir
    # set some cipher => for this web
    requests.packages.urllib3.disable_warnings()
    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
    try:
        requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
    except AttributeError:
        # no pyopenssl support used / needed / available
        pass
    # download
    Downloader.download_file(arg_url, arg_dist_dir)
