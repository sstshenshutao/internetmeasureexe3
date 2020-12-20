import os
import pandas as pd

curl_program_h3 = "./build_curl/h3/curl/src/curl"
curl_program_h2 = "./build_curl/h2/curl/src/curl"
top_1m_dir = "./toplist_1m"
top_1m_filename = "top-1m.csv"
top_1m_csv = os.path.join(top_1m_dir, top_1m_filename)
chunk_dir_pattern = "chunk_%d"
question_c_output_dir = "question_c_output"
question_c_output_csv = "output.csv"
question_c_intermediate_csv = "intermediate.csv"

question_d_output_dir = "question_d_output"
question_d_output_csv = "output.csv"
question_d_top_1k_h3_csv = "top-1k-h3.csv"
question_d_top_1k_asn_csv = "top-1k-h3-asn.csv"
asn_regex_csv = os.path.join('as_csv', 'regexes.csv')
asns_csv = os.path.join('as_csv', 'asns.csv')
bgp_rib = os.path.join('as_csv', 'rib.20201215.1200.bz2')
ipasn_db = os.path.join('as_csv', 'IPASN.DAT')

question_e_output_dir = "question_e_output"
question_e_lim8 = "lim8.png"
question_e_lim1 = "lim1.png"

question_f_output_dir = "question_f_output"
question_f_output_csv = "output.csv"
question_f_top_1k_csv = "top-1k.csv"
question_f_lim8 = "lim8.png"
question_f_lim1 = "lim1.png"
top_1k_h2_csv = "top-1k-h2.csv"
top_1k_h2_fail_csv = "top-1k-h2-fail.csv"
top_1k_h3_csv = "top-1k-h3.csv"
all_summary = 'all_summary.csv'

question_g_output_dir = "question_g_output"
question_g_lim8 = "lim8.png"
question_g_lim1 = "lim1.png"

question_h_output_dir = "question_h_output"
question_i_output_dir = "question_i_output"

def first_10k(some_dir, filename):
    source_dfs = pd.read_csv(os.path.join(some_dir, filename), header=None, index_col=0, names=["no", "website"],
                             chunksize=10000)
    for df in source_dfs:
        df.to_csv(os.path.join(some_dir, filename), mode='w', index=True, header=False)
        break


def add_units(input_df):
    def funfunc(x):
        return str(x) + "s" if pd.notnull(x) else None

    # add unit
    input_df["time_appconnect"] = input_df["time_appconnect"].map(funfunc)
    input_df["time_connect"] = input_df["time_connect"].map(funfunc)
    input_df["time_namelookup"] = input_df["time_namelookup"].map(funfunc)
    input_df["time_pretransfer"] = input_df["time_pretransfer"].map(funfunc)
    input_df["time_redirect"] = input_df["time_redirect"].map(funfunc)
    input_df["time_starttransfer"] = input_df["time_starttransfer"].map(funfunc)
    input_df["time_total"] = input_df["time_total"].map(funfunc)
