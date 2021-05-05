#!/usr/bin/env python3
'''merges and copies (already segmented) annotations of confounds
'''


from glob import glob
import argparse
import numpy as np
import os
import pandas as pd
import re


# constants
# no. of segments
SEGMENTS = range(0, 8)
# currently relevant annotations
VIS_CONFS = ['brmean', 'brlr', 'brud', 'phash', 'normdiff']
AUD_CONFS = ['rms', 'lrdiff']

def parse_arguments():
    '''
    '''
    parser = argparse.ArgumentParser(
        description='merges and copies annotations of confounds'
    )

    parser.add_argument('-i',
                        help='input directory where files are located',
                        default='src/confounds/annotation/audio/'
                        )

    parser.add_argument('-s',
                        help='the annotated stimulus' +
                        '(\'aomovie\' or \'avmovie\')',
                        default='aomovie'
                        )

    parser.add_argument('-o',
                        default='test',
                        help='output directory')

    args = parser.parse_args()

    in_dir = args.i
    stimulus = args.s
    out_dir = args.o

    return in_dir, stimulus, out_dir


def find_files(pattern):
    '''
    '''
    found_files = glob(pattern)

    return sorted(found_files)

def create_merged_datafr(inputs):
    '''
    '''
    # initial dataframe providing 'duration', too
    df = pd.read_csv(inputs[0],
                     header=0,
                     sep='\t',
                     index_col=0,
                     dtype='str'  # read all input as string
                     )

    # populate the dataframe with the data from remaining files
    for input_f in inputs[1:]:
        df_new = pd.read_csv(input_f,
                             usecols=[0, 2],
                             index_col=0, # well, thats hard coded
                             header = 0,
                             sep='\t',
                             dtype='str'  # read all input as string
                             )

        df[df_new.columns[0]] = df_new

    return df



if __name__ == '__main__':
    # get command line arguments
    in_dir, stimulus, out = parse_arguments()

    out_path = os.path.join(out, stimulus)
    os.makedirs(out_path, exist_ok=True)

    if stimulus == 'aomovie':
        file_pattern = 'fg_ad_seg?_*.tsv'
#        in_fpathes = find_files(os.path.join(in_dir, file_pattern))
    elif stimulus == 'avmovie':
        file_pattern = 'fg_av_ger_seg?_*.tsv'
#        in_fpathes = find_files(os.path.join(in_dir, file_pattern))
    else:
        raise ValueError('stimulus must be \'aomovie\' or \'avmovie\'')

    # segments = [re.search(r'seg\d{1}', in_fpath) for in_fpath in in_fpathes]
    # segments = sorted(list(set([segment.group() for segment in segments])))

    for segment in SEGMENTS:
        run = f'run-{segment + 1}'
        # subtitute for current segment
        inputs = os.path.join(in_dir, file_pattern)
        inputs = inputs.replace('seg?', f'seg{str(segment)}')

        if 'visual' in in_dir:
            inputs = [inputs.replace('_*.tsv', f'_{conf}.tsv') for conf in VIS_CONFS]
            out_file = 'conf_visual_' + run + '_events.tsv'

        elif 'audio' in in_dir:
            inputs = [inputs.replace('_*.tsv', f'_{conf}.tsv') for conf in AUD_CONFS]
            out_file = 'conf_audio_' + run + '_events.tsv'

        # read and merge the inputs
        merged_df = create_merged_datafr(inputs)

        # prepare saving
        out_fpath = os.path.join(out_path, out_file)
        # format the index in such a way
        # that is written to file nicely formatted
        merged_df.reset_index(level=0, inplace=True)
        merged_df['onset'] = merged_df['onset'].map('{:.2f}'.format)
        merged_df.to_csv(out_fpath, sep='\t', index=False)
