#!/usr/bin/python
'''
'''
from os.path import join as opj
import pandas as pd

# read the annotation
# TO DO: skiprows flagged with '???' here already?
df = pd.read_csv(opj('src', 'voice', 'data', 'audio-description-by-word.csv'))

# # drop rows with whole sentences as flagged with '???' in column 1
df = df.loc[df.iloc[:,1] != '???']
# reset index
# df.index = range(0, len(df))

# convert the cleaned columns to float64
df.iloc[:, 0:2] = df.iloc[:, 0:2].astype('float64')

# replace column 1 (end) with duration (end - start)
df.iloc[:,1] = df.iloc[:,1] - df.iloc[:,0]

# apply BIDS standard column names
df.rename(columns=dict(start='onset', end='duration'), inplace=True)

df.to_csv(
    opj('researchcut', 'audio-description-by-word.tsv'),
    index=False,
    sep='\t',
    float_format='%.3f')
