import os

import seaborn as sns
import pandas as pd
from utils import question_i_output_dir, question_f_top_1k_csv, question_h_output_dir
import matplotlib.pyplot as plt

if __name__ == '__main__':
    if not os.path.exists(question_i_output_dir):
        os.mkdir(question_i_output_dir)
    h2_df = pd.read_csv(os.path.join(question_h_output_dir, 'summary_chrome_h2.csv'))
    h2_df.rename(columns={
        "responseStart": "responseStart HTTP/2",
        "domInteractive": "domInteractive HTTP/2",
        "domComplete": "domComplete HTTP/2"
    }, inplace=True)
    h3_df = pd.read_csv(os.path.join(question_h_output_dir, 'summary_chrome_h3.csv'))
    h3_df.rename(columns={
        "responseStart": "responseStart HTTP/3",
        "domInteractive": "domInteractive HTTP/3",
        "domComplete": "domComplete HTTP/3"
    }, inplace=True)
    # plot
    plt.clf()
    ax = plt.gca()
    sns.ecdfplot(ax=ax, data=h2_df, x="responseStart HTTP/2", label="responseStart HTTP/2", linestyle="dashed",
                 color='green', stat="proportion")
    sns.ecdfplot(ax=ax, data=h2_df, x="domInteractive HTTP/2", label="domInteractive HTTP/2", linestyle="dashed",
                 color='blue', stat="proportion")
    sns.ecdfplot(ax=ax, data=h2_df, x="domComplete HTTP/2", label="domComplete HTTP/2", linestyle="dashed",
                 color='red', stat="proportion")
    sns.ecdfplot(ax=ax, data=h3_df, x="responseStart HTTP/3", label="responseStart HTTP/3", linestyle="solid",
                 color='green', stat="proportion")
    sns.ecdfplot(ax=ax, data=h3_df, x="domInteractive HTTP/3", label="domInteractive HTTP/3", linestyle="solid",
                 color='blue', stat="proportion")
    sns.ecdfplot(ax=ax, data=h3_df, x="domComplete HTTP/3", label="domComplete HTTP/3", linestyle="solid",
                 color='red', stat="proportion")

    ax.legend(fontsize='xx-small')
    ax.set_ylabel('CDF')
    ax.set_xlabel('time (ms)')
    ax.set_title('chrome webpage timing statistics')
    plt.savefig(os.path.join(question_i_output_dir, "output_no_limit.png"), dpi=300)
    ax.set_xlim(left=0, right=10000)
    plt.savefig(os.path.join(question_i_output_dir, "output_limit_10000.png"), dpi=300)
