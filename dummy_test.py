import pandas as pd

source_df = pd.read_csv("toplist_1m/chunk_0/chunk_thread_0/chunk.csv", header=None,
                        names=["no", "website"]).head()


# print(source_df)


def functionapply(str):
    dictionary = {'no': str, 'a': "a_%s" % str, 'b': "b_%s" % str, 'c': "c_%s" % str}
    series = pd.Series(dictionary)
    return series


# source_df['a', 'b', 'c'] =
kk = source_df['no'].apply(functionapply)
source_df = source_df.merge(kk, left_on='no', right_on='no')
print(source_df)
