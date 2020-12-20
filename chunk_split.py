# split the csv to some chunks

import argparse
import os
import pandas as pd
from utils import top_1m_filename, top_1m_dir, chunk_dir_pattern


def init_argparse():
    parser = argparse.ArgumentParser(description='question_b')
    parser.add_argument('--filename', metavar='filename', type=str, nargs='?',
                        help='unzip url')
    parser.add_argument('--dir', metavar='dir', type=str, nargs='?',
                        help='unzip dir')
    parser.add_argument('--chunksize', metavar='chunksize', type=int, nargs='?',
                        help='unzip dir')
    return parser.parse_args()


def chunk_csv_to_file(chunksize, filename, csv_dir, chunk_dir_pattern_=chunk_dir_pattern):
    print("split '%s' into %d-record-chunks >> %s" % (filename, chunksize, csv_dir))
    source_dfs = pd.read_csv(os.path.join(csv_dir, filename), header=None, index_col=0, names=["no", "website"],
                             chunksize=chunksize)
    index = 0
    counter = 0
    for df in source_dfs:
        output_dir = os.path.join(csv_dir, chunk_dir_pattern_ % index)
        output_file = os.path.join(output_dir, "chunk.csv")
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        df.to_csv(output_file, mode='w', index=True, header=False)
        counter += df.size
        print("chunk to %s_%d %d, total: %d" % (filename, index, df.size, counter))
        index += 1
    return index
