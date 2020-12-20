import os
from utils import question_c_output_dir, question_c_intermediate_csv, question_g_output_dir, question_f_output_dir, \
    top_1k_h2_csv, question_g_lim8, question_g_lim1
import pandas as pd

import matplotlib.pyplot as plt
from question_e import support_h3

if __name__ == '__main__':
    if not os.path.exists(question_g_output_dir):
        os.mkdir(question_g_output_dir)

    # prepare h3
    source_df = pd.read_csv(os.path.join(question_c_output_dir, question_c_intermediate_csv))
    source_df_h3 = support_h3(source_df)[["no", "time_appconnect",
                                          "time_connect",
                                          "time_namelookup",
                                          "time_pretransfer",
                                          "time_redirect",
                                          "time_starttransfer",
                                          "time_total"]]
    source_df_h3.rename(columns={
        "time_appconnect": "time_appconnect_h3",
        "time_connect": "time_connect_h3",
        "time_namelookup": "time_namelookup_h3",
        "time_pretransfer": "time_pretransfer_h3",
        "time_redirect": "time_redirect_h3",
        "time_starttransfer": "time_starttransfer_h3",
        "time_total": "time_total_h3",
    }, inplace=True)
    # prepare h2
    source_df_h2 = pd.read_csv(os.path.join(question_f_output_dir, top_1k_h2_csv))[["no", "time_appconnect",
                                                                                    "time_connect",
                                                                                    "time_namelookup",
                                                                                    "time_pretransfer",
                                                                                    "time_redirect",
                                                                                    "time_starttransfer",
                                                                                    "time_total"]]
    source_df_h2.rename(columns={
        "time_appconnect": "time_appconnect_h2",
        "time_connect": "time_connect_h2",
        "time_namelookup": "time_namelookup_h2",
        "time_pretransfer": "time_pretransfer_h2",
        "time_redirect": "time_redirect_h2",
        "time_starttransfer": "time_starttransfer_h2",
        "time_total": "time_total_h2",
    }, inplace=True)
    # merge them
    merged_df = source_df_h2.merge(source_df_h3, left_on='no', right_on='no')
    # print(merged_df)
    # merged_df\[\"$1\\n_delta\"\]=merged_df\[\"$1_h2\"\]-merged_df\[\"$1_h3\"\]
    merged_df["time\n appconnect\n delta"] = merged_df["time_appconnect_h2"] - merged_df["time_appconnect_h3"]
    merged_df["time\n connect\n delta"] = merged_df["time_connect_h2"] - merged_df["time_connect_h3"]
    merged_df["time\n namelookup\n delta"] = merged_df["time_namelookup_h2"] - merged_df["time_namelookup_h3"]
    merged_df["time\n pretransfer\n delta"] = merged_df["time_pretransfer_h2"] - merged_df["time_pretransfer_h3"]
    merged_df["time\n redirect\n delta"] = merged_df["time_redirect_h2"] - merged_df["time_redirect_h3"]
    merged_df["time\n starttransfer\n delta"] = merged_df["time_starttransfer_h2"] - merged_df["time_starttransfer_h3"]
    merged_df["time\n total\n delta"] = merged_df["time_total_h2"] - merged_df["time_total_h3"]

    # plot
    _, ax = plt.subplots(figsize=(12, 5))
    plot_df = merged_df[["time\n appconnect\n delta",
                         "time\n connect\n delta",
                         "time\n namelookup\n delta",
                         "time\n pretransfer\n delta",
                         "time\n redirect\n delta",
                         "time\n starttransfer\n delta",
                         "time\n total\n delta"]]
    bp = plot_df.boxplot(ax=ax,
                         column=["time\n appconnect\n delta",
                                 "time\n connect\n delta",
                                 "time\n namelookup\n delta",
                                 "time\n pretransfer\n delta",
                                 "time\n redirect\n delta",
                                 "time\n starttransfer\n delta",
                                 "time\n total\n delta"])
    plot_df.quantile([0.25, 0.5, 0.75]).rename(columns={
        "time\n appconnect\n delta": "time_appconnect_delta",
        "time\n connect\n delta": "time_connect_delta",
        "time\n namelookup\n delta": "time_namelookup_delta",
        "time\n pretransfer\n delta": "time_pretransfe_delta",
        "time\n redirect\n delta": "time_redirect_elta",
        "time\n starttransfer\n delta": "time_starttransfer_delta",
        "time\n total\n delta": "time_total_delta"
    }).to_csv(os.path.join(question_g_output_dir, 'percentiles.csv'))
    plt.savefig(os.path.join(question_g_output_dir, question_g_lim8), dpi=300)
    ax.set_ylim(top=1)
    plt.savefig(os.path.join(question_g_output_dir, question_g_lim1), dpi=300)
