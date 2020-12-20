import argparse
import os
import time

import pandas as pd
import multiprocessing
import subprocess
from utils import question_c_output_dir, question_c_intermediate_csv, question_f_top_1k_csv, \
    question_f_output_dir, curl_program_h2, top_1k_h3_csv
from shutil import copyfile
from curl_call import clean_logger, init_logger, summary_result
import shlex
import itertools
import json
import logging
from chunk_split import chunk_csv_to_file

# top_1k_h2_csv = "top-1k-h2.csv"
# top_1k_h2_fail_csv = "top-1k-h2-fail.csv"
#
# source_df = pd.read_csv(os.path.join(question_c_output_dir, question_c_intermediate_csv))
# source_df[(source_df['status'] == 'ok') & (source_df['time_connect'] != 0.0)].head(n=1000).to_csv(
#     os.path.join("./123.csv"), index=False)

source_df_123 = pd.read_csv(os.path.join("xxx/123.csv"))
source_df_1234 = pd.read_csv(os.path.join("./1234.csv"))
# source_df_123.merge(source_df_1234, how='inner', left_on='no', right_on='no'))
print(pd.concat([source_df_123[['no']], source_df_1234[['no']]]).drop_duplicates(keep=False))
