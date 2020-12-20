import argparse
import os
import time

import pandas as pd
import multiprocessing
import subprocess
from utils import question_c_output_dir, question_c_intermediate_csv, question_f_top_1k_csv, \
    question_f_output_dir, curl_program_h2, top_1k_h3_csv, top_1k_h2_csv, top_1k_h2_fail_csv, question_f_lim8, \
    question_f_lim1
from shutil import copyfile
from curl_call import clean_logger, init_logger, summary_result
import shlex
import itertools
import json
import logging
from chunk_split import chunk_csv_to_file
import matplotlib.pyplot as plt
from question_e import support_h3


def extract_top_1k():
    source_df = pd.read_csv(os.path.join(question_c_output_dir, question_c_intermediate_csv))
    source_df[source_df['status'] == 'ok'].head(n=1000).to_csv(
        os.path.join(question_f_output_dir, top_1k_h3_csv), index=False)
    source_df[source_df['status'] == 'ok'][['no', 'domain name']].head(n=1000).to_csv(
        os.path.join(question_f_output_dir, question_f_top_1k_csv), header=None, index=False)


def curl_h2():
    tmp_dir = os.path.join(question_f_output_dir, 'tmp')
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    arg_filename = 'chunk.csv'
    copyfile(os.path.join(question_f_output_dir, question_f_top_1k_csv), os.path.join(tmp_dir, arg_filename))
    arg_dir = tmp_dir
    arg_chunksize_thread = 100
    chunk_thread_pattern_ = "chunk_thread_%d"
    multiprocess_chunk_one_h2(arg_filename, arg_dir, arg_chunksize_thread, chunk_thread_pattern_,
                              summary_dist='summary_h2.csv')


def call_curl_h2(url, timeout_second=10):
    # SET THE -WFLAG
    wflag = "-w '\ntime_appconnect: %{time_appconnect}\ntime_connect: %{time_connect}\ntime_namelookup: %{" \
            "time_namelookup}\ntime_pretransfer: %{time_pretransfer}\ntime_redirect: %{" \
            "time_redirect}\ntime_starttransfer: %{time_starttransfer}\ntime_total: %{time_total}\nremote_ip: %{" \
            "remote_ip}\nremote_port: %{remote_port}\nhttp_version: %{http_version}\n'"
    command = "%s -s %s --http2 --connect-timeout %d --output /dev/null %s --ipv4" % (
        curl_program_h2, url, timeout_second + 5, wflag)
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
        "http_version": None,
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
            # check if the version is 0
            if key_value[1] == '0':
                ret_object['status'] = 'error'
            else:
                ret_object['status'] = 'ok'
        ret_object[key_value[0]] = key_value[1]
    # log the json to output_logger
    output_logger.info("%s: %s" % (log_url, json.dumps(ret_object, sort_keys=True, indent=4)))
    return ret_object


def curl_one_h2(url, all_loggers):
    print("doing: %s " % url)
    return parse_curl_return(*call_curl_h2(url), all_loggers, log_url=url)


def init_argparse():
    parser = argparse.ArgumentParser(description='curl_call')
    parser.add_argument('--filename', metavar='filename', type=str, nargs='?',
                        help='filename')
    parser.add_argument('--chunksize_thread', metavar='chunksize_thread', type=int, nargs='?',
                        help='chunksize_thread')
    return parser.parse_args()


def curl_worker_h2(some_dir, filename, chunk_index, chunk_thread_pattern="chunk_thread_%d"):
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
    curl_result_df = source_df['website'].apply(lambda web: pd.Series(curl_one_h2(web, all_loggers_)))
    source_df = source_df.merge(curl_result_df, left_on='website', right_on='website')
    source_df.to_csv(chunk_output, index=False)


def multiprocess_chunk_one_h2(filename, chunk_dir, chunksize_thread, chunk_thread_pattern, summary_dist="summary.csv"):
    # split_csv
    csv_file_size = chunk_csv_to_file(chunksize_thread, filename, chunk_dir,
                                      chunk_dir_pattern_=chunk_thread_pattern)
    print("use threads: %d" % csv_file_size)
    # multiprocessing call curl
    jobs = []
    # test the time
    start_time = time.time()
    for i in range(csv_file_size):
        p = multiprocessing.Process(target=curl_worker_h2, args=(chunk_dir, filename, i, chunk_thread_pattern))
        jobs.append(p)
        p.start()
    for p in jobs:
        p.join()
    # summary the result:
    summary_result(chunk_dir, filename, csv_file_size, dist=summary_dist, chunk_thread_pattern=chunk_thread_pattern)
    print("used time: %f" % (time.time() - start_time))


def label_resolve_error():
    curl_result_df = pd.read_csv(os.path.join(question_f_output_dir, 'tmp', 'summary_h2.csv'), index_col=0).sort_index(
        axis=0)
    # deal with the "resolve host error"
    curl_result_df.loc[
        (curl_result_df['status'] == 'ok') & (curl_result_df['remote_ip'].isna()), [
            'status',
            'http_version',
            "remote_port",
            "time_appconnect",
            "time_connect",
            "time_namelookup",
            "time_pretransfer",
            "time_redirect",
            "time_starttransfer",
            "time_total"
        ]] = [
        'resolve host error',
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None
    ]

    # remove h1.1 and ssl failed entries
    curl_result_df_ok = curl_result_df[curl_result_df['http_version'] == 2]
    curl_result_df_ok.to_csv(
        os.path.join(question_f_output_dir, top_1k_h2_csv))
    # print(curl_result_df)
    print(
        "The top 1k h3-websites, some webs failed with http/2 or return http/1.1, only %d support h2" %
        curl_result_df_ok[
            'http_version'].size)
    curl_result_df_fail = curl_result_df[curl_result_df['http_version'] != 2]
    curl_result_df_fail.to_csv(
        os.path.join(question_f_output_dir, top_1k_h2_fail_csv))


def plot_difference():
    # calculate h3
    source_df = pd.read_csv(os.path.join(question_c_output_dir, question_c_intermediate_csv))
    h3_1k_df = support_h3(source_df)
    # |---DNS---||---QUIC--||--C--|----Transfer---|   the whole sequence process
    h3_1k_df['DNS Lookup\n H3'] = h3_1k_df['time_namelookup']
    h3_1k_df['QUIC\n H3'] = h3_1k_df['time_connect'] - h3_1k_df['time_namelookup']
    h3_1k_df['Compute\n H3'] = h3_1k_df['time_starttransfer'] - h3_1k_df['time_pretransfer']
    h3_1k_df['Transfer\n H3'] = h3_1k_df['time_total'] - h3_1k_df['time_starttransfer']
    h3_1k_df['Total Time\n H3'] = h3_1k_df['time_total']
    h3_1k_df = h3_1k_df[['no', 'DNS Lookup\n H3', 'QUIC\n H3', 'Compute\n H3', 'Transfer\n H3', 'Total Time\n H3']]

    # calculate h2
    source_df_h2 = pd.read_csv(os.path.join(question_f_output_dir, top_1k_h2_csv))
    # |---DNS---||---QUIC--||--C--|----Transfer---|   the whole sequence process
    source_df_h2['DNS Lookup\n H2'] = source_df_h2['time_namelookup']
    source_df_h2['TCP TLS\n H2'] = source_df_h2['time_connect'] - source_df_h2['time_namelookup']
    source_df_h2['Compute\n H2'] = source_df_h2['time_starttransfer'] - source_df_h2['time_pretransfer']
    source_df_h2['Transfer\n H2'] = source_df_h2['time_total'] - source_df_h2['time_starttransfer']
    source_df_h2['Total Time\n H2'] = source_df_h2['time_total']
    source_df_h2 = source_df_h2[
        ['no', 'DNS Lookup\n H2', 'TCP TLS\n H2', 'Compute\n H2', 'Transfer\n H2', 'Total Time\n H2']]
    # merge them
    h3_1k_df = h3_1k_df.merge(source_df_h2, left_on='no', right_on='no')
    # plot
    _, ax = plt.subplots(figsize=(12, 5))
    boxplot = h3_1k_df.boxplot(ax=ax, column=['DNS Lookup\n H3', 'DNS Lookup\n H2', 'QUIC\n H3', 'TCP TLS\n H2',
                                              'Compute\n H3',
                                              'Compute\n H2', 'Transfer\n H3', 'Transfer\n H2', 'Total Time\n H3',
                                              'Total Time\n H2'])
    plt.savefig(os.path.join(question_f_output_dir, question_f_lim8), dpi=300)
    ax.set_ylim(top=1)
    plt.savefig(os.path.join(question_f_output_dir, question_f_lim1), dpi=300)


if __name__ == '__main__':
    if not os.path.exists(question_f_output_dir):
        os.mkdir(question_f_output_dir)
    extract_top_1k()
    curl_h2()
    label_resolve_error()
    plot_difference()
