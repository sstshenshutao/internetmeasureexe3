import os
from utils import question_c_output_dir, question_c_intermediate_csv, question_e_output_dir, question_e_lim8, \
    question_e_lim1
import pandas as pd

import matplotlib.pyplot as plt


def support_h3(df):
    h3_df = df[df['status'] == 'ok'].copy()
    return h3_df


if __name__ == '__main__':
    if not os.path.exists(question_e_output_dir):
        os.mkdir(question_e_output_dir)

    source_df = pd.read_csv(os.path.join(question_c_output_dir, question_c_intermediate_csv), index_col=0)
    h3_1k_df = support_h3(source_df)
    # |---DNS---||---QUIC--||--C--|----Transfer---|   the whole sequence process
    h3_1k_df['DNS Lookup'] = h3_1k_df['time_namelookup']
    h3_1k_df['QUIC'] = h3_1k_df['time_connect'] - h3_1k_df['time_namelookup']
    h3_1k_df['Compute'] = h3_1k_df['time_starttransfer'] - h3_1k_df['time_pretransfer']
    h3_1k_df['Transfer'] = h3_1k_df['time_total'] - h3_1k_df['time_starttransfer']
    h3_1k_df['Total Time'] = h3_1k_df['time_total']
    # plot
    plt.clf()
    ax = plt.gca()
    boxplot = h3_1k_df.boxplot(ax=ax, column=['DNS Lookup', 'QUIC', 'Compute', 'Transfer', 'Total Time'])
    plt.savefig(os.path.join(question_e_output_dir, question_e_lim8), dpi=300)
    ax.set_ylim(top=1)
    plt.savefig(os.path.join(question_e_output_dir, question_e_lim1), dpi=300)
