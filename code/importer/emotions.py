#!/usr/bin/python
#
# This source code is (C) by Michael Hanke <michael.hanke@gmail.com> and
# made available under the terms of the Creative Common Attribution-ShareAlike
# 4.0 International (CC BY-SA 4.0) license.
#

import numpy as np

#
# Load data
#


def get_nsecond_segments(n=1):
    onsets = np.recfromcsv(
        opj('src', 'locations', 'data', 'structure.csv'),
            names=('start', 'title', 'major', 'setting', 'locale', 'intext', 'temp', 'tod'))['start']
    max = float(onsets[-1])
    return np.array((np.arange(0, max - n, n), np.arange(n, max, n))).T


def get_av_ratings():
    import glob
    return [np.recfromcsv(f) for f in glob.glob(
        opj('src', 'emotions', 'data', 'raw', 'av*.csv'))]


def get_ao_ratings():
    import glob
    return [np.recfromcsv(f) for f in glob.glob(
        opj('src', 'emotions', 'data', 'raw', 'ao*.csv'))]


#
# Segmentation
#


def mk_thresh_emotion_episodes(rat, thresh, segments):
    # yield per character list of emotion episodes with a minimum inter-observer
    # agreement wrt any emotion attribute
    chars = get_unique_characters(rat)
    episodes = {}

    def _postprocess(e):
        return {k: np.median(v) for k, v in e.items()}

    for char in chars:
        ep = episodes.get(char, [])
        ind = [get_arousal_modulation(rat, segments, char=char)]
        labels = ['arousal']
        for l, d in (('v_pos', dict(valence='POS')),
                     ('v_neg', dict(valence='NEG')),
                     ('d_self', dict(direction='SELF')),
                     ('d_other', dict(direction='OTHER')),
                     ('e_admiration', dict(emotion='ADMIRATION')),
                     ('e_anger/rage', dict(emotion='ANGER/RAGE')),
                     ('e_contempt', dict(emotion='CONTEMPT')),
                     ('e_disappointment', dict(emotion='DISAPPOINTMENT')),
                     ('e_fear', dict(emotion='FEAR')),
                     ('e_fears_confirmed', dict(emotion='FEARS_CONFIRMED')),
                     ('e_gloating', dict(emotion='GLOATING')),
                     ('e_gratification', dict(emotion='GRATIFICATION')),
                     ('e_gratitude', dict(emotion='GRATITUDE')),
                     ('e_happiness', dict(emotion='HAPPINESS')),
                     ('e_happy-for', dict(emotion='HAPPY-FOR')),
                     ('e_hate', dict(emotion='HATE')),
                     ('e_hope', dict(emotion='HOPE')),
                     ('e_love', dict(emotion='LOVE')),
                     ('e_pity/compassion', dict(emotion='PITY/COMPASSION')),
                     ('e_pride', dict(emotion='PRIDE')),
                     ('e_relief', dict(emotion='RELIEF')),
                     ('e_remorse', dict(emotion='REMORSE')),
                     ('e_resent', dict(emotion='RESENTMENT')),
                     ('e_sadness', dict(emotion='SADNESS')),
                     ('e_satisfaction', dict(emotion='SATISFACTION')),
                     ('e_shame', dict(emotion='SHAME')),
                     ('c_audio', dict(oncue='AUDIO')),
                     ('c_context', dict(oncue='CONTEXT')),
                     ('c_face', dict(oncue='FACE')),
                     ('c_gesture', dict(oncue='GESTURE')),
                     ('c_narrator', dict(oncue='NARRATOR')),
                     ('c_verbal', dict(oncue='VERBAL')),
                     ):
            ind.append(_get_modulation(rat, segments, character=char, **d))
            labels.append(l)
        ind = np.array(ind)
        # where is any above threshold agreement
        flags = np.abs(ind) >= thresh
        staging = None
        last_ind = np.array([False] * len(ind))
        # for each segment
        for i, f in enumerate(flags.T):
            # print i, f,
            if not np.sum(f):
                if staging:
                    ep.append(_postprocess(staging))
                    staging = None
                    # print 'commit',
                last_ind = f
                # print 'skip'
                continue
            # continuing episode?
            if np.all(f == last_ind):
                # end of annotation is end of current segment
                staging['end'] = segments[i, 1]
                for nl, l in enumerate(labels):
                    staging[l].append(ind[nl, i])
                # print 'extend'
            else:
                # new episode
                if staging:
                    # print 'commit',
                    ep.append(_postprocess(staging))
                # print 'new'
                staging = dict(start=segments[i, 0],
                               end=segments[i, 1])
                last_ind = f
                for nl, l in enumerate(labels):
                    staging[l] = [ind[nl, i]]

        episodes[char] = ep
    return episodes, labels


def emo2eventstsv(data, labels):
    # format output of `mk_thresh_emotion_episodes()` into a format that is
    # importable by Advene, while merging all episodes of all characters
    # into a single file
    episodes = []
    s = 'onset\tduration\tcharacter\tarousal\tvalence_positive\tvalence_negative\t'
    s += '\t'.join(l for l in sorted(labels) if not l in ('arousal', 'v_pos', 'v_neg'))
    s += '\n'
    for char, ep in data.items():
        for e in ep:
            e['character'] = char
            episodes.append(e)
    episodes = sorted(episodes, key=lambda x: x['start'])

    fmt = '{onset}\t{duration}\t{character}\t{arousal}\t{valence_positive}\t{valence_negative}\t'
    fmt += '\t'.join('{%s}' % l for l in sorted(labels) if not l in ('arousal', 'v_pos', 'v_neg'))
    fmt += '\n'
    for e in episodes:
        s += fmt.format(
                onset=e['start'],
                duration=e['end'] - e['start'],
                valence_positive=e['v_pos'],
                valence_negative=e['v_neg'],
                **e)
    return s

#
# Helpers
#


def get_unique_characters(rat):
    return np.unique(
        np.concatenate(
            [np.unique([a['character'] for a in an])
             for an in rat]))


def get_unique_emotions(rat):
    return [e for e in np.unique(
            np.concatenate(
                [np.unique(
                    np.concatenate([a['emotion'].split() for a in an]))
                    for an in rat])) if not '?' in e]


def get_unique_oncues(rat):
    return [e for e in np.unique(
            np.concatenate(
                [np.unique(
                    np.concatenate([a['oncue'].split() for a in an]))
                    for an in rat])) if not '?' in e]


def slice2segments(ratings, cond, segments):
    # compute a time series of inter-observer agreement wrt a particular
    # emotion property (or combinations thereof)
    # annotations given with start and stop time, are converted into a
    # timeseries with data point locations given by the sequence of
    # `segments`. Segments intersecting with a given annotation from an
    # individual observer are set to one, the rest to zero. The mean
    # across observers for any segment is returned
    slicer = np.zeros(len(segments))
    for rat in ratings:
        rslicer = np.zeros(len(segments))
        for e in rat:
            use = True
            for k, v in cond.items():
                if v == '*':
                    continue
                if k in ('oncue', 'offcue', 'emotion'):
                    if not v in e[k].split():
                        use = False
                else:
                    if not v == e[k]:
                        use = False
            if not use:
                continue
            select = np.logical_and(segments.T[1] > e['start'],
                                    segments.T[0] < e['end'])
            rslicer[select] += 1
        slicer += rslicer > 0
    slicer = slicer.astype(float) / len(ratings)
    return slicer


def get_timeseries(rat, urat, segments, char='*'):
    # yield time series representations of all relevant emotion attributes
    # from raw annotations
    vars = [get_arousal_modulation(rat, segments, char=char),
            get_valence_modulation(rat, segments, char=char),
            get_direction_modulation(rat, segments, char=char)]
    labels = ['arousal', 'valence', 'direction']
    for emo in get_unique_emotions(urat):
        vars.append(_get_modulation(rat, segments, emotion=emo, character=char))
        labels.append(emo.lower())
    for oc in get_unique_oncues(urat):
        vars.append(_get_modulation(rat, segments, oncue=oc, character=char))
        labels.append(oc.lower())
    return np.array(vars).T, labels


def _get_modulation(ratings, segments, **kwargs):
    return slice2segments(ratings, kwargs, segments)


def get_arousal_modulation(ratings, segments, char='*'):
    ts = _get_modulation(ratings, segments, character=char, arousal='HIGH') \
        - _get_modulation(ratings, segments, character=char, arousal='LOW')
    return ts


def get_valence_modulation(ratings, segments, char='*'):
    ts = _get_modulation(ratings, segments, character=char, valence='POS') \
        - _get_modulation(ratings, segments, character=char, valence='NEG')
    return ts


def get_direction_modulation(ratings, segments, char='*'):
    ts = _get_modulation(ratings, segments, character=char, direction='SELF') \
        - _get_modulation(ratings, segments, character=char, direction='OTHER')
    return ts


if __name__ == '__main__':
    # main function: compute stats, generate derived data, make figures
    import os
    from os.path import join as opj

    outpath = 'researchcut'
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    second_segments = get_nsecond_segments()

    avr = get_av_ratings()
    aor = get_ao_ratings()

    open(opj(outpath, 'emotions_av_1s_events.tsv'), 'w').write(
        emo2eventstsv(
            *mk_thresh_emotion_episodes(avr, .5, get_nsecond_segments(1))))
    open(opj(outpath, 'emotions_ao_1s_events.tsv'), 'w').write(
        emo2eventstsv(
            *mk_thresh_emotion_episodes(aor, .5, get_nsecond_segments(1))))
