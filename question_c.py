# we use the google cloud for parallel computing (but here in this file, we only use one machine)
import os

from utils import first_10k, top_1m_dir, top_1m_filename, top_1m_csv, chunk_dir_pattern, question_c_output_csv, \
    question_c_output_dir, question_c_intermediate_csv, add_units
from chunk_split import chunk_csv_to_file
from curl_call import multiprocess_chunk_one
import pandas as pd


def summary_all(summary_file_size):
    frames = [
        pd.read_csv(os.path.join(top_1m_dir, chunk_dir_pattern % index, 'summary_%d.csv' % index), index_col=0)
        for index in range(summary_file_size)
    ]
    pd.concat(frames).to_csv(os.path.join(top_1m_dir, 'all_summary.csv'))


def output():
    curl_result_df = pd.read_csv(os.path.join(top_1m_dir, 'all_summary.csv'), index_col=0).sort_index(axis=0)

    # change port type >> int if possible
    curl_result_df["remote_port"] = curl_result_df["remote_port"].astype('Int32')

    # merge with the original df to get the domain name (forget to save this column)
    source_dfs = pd.read_csv(os.path.join(top_1m_dir, top_1m_filename), header=None, index_col=0,
                             names=["no", "domain name"],
                             chunksize=10000)
    df = None
    for sdf in source_dfs:
        df = sdf
        break
    curl_result_df = df.merge(curl_result_df, left_index=True, right_index=True)

    # deal with the "resolve host error"
    curl_result_df.loc[
        (curl_result_df['status'] == 'ok') & (curl_result_df['remote_ip'].isna()), [
            'status',
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
        None
    ]

    # save the intermediate_csv
    if not os.path.exists(question_c_output_dir):
        os.mkdir(question_c_output_dir)
    curl_result_df.to_csv(os.path.join(question_c_output_dir, question_c_intermediate_csv),
                          index=True)

    # save the questionc_csv
    add_units(curl_result_df)
    curl_result_df.drop(columns=['website']).to_csv(os.path.join(question_c_output_dir, question_c_output_csv),
                                                    index=False)


if __name__ == '__main__':
    # only calculate first 10k
    first_10k(top_1m_dir, top_1m_filename)

    # divided 10k into 10 machines, each 1000
    chunksize_ = 1000
    machine_size = chunk_csv_to_file(chunksize_, top_1m_filename, top_1m_dir)
    print(machine_size)

    # run all by loop (can run with 10 different machines)
    for i in range(machine_size):
        arg_filename = 'chunk.csv'
        arg_dir = os.path.join(top_1m_dir, chunk_dir_pattern % i)
        arg_chunksize_thread = 100
        chunk_thread_pattern_ = "chunk_thread_%d"
        multiprocess_chunk_one(arg_filename, arg_dir, arg_chunksize_thread, chunk_thread_pattern_,
                               summary_dist=('summary_%d.csv' % i))
    # summary all summary-files
    summary_all(machine_size)
    output()
