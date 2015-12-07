Stimulus annotations
====================

This repository collects stimulus annotations for the research cut of the
"Forrest Gump" movie used in the `studyforrest.org project
<http://studyforrest.org>`_. Most files are in plain text format with
comma-separated value (CSV) markup.  All time stamps are given in seconds from
movie start.  Here is an overview of the annotations:

Stimulus structure (``structure/``)
  Annotations for movie/stimulus structure segmentation.

  - ``scenes.csv``

    Consecutive movie segments that take place in the same location/setting.
    Plain text comma-separated value file. Columns: start time, location label,
    time of day (day or night), setting (interior or exterior)

  - ``shots.csv``

    Consecutive movie segment without a "cut".  Cuts were initially detected
    using an automated procedure and later curated by hand.  Plain text file.
    Single column: start time.

  - ``segments.csv``

    Segments of the movie used for the eight individual acquisitions runs.
    Plain text comma-separated value file. Columns: start time, end time, ID.

  - ``fmri_segments.csv``

    Same as "movie segments", but start and end times match the start of an
    fMRI volume acquisition start. This segmentation represents the actual
    segment timing used for the fMRI acquisitions except for the inter-segment
    transition. Plain text comma-separated value file. Columns: start time, end
    time, ID.

Speech (``speech/``)
  Spoken words in the movie.

  - ``german_audio_description.csv``

    German audio description in the Forrest Gump audio movie.  This transcript
    contains all information on the audio-movie content that cannot be inferred
    from the DVD release. Plain text comma-separated value file. Columns: start
    time, end time, text of the audio description.

  - ``german_dialog.csv`` **[work in progress]**

    All German dialog (present in both the audio and audio-visual movie).
    Plain text comma-separated value file. Columns: start time, end time, person
    label, text of the dialog.

  - ``english_dialog.csv`` **[work in progress]**

    Same as the German dialog, but for the original English soundtrack.
    Plain text comma-separated value file. Columns: start time, end time, person
    label, text of the dialog.

Audio (``audio/``)
  "Low-level" auditory movie content.

  - ``music.csv`` **[work in progress]**

    Description of all musical excerpts in the soundtrack.
    Plain text comma-separated value file. Columns: start time, end time, artist
    label, title, background flag.

    An artist label of ``OST`` indicated 'original sound track' and indicates
    a musical pieces that was composed for the movie, as opposed to songs from
    other artists that have been re-used for the soundtrack.

    The background flag indicates whether a musical piece is presented in the
    auditory foreground or whether it is presented as background music
    underneath other simultaneously presented salient auditory content.

  - ``non_speech_vocalization.csv`` **[work in progress]**

    Sounds produced with a human voice that are not speech.

Portrayed emotions
  Various properties of portrayed emotion (via visual and auditory cues).

  - ``emotions``, ``src/emotions``

    Characterization of the temporal location and duration of portrayed
    emotions by independent 12 observers. The nature of an emotion was
    characterized with basic attributes, such as arousal and valence, as well
    as 22 explicit emotion category labels. In addition, annotations include a
    record of the perceptual evidence for the presence of an emotion. Both
    variant of the stimulus (audio-only and auto-visual) were annotated
    separately. In addition to raw annotations, aggregate time series of
    inter-observer agreement are provided that can be used as probabilistic
    indicators of particular attributes of portrayed emotions. All data is
    provided as plain text (comma-separated value) tables.

    A detailed data descriptor has been published in `F1000Research
    <http://dx.doi.org/10.12688/f1000research.6230.1>`_.

    Labs, A., Reich, T., Schulenburg, H., Boennen, M., Gehrke, M., Golz, M.,
    Hartings, B., Hoffmann, N., Keil, S., Perlow, M., Peukmann, A. K., Rabe, L.
    N., von Sobbe, F.-R. & Hanke, M. (2015). `Portrayed emotions in the movie
    “Forrest Gump”. F1000Research, 4:92
    <http://f1000research.com/articles/4-92>`_.
