import argparse
import os
import time
from utils import question_c_output_dir, question_c_intermediate_csv, question_d_output_dir, question_d_top_1k_h3_csv, \
    question_d_top_1k_asn_csv
from ip_asn import Host, Asn
import pandas as pd


def support_h3(df):
    h3_df = df[df['status'] == 'ok']
    print("%d websites support HTTP/3!" % h3_df['status'].size)
    h3_head_df = h3_df.head(n=1000)
    # h3_head_df.to_csv(
    #     os.path.join(question_d_output_dir, question_d_top_1k_h3_csv), index=False)
    return h3_head_df


if __name__ == '__main__':
    if not os.path.exists(question_d_output_dir):
        os.mkdir(question_d_output_dir)

    source_df = pd.read_csv(os.path.join(question_c_output_dir, question_c_intermediate_csv))
    h3_1k_df = support_h3(source_df)
    asn = Asn()
    host = Host()
    h3_1k_df['asn'] = h3_1k_df['remote_ip'].apply(asn.lookup)
    asn_df = h3_1k_df['asn'].value_counts().sort_values(ascending=False).rename_axis(
        'asn').reset_index(name='num_http3_websites')
    # to file
    asn_df.to_csv(
        os.path.join(question_d_output_dir, question_d_top_1k_asn_csv), index=False)
    asn_df['provider'] = asn_df['asn'].apply(host.identify_ases)
    print(asn_df)
