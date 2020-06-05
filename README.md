[![made-with-datalad](https://www.datalad.org/badges/made_with.svg)](https://datalad.org)

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

## DataLad datasets and how to use them

This repository is a [DataLad](https://www.datalad.org/) dataset
dataset (id: 45b9ab26-07fc-11e8-8c71-f0d5bf7b5561). It provides
fine-grained data access down to the level of individual files, and allows for
tracking future updates. In order to use this repository for data retrieval,
[DataLad](https://www.datalad.org/) is required. It is a free and
open source command line tool, available for all major operating
systems, and builds up on Git and [git-annex](https://git-annex.branchable.com/)
to allow sharing, synchronizing, and version controlling collections of
large files. You can find information on how to install DataLad at
[handbook.datalad.org/en/latest/intro/installation.html](http://handbook.datalad.org/en/latest/intro/installation.html).

### Get the dataset

A DataLad dataset can be `cloned` by running

```
datalad clone <url>
```

Once a dataset is cloned, it is a light-weight directory on your local machine.
At this point, it contains only small metadata and information on the
identity of the files in the dataset, but not actual *content* of the
(sometimes large) data files.

### Retrieve dataset content

After cloning a dataset, you can retrieve file contents by running

```
datalad get <path/to/directory/or/file>`
```

This command will trigger a download of the files, directories, or
subdatasets you have specified.

DataLad datasets can contain other datasets, so called *subdatasets*.
If you clone the top-level dataset, subdatasets do not yet contain
metadata and information on the identity of files, but appear to be
empty directories. In order to retrieve file availability metadata in
subdatasets, run

```
datalad get -n <path/to/subdataset>
```

Afterwards, you can browse the retrieved metadata to find out about
subdataset contents, and retrieve individual files with `datalad get`.
If you use `datalad get <path/to/subdataset>`, all contents of the
subdataset will be downloaded at once.

### Stay up-to-date

DataLad datasets can be updated. The command `datalad update` will
*fetch* updates and store them on a different branch (by default
`remotes/origin/master`). Running

```
datalad update --merge
```

will *pull* available updates and integrate them in one go.

### More information

More information on DataLad and how to use it can be found in the DataLad Handbook at
[handbook.datalad.org](http://handbook.datalad.org/en/latest/index.html). The chapter
"DataLad datasets" can help you to familiarize yourself with the concept of a dataset.
