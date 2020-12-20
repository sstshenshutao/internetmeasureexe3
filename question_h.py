import json
import logging
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests

import pandas as pd
import multiprocessing
import subprocess
from utils import question_f_output_dir, question_f_top_1k_csv, question_h_output_dir
from chunk_split import chunk_csv_to_file
from curl_call import clean_logger, init_logger, summary_result
from shutil import copyfile


def start_driver(mode='h3'):
    chrome_options = Options()
    # allow to run with root
    chrome_options.add_argument('--no-sandbox')
    # no GUI
    chrome_options.add_argument('--headless')
    # quic
    if mode == 'h3':
        chrome_options.add_argument('--enable-quic')
        chrome_options.add_argument('--quic-version=h3-29')
        chrome_options.add_argument('--origin-to-force-quic-on=*')
    else:
        chrome_options.add_argument('--disable-quic')
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def visit(driver, url, all_loggers):
    ret_obj = {
        "website": url,
        "responseStart": None,
        "domInteractive": None,
        "domComplete": None,
        "nextHopProtocol": None,
    }
    # get the loggers for using
    output_logger = all_loggers["output"]
    # timeout_logger = all_loggers["timeout"]
    try:
        driver.get(url)
    except Exception:
        print("exception: " % url)
        output_logger.info("%s" % (json.dumps(ret_obj, sort_keys=True, indent=4)))
        return ret_obj
    navigation = driver.execute_script("return performance.getEntriesByType('navigation')")
    ret_obj = {
        "website": url,
        "responseStart": navigation[0]['responseStart'],
        "domInteractive": navigation[0]['domInteractive'],
        "domComplete": navigation[0]['domComplete'],
        "nextHopProtocol": navigation[0]['nextHopProtocol']
    }
    output_logger.info("%s" % (json.dumps(ret_obj, sort_keys=True, indent=4)))
    return ret_obj


def visit_worker(some_dir, filename, chunk_index, chunk_thread_pattern="chunk_thread_%d", mode='h3'):
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

    # visit all websites
    # start a driver
    driver = start_driver(mode=mode)

    # do the visit
    visit_result_df = source_df['website'].apply(lambda web: pd.Series(visit(driver, web, all_loggers_)))

    # merge the result with df
    source_df = source_df.merge(visit_result_df, left_on='website', right_on='website')

    # remove the driver
    driver.quit()

    source_df.to_csv(chunk_output, index=False)


def multiprocess_visit(filename, chunk_dir, chunksize_thread, chunk_thread_pattern, summary_dist="summary.csv",
                       mode='h3'):
    # split_csv
    csv_file_size = chunk_csv_to_file(chunksize_thread, filename, chunk_dir,
                                      chunk_dir_pattern_=chunk_thread_pattern)
    print("use threads: %d" % csv_file_size)
    # multiprocessing call curl
    jobs = []
    # test the time
    start_time = time.time()
    for i in range(csv_file_size):
        p = multiprocessing.Process(target=visit_worker, args=(chunk_dir, filename, i, chunk_thread_pattern, mode))
        jobs.append(p)
        p.start()
    for p in jobs:
        p.join()
    # summary the result:
    summary_result(chunk_dir, filename, csv_file_size, dist=summary_dist, chunk_thread_pattern=chunk_thread_pattern)
    print("used time: %f" % (time.time() - start_time))


def chrome_do_visit(mode='h3'):
    # # load_1k
    # top_1k_df = pd.read_csv(os.path.join(question_h_output_dir, question_f_top_1k_csv), index_col=0)
    # print(top_1k_df, top_1k_df['website'].size)
    tmp_dir = os.path.join(question_h_output_dir, 'tmp')
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    arg_filename = 'chunk.csv'
    copyfile(os.path.join(question_f_output_dir, question_f_top_1k_csv), os.path.join(tmp_dir, arg_filename))
    arg_dir = tmp_dir
    arg_chunksize_thread = 100
    chunk_thread_pattern_ = "chunk_thread_%d"
    multiprocess_visit(arg_filename, arg_dir, arg_chunksize_thread, chunk_thread_pattern_,
                       summary_dist='summary_chrome_%s.csv' % mode, mode=mode)


if __name__ == '__main__':
    if not os.path.exists(question_h_output_dir):
        os.mkdir(question_h_output_dir)
    chrome_do_visit(mode='h3')
    chrome_do_visit(mode='h2')

    domain_df = pd.read_csv(os.path.join(question_h_output_dir, 'tmp', 'chunk.csv'), header=None, index_col=0,
                            names=["no", "domain name"], )
    chrome_h2_df = pd.read_csv(os.path.join(question_h_output_dir, 'tmp', 'summary_chrome_h2.csv'), index_col=0)
    chrome_h3_df = pd.read_csv(os.path.join(question_h_output_dir, 'tmp', 'summary_chrome_h3.csv'), index_col=0)
    chrome_h2_df.merge(domain_df, left_index=True, right_index=True)[[
        "domain name", "responseStart", "domInteractive", "domComplete"]].to_csv(
        os.path.join(question_h_output_dir, 'summary_chrome_h2.csv'), index=False)
    chrome_h3_df.merge(domain_df, left_index=True, right_index=True)[[
        "domain name", "responseStart", "domInteractive", "domComplete"]].to_csv(
        os.path.join(question_h_output_dir, 'summary_chrome_h3.csv'), index=False)
