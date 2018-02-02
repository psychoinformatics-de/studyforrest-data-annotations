#!/usr/bin/python
"""
created on Wed Jan 30 2018
author: Christian Olaf Haeusler

To Do:
    argparser
"""
from __future__ import print_function
from collections import defaultdict
from datetime import datetime
import csv
import os
import re
import sys


# constants #
MOVIE = True
CROPPED = 0 # in sec; is a concatenated time series with cropped volumes used?
INPUT_FILES = ['structure.csv',
               'speech_vocalization.csv',
               'speech_google_narrator.csv'] # sys.argv[1]
OUT_DIR = './annos_segmented/output'

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


# functions #
def read_anno(anno):
    '''not pretty but works with different kind of annoation formats
    '''
    with open(anno, 'r') as txt_file:
        rows = txt_file.readlines()

    print('\nReading:', os.path.basename(anno))

    cleaned = []
    for row in rows:
        row = row.strip()
        row = row.split(',')

        # skip the header
        if row[0] in ['time', 'start']:
            continue

        # skip column 1 if it cointains '???' (s.speech_google_narrator.csv)
        if '???' in row[1]:
            continue

        # in column 0 and (maybe) column 1, convert time stamps (hh:mm:ss:ff)
        # to seconds (s. structure.csv and speech_vocalization.csv)
        regex = r'[\d#]+:[\d#]+:[\d#]+:[\d#]+'

        # check if time info is given as a time stamp in column 0
        # and if the time stamp does not contain a commentary ('#')
        if re.match(regex, row[0]):
            if '#' not in row[0]:
                row[0] = time_stamp_to_msec(row[0]) / 1000.0
            else:
                print('skipping', row)
                continue
        # else time must be given in seconds already
        else:
            row[0] = float(row[0])

        # check if column 1 gives time info, too ('end')
        # check if it is given as a time stamp (hh:mm:ss:ff)
        # and if the time stamp contains a commentary
        if re.match(regex, row[1]):
            if '#' not in row[1]:
                row[1] = time_stamp_to_msec(row[1]) / 1000.0
            else:
                print('skipping', row)
        # if it is not a time stamp it must be in seconds
        # or the column does not provide time info at all
        else:
            try:
                row[1] = float(row[1])
            except ValueError as e:
                pass

        cleaned.append(row)

    return cleaned


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


def fix_segment_shift(timing_in_anno, cropped_time):
    '''
    the function is not necessary anymore since the correction
    is implicitly done by additionally given offsets in SEGMENTS_OFFSETS


    fixes the timing of the 8 stimulus movie sigments
    https://github.com/psychoinformatics-de/studyforrest-data-phase2/blob/master/code/stimulus/movie/segment_timing.csv
    '''
    # regular case which will be kept in runs 1 and 2
    timing_in_segment = timing_in_anno

    # correct for the accumulating offsets in segments 3 to 8
    for segment_start, offset in sorted(SEGMENTS_OFFSETS, reverse = True):
        # if timing is in a critical segment, correct the timing
        if timing_in_anno >= segment_start + cropped_time:
            timing_in_segment = round(timing_in_anno - offset, 3)
            break

    return timing_in_segment


def fix_audio_timing(uncorrected_audio):
    '''the movie's audiotrack lacks behind the visual frames
    there is an slightly increasing offset (but problably no continuous drift)
    over the movie segments
    '''
    corrected_audio = uncorrected_audio
    return corrected_audio


def anno_time_to_seg_time(seg_starts, run_nr, anno_time, cropped_time):
    '''
    "The position of an event from a movie annotation with respect to the
    cropped fMRI time series can now be determined by substracting the
    start time of the respective segment as listed in Table 1"
    http://studyforrest.org/annotation_timing.html

    events occur earlier in the cropped stimulus segments.
    hence the cropped ammount is additionally substracted from the anno timing
    '''
    seg_time = round(anno_time - (seg_starts[run_nr] + cropped_time), 2)

    return seg_time


def write_segmented_annos(source_anno, movie, cropped, run_dict, out_dir, ):
    '''
    '''
    if MOVIE is True:
        stimulus = 'movie'
    else:
        stimulus = 'audio'

    old_anno_name = os.path.splitext(os.path.basename(source_anno))[0]
    new_anno_name = '%s_%s_%scr' % ((old_anno_name, stimulus, cropped))

    print('Writing results to %s' % new_anno_name)

    for run in sorted(run_dict.keys()):
        print(run)

        tnow = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        out_fname = '%s_%s_run_%s.csv' % (new_anno_name, tnow, run + 1)
        out_path = os.path.join(out_dir, out_fname)
        print(out_path)

        # in case the OUT_DIR changes to a directory incl. subdirectories
        path = os.path.dirname(out_path)
        if not os.path.exists(path):
            os.makedirs(path)

        with open(out_path, 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(run_dict[run])


#### main program #####
if __name__ == "__main__":

    # read the annotation file
    for input_file in INPUT_FILES[:1]:
        anno = read_anno(input_file)
        segment_starts = [start for start, offset in SEGMENTS_OFFSETS]

        run_events = defaultdict(list)
        for row in anno:
        # get the run number
            run = get_run_number(segment_starts, row[0])

            # SEGMENT SHIFT correction
            # is now implicitly done by func 'anno_time_to_seg_time'
            # using the adjusted segment starts (s. SEGMENTS_OFFSETS)
#             row[0] = fix_segment_shift(row[0], CROPPED)
#             if type(row[1]) == float:
#                 row[1] = fix_segment_shift(row[1], CROPPED)

            # finally convert the timings of the continouos annotation
            # to timings in respect to the start of the corresponding segment
            row[0] = anno_time_to_seg_time(segment_starts, run, row[0], CROPPED)
            if type(row[1]) == float:
                row[1] = anno_time_to_seg_time(segment_starts, run, row[1], CROPPED)

            # AUDIO TIMING (MOVIE) correction
            # Dialoge im Film kommen 1/2 frame spater als das Hoerspiel,
            # das einem frame (40ms) nach vorn gezogen wurde
            if MOVIE is True:
                pass

            # AUDIO TIMING (AUDIOBOOK) correction
            if MOVIE is False:
                pass

            # append that shit
            run_events[run].append(row)

        write_segmented_annos(input_file, MOVIE, CROPPED, run_events, OUT_DIR)
