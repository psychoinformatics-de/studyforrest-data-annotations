#!/usr/bin/python
'''
'''
from os.path import join as opj
import pandas as pd


def time_stamp_to_sec(t_stamp='01:50:34:01'):
    '''
    Input:
        time stamp (str) in format HH:MM:SS:Frame

    Output:
        time point in seconds (float)
    '''
    splitted_stamp = t_stamp.split(':')
    milliseconds = (int(splitted_stamp[0]) * 60 * 60 * 1000) +\
                        (int(splitted_stamp[1]) * 60 * 1000) +\
                        (int(splitted_stamp[2]) * 1000) +\
                        (int(splitted_stamp[3]) * 40)

    seconds = milliseconds / 1000.0

    return seconds


# read the annotation
df = pd.read_csv(opj('src', 'voice', 'speech_vocalization.csv'))

# filter for rows that contain an #-flag indicating missing timing
df = df.loc[df.iloc[:, 0].str.contains('#') == False]
df = df.loc[df.iloc[:, 1].str.contains('#') == False]

# convert time stamps to
df.iloc[:, 0] = df.iloc[:, 0].apply(time_stamp_to_sec)
df.iloc[:, 1] = df.iloc[:, 1].apply(time_stamp_to_sec)

# replace column 1 (end) with duration (end - start)
df.iloc[:,1] = df.iloc[:,1] - df.iloc[:,0]

# apply BIDS standard column names
df.rename(columns=dict(start='onset', end='duration'), inplace=True)

df.to_csv(
    opj('researchcut', 'speech_vocalization.tsv'),
    index=False,
    sep='\t',
    float_format='%.3f')
