# Stimulus annotations for the movie Forrest Gump

This repository collects stimulus annotations for the research cut of the
"Forrest Gump" movie used in the [studyforrest.org
project](http://studyforrest.org).  Annotations are collected from
various contributors and publications.

Annotations are typically provided as plain text tables, using a
tab-separated-value markup with a header row. Table usually contain a *onset*
and a *duration* column to indicate the timing of an event.  All other columns
contain variables that describe properties of an event.

## Repository content

- `code/`

  All code necessary to import and convert annotations from the formats they
  were originally provided in.

- `researchcut/`

  Annotation plain text tables with timing matching the entire "research cut"
  as one continuous piece.

- `segments/`

  Annotation plain text tables with timing matching individual movie segments
  used in the studyforrest.org project.

- `src/`

  Datalad subdatasets referencing repositories with available annotations.

- `old/` (deprecated)

  Previously provided, less uniformly structured, annotation. All of these
  will eventually be replaced by the format described above. This directory
  will be removed in the future

## General information

This is a DataLad dataset (id: 45b9ab26-07fc-11e8-8c71-f0d5bf7b5561).

For more information on DataLad and on how to work with its datasets,
see the DataLad documentation at: http://docs.datalad.org
