import argparse
import itertools
import json
import multiprocessing
import os
import subprocess
import shlex
import logging
import time

import pandas as pd
from utils import curl_program_h3, top_1m_dir, chunk_dir_pattern
from chunk_split import chunk_csv_to_file


def call_curl(url, timeout_second=10):
    # SET THE -WFLAG
    wflag = "-w '\ntime_appconnect: %{time_appconnect}\ntime_connect: %{time_connect}\ntime_namelookup: %{" \
            "time_namelookup}\ntime_pretransfer: %{time_pretransfer}\ntime_redirect: %{" \
            "time_redirect}\ntime_starttransfer: %{time_starttransfer}\ntime_total: %{time_total}\nremote_ip: %{" \
            "remote_ip}\nremote_port: %{remote_port}\nhttp_version: %{http_version}'"
    command = "%s -v %s --http3 --connect-timeout %d --output /dev/null %s --ipv4" % (
        curl_program_h3, url, timeout_second + 5, wflag)
    split_command = shlex.split(command)
    # print(split_command)
    proc = subprocess.Popen(split_command,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = proc.communicate(timeout=timeout_second)
        # print(stderr)
        # print(stdout)
    except subprocess.TimeoutExpired:
        return [None, True]
    return [stdout.decode('utf-8'), False]


print(call_curl('https://www.sohu.com'))

# print(call_curl('https://quic.rocks:4433/'))
