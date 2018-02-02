#!/usr/bin/python

from os.path import join as opj
import pandas as pd

df = pd.read_csv(opj('src', 'locations', 'data', 'structure.csv'))

# apply BIDS standard column names
df.rename(columns=dict(time='onset'), inplace=True)

# last line in input is not a shot, but the end of the last shot
shot_durations = df['onset'].diff()[1:]
shot_durations.index = range(0, len(shot_durations))
df.drop(df.tail(1).index, inplace=True)
# include BIDS standard duration column
df.insert(1, 'duration', shot_durations)

df.to_csv(
    opj('researchcut', 'locations.tsv'),
    sep='\t',
    index=False)
