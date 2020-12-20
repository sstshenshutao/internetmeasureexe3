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


def clean_logger(log_setting, working_dir):
    for name, _ in log_setting:
        log_name = os.path.join(working_dir, '%s.log' % name)
        if os.path.isfile(log_name):
            os.remove(log_name)


def init_logger(log_setting, working_dir):
    ret_loggers = {}
    for name, level in log_setting:
        # create logger for "name"
        logger = logging.getLogger(name)
        logger.setLevel(level)
        # create file handler which logs even debug messages
        fh = logging.FileHandler(os.path.join(working_dir, '%s.log' % name))
        fh.setLevel(level)
        logger.addHandler(fh)
        ret_loggers[name] = logger
    return ret_loggers


def call_curl(url, timeout_second=10):
    # SET THE -WFLAG
    wflag = "-w '\ntime_appconnect: %{time_appconnect}\ntime_connect: %{time_connect}\ntime_namelookup: %{" \
            "time_namelookup}\ntime_pretransfer: %{time_pretransfer}\ntime_redirect: %{" \
            "time_redirect}\ntime_starttransfer: %{time_starttransfer}\ntime_total: %{time_total}\nremote_ip: %{" \
            "remote_ip}\nremote_port: %{remote_port}\nhttp_version: %{http_version}\n'"
    command = "%s -s %s --http3 --connect-timeout %d --output /dev/null %s --ipv4" % (
        curl_program_h3, url, timeout_second + 5, wflag)
    split_command = shlex.split(command)
    # print(split_command)
    proc = subprocess.Popen(split_command,
                            stdout=subprocess.PIPE)
    try:
        stdout, _ = proc.communicate(timeout=timeout_second)
    except subprocess.TimeoutExpired:
        return [None, True]
    return [stdout.decode('utf-8'), False]


def parse_curl_return(ret_str, err, all_loggers, log_url=''):
    ret_object = {
        'website': log_url,
        "status": None,
        "remote_ip": None,
        "remote_port": None,
        "time_appconnect": None,
        "time_connect": None,
        "time_namelookup": None,
        "time_pretransfer": None,
        "time_redirect": None,
        "time_starttransfer": None,
        "time_total": None
    }
    # get the loggers for using
    output_logger = all_loggers["output"]
    timeout_logger = all_loggers["timeout"]
    # timeout:
    if err:
        timeout_logger.warning("timeout: %s" % log_url)
        ret_object['status'] = 'timeout'
        return ret_object
    # connection refused:
    if len(ret_str) == 0:
        timeout_logger.warning("connection refused: %s" % log_url)
        ret_object['status'] = 'connection refused'
        return ret_object
    # parse the returned header
    str_list = ret_str.split('\n')
    str_list = list(itertools.dropwhile(lambda x: not x.startswith('time_appconnect:'), str_list))
    str_list = list(filter(lambda x: len(x.strip()) != 0, str_list))
    for line in str_list:
        key_value = line.split(': ')
        if key_value[0] == 'http_version':
            # check if the version is 3
            if key_value[1] != '3':
                ret_object['status'] = 'error'
            else:
                ret_object['status'] = 'ok'
        else:
            ret_object[key_value[0]] = key_value[1]

    # log the json to output_logger
    output_logger.info("%s: %s" % (log_url, json.dumps(ret_object, sort_keys=True, indent=4)))
    return ret_object


def curl_one(url, all_loggers):
    print("doing: %s " % url)
    return parse_curl_return(*call_curl(url), all_loggers, log_url=url)


def init_argparse():
    parser = argparse.ArgumentParser(description='curl_call')
    parser.add_argument('--filename', metavar='filename', type=str, nargs='?',
                        help='filename')
    parser.add_argument('--machine_index', metavar='machine_index', type=int, nargs='?',
                        help='machine_index')
    parser.add_argument('--chunksize_thread', metavar='chunksize_thread', type=int, nargs='?',
                        help='chunksize_thread')
    return parser.parse_args()


def curl_worker(some_dir, filename, chunk_index, chunk_thread_pattern="chunk_thread_%d"):
    working_dir = os.path.join(some_dir, chunk_thread_pattern % chunk_index)
    # the log_setting:
    logs = [
        ("output", logging.INFO),
        ("timeout", logging.WARNING)
    ]
    # del the log file
    clean_logger(logs, working_dir)
    # init the logs:
    all_loggers_ = init_logger(logs, working_dir)

    # prepare input and output
    chunk_input = os.path.join(working_dir, filename)
    chunk_output = os.path.join(working_dir, "out_%s" % filename)
    # preprocess the csv to website
    source_df = pd.read_csv(chunk_input, header=None, names=["no", "website"])
    source_df['website'] = source_df['website'].apply(
        lambda x: 'https://www.%s' % x if not x.startswith('www.') else 'https://%s' % x)
    # curl all websites
    curl_result_df = source_df['website'].apply(lambda web: pd.Series(curl_one(web, all_loggers_)))
    source_df = source_df.merge(curl_result_df, left_on='website', right_on='website')
    source_df.to_csv(chunk_output, index=False)


def summary_result(some_dir, filename, csv_file_size, dist="summary.csv", chunk_thread_pattern="chunk_thread_%d"):
    frames = [
        pd.read_csv(os.path.join(some_dir, chunk_thread_pattern % chunk_index, "out_%s" % filename), index_col=0)
        for chunk_index in range(csv_file_size)
    ]
    pd.concat(frames).to_csv(os.path.join(some_dir, dist))


def multiprocess_chunk_one(filename, chunk_dir, chunksize_thread, chunk_thread_pattern, summary_dist="summary.csv"):
    # split_csv
    csv_file_size = chunk_csv_to_file(chunksize_thread, filename, chunk_dir,
                                      chunk_dir_pattern_=chunk_thread_pattern)
    print("use threads: %d" % csv_file_size)
    # multiprocessing call curl
    jobs = []
    # test the time
    start_time = time.time()
    for i in range(csv_file_size):
        p = multiprocessing.Process(target=curl_worker, args=(chunk_dir, filename, i, chunk_thread_pattern))
        jobs.append(p)
        p.start()
    for p in jobs:
        p.join()
    # summary the result:
    summary_result(chunk_dir, filename, csv_file_size, dist=summary_dist, chunk_thread_pattern=chunk_thread_pattern)
    print("used time: %f" % (time.time() - start_time))


# python curl_call.py --filename="chunk.csv" --chunksize_thread=100 --machine_index=0
if __name__ == '__main__':
    args = init_argparse()
    arg_filename = args.filename
    arg_machine_index = args.machine_index
    arg_chunksize_thread = args.chunksize_thread
    arg_dir = os.path.join(top_1m_dir, chunk_dir_pattern % arg_machine_index)
    chunk_thread_pattern_ = "chunk_thread_%d"
    multiprocess_chunk_one(arg_filename, arg_dir, arg_chunksize_thread, chunk_thread_pattern_,
                           summary_dist="summary_%d.csv" % arg_machine_index)
