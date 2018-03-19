#!/usr/bin/python3
"""
created on Wed Jan 30 2018
author: Christian Olaf Haeusler

To Do:
    argparser
    Erzaehler Filtern wennn MOVIE = True
"""
from collections import defaultdict
import os
from os.path import basename
from os.path import join as opj
from os.path import exists
import re
import sys
import pandas as pd


SEGMENTS_OFFSETS = (
    (0.00, 0.00),
    (886.00, 0.00),
    (1752.08, 0.08),  # third segment's start
    (2612.16, 0.16),
    (3572.20, 0.20),
    (4480.28, 0.28),
    (5342.36, 0.36),
    (6410.44, 0.44),  # last segment's start
    (7086.00, 0.00))  # movie's last time point

# dictionaries with paired touples containing time (2sec steps) and offset
# in respect to the audiovisual movie (forrestgump_researchcut_ger_mono.mkv)
AUDIO_AV_OFFSETS = {
    0: {  0:  21.33},
    1: {  0:  37.33,
        408:  21.33},
    2: {  0:  69.33,
        199:  61.33},
    3: {  0:  93.33,
        320: 101.33},
    4: {  0: 109.33,
        401: 101.33},
    5: {  0: 141.33},
    6: {  0: 189.31,
         61: 181.31},
    7: {  0: 205.33}}

AUDIO_AO_OFFSETS = {
    0: {  0:  47.02},
    1: {  0:  36.35,
        203:  47.02},
    2: {  0:  87.02,
        199:  92.35},
    3: {  0: 124.35,
        320: 132.35},
    4: {  0: 105.69,
        401:  92.35},
    5: {  0: 137.69,
        364: 167.02},
    6: {  0: 201.67,
         61: 543.00},
    7: {  0:-1422.31}}


def time_stamp_to_msec(t_stamp='01:50:34:01'):
    '''
    Input:
        time stamp (str) in format HH:MM:SS:Frame

    Output:
        time point in milliseconds (int)
    '''
    splitted_stamp = t_stamp.split(':')
    milliseconds = (int(splitted_stamp[0]) * 60 * 60 * 1000) +\
                   (int(splitted_stamp[1]) * 60 * 1000) +\
                   (int(splitted_stamp[2]) * 1000) +\
                   (int(splitted_stamp[3]) * 40)

    return milliseconds


def msec_to_time_stamp(milliseconds=6634040):
    '''
    Input:
        a time point in  milliseconds (int)

    Output:
        a time stamp (str) in format HH:MM:SS:Frame
    '''
    # convert in case function was called from the command line with the
    # timing given as a string
    milliseconds = int(milliseconds)

    hours = (milliseconds / (60 * 60 * 1000))
    minutes = (milliseconds % (60 * 60 * 1000) / (60 * 1000))
    seconds = (milliseconds % (60 * 60 * 1000) % (60 * 1000) / 1000)
    frame = (milliseconds % (60 * 60 * 1000) % (60 * 1000) % (1000) // 40)
    time_stamp = '%02d:%02d:%02d:%02d' % (hours, minutes, seconds, frame)

    return time_stamp


def get_run_number(starts, onset):
    '''
    '''
    for start in sorted(starts, reverse=True):
        if onset >= start:
            run = starts.index(start)
            break

    return run


def whole_anno_to_segments(seg_starts, run_nr, anno_time):
    '''
    "The position of an event from a movie annotation with respect to the
    cropped fMRI time series can now be determined by substracting the
    start time of the respective segment as listed in Table 1"
    http://studyforrest.org/annotation_timing.html
    '''
    seg_time = anno_time - seg_starts[run_nr]

    return seg_time


def fix_audio_movie_segments(AUDIO_AV_OFFSETS, run, uncorrected):
    '''corrects the segments' audio offsets
    in respect to the unsegmented movie
    '''
    critical_time_points = sorted(AUDIO_AV_OFFSETS[run].keys(), reverse=True)
    for crit in critical_time_points:
       if uncorrected >= crit * 2.0:
           corrected = uncorrected + (AUDIO_AV_OFFSETS[run][crit] / 1000.0)
           break

    return corrected


def fix_audio_descr_segments(AUDIO_AO_OFFSETS, run, uncorrected):
    '''corrects the segments' audio offsets
    in respect to the unsegmented audiobook
    '''
    critical_time_points = sorted(AUDIO_AO_OFFSETS[run].keys(), reverse=True)
    for crit in critical_time_points:
       if uncorrected >= crit * 2.0:
           corrected = uncorrected + (AUDIO_AO_OFFSETS[run][crit] / 1000.0)
           break

    return corrected


def write_segmented_annos(infilename, stimulus, run_dict, out_dir):
    '''
    '''
    basefilename = basename(infilename)[:-4]
    outdir = opj(out_dir, stimulus)
    if not exists(outdir):
        os.makedirs(outdir)

    for run in sorted(run_dict.keys()):
        outname = opj(out_dir, stimulus, '{}_run-{}_events.tsv'.format(
            basefilename,
            run + 1))

        pd.DataFrame.from_records(
            run_dict[run],
            columns=run_dict[run][0].dtype.names).to_csv(
                outname,
                sep='\t',
                index=False,
                encoding='utf-8')


#### main program #####
if __name__ == "__main__":
    # constants #
    infile = sys.argv[1]
    annotated_time = sys.argv[2]
    target_time = sys.argv[3]
    outdir = sys.argv[4]

#     with launch_ipdb_on_exception():
    # read the annotation file
    anno = pd.read_csv(infile, sep='\t', encoding='utf-8').to_records(index=False)
    segment_starts = [start for start, offset in SEGMENTS_OFFSETS]

    run_events = defaultdict(list)
    for row in anno:
        # get the run number
        run = get_run_number(segment_starts, row['onset'])

        # convert the timings of a continuous annotation
        # to timings in respect to the start of the corresponding segment
        onset_in_seg = whole_anno_to_segments(
            segment_starts,
            run,
            float(row['onset']))


        # correct for the stimulus used to annotate the audiotrack
        if annotated_time == 'aomovie':
            # the files
            # forrestgump_researchcut_ad_ger.flac and
            # german_dvd_5.1_48000hz_488kb_research_cut_aligned_cutted_narrator_muted_48000Hz.flac
            # (that contain the audio description) were originally lagging
            # behind for XYZ msec and were shiftet forward
            # by one frame (40ms) in respect to the reference file
            # forrestgump_researchcut_ger.mkv

            # 1st, correct for shifting the narrator (incl. dialogue) 40ms
            # to the front before annotating the narrator/dialogue
            onset_in_seg += 0.040

            # 2nd, correct for the offset between the (unshifted) audio
            # description and the audiovisual movie
            # -> the offset is varying +/- one frame (40 ms) around 0
            onset_in_seg -= 0.000

            # 3rd, correct for the offset between whole stimulus
            # (audiovisual or audio-only) and its segments
            if target_time == 'avmovie':
                onset_in_seg = fix_audio_movie_segments(
                    AUDIO_AV_OFFSETS,
                    run,
                    onset_in_seg)

            elif target_time == 'aomovie':
                onset_in_seg = fix_audio_descr_segments(
                    AUDIO_AO_OFFSETS,
                    run,
                    onset_in_seg)

            else:
                raise ValueError('Unknown time label %s', target_time)

        elif annotated_time == 'avmovie':
            # all splendid for now
            pass

        else:
            raise ValueError('%s is an unknown annotation', basename(input_file))

        row['onset'] = round(onset_in_seg, 3)

        # append that shit
        run_events[run].append(row)

    write_segmented_annos(infile, target_time, run_events, outdir)
