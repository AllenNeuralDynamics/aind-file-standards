# Standards on FIP fiber photometry acquisition

## Version

`0.1.0`

## Introduction

This document describes the standards for the acquisition of frame-projected independent-fiber photometry (FIP) data in the Allen Institute for Neural Dynamics.

## Raw Data Format

Following SciComp standards, ecephys data from experiments should be saved to the "fib" modality folder.

### File format 

In most cases, FIP fiber photometry data will be stored in 3 CSV files (extracted traces + timestamp; 6 time-series) and 3 bin files (raw camera-detector movie file).

For example:

```plaintext
📦 fib
┣ FIP_DataG_2024-06-05T08_25_33.csv
┣ FIP_DataIso_2024-06-05T08_25_33.csv
┣ FIP_DataR_2024-06-05T08_25_33.csv
┣ FIP_RawG_2024-06-05T08_25_33.bin
┣ FIP_RawIso_2024-06-05T08_25_33.bin
┗ FIP_RawR_2024-06-05T08_25_33.bin
```
The file names are `FIP_[channel-name]_[datetime].csv`.  The `[channel-name]` token can be one of the following:

* `DataG`: data for green channel
* `DataR`: data for red channel
* `DataIso`: data for isosbestic channel
  
#### CSV files

These files contain photometry readouts. The files have no headers. Each column is a timeseries, ordered as follows:

* timestamp (in millisecond, total time of the day)
* ROI0 (corresponding to fiber branch1) values
* ROI1 (corresponding to fiber branch2) values
* ...  (depending on how many fibers are used; in most of the experiments: ROI0-3/4branches)
* Blank ROI: CMOS dark count floor signal

#### BIN files

These are movies that document the fiber implants during the recording.

[TBD - how to interpret these files?]

* 200x200 pixels
* 16bit depth
* 20Hz (effective sampling frequency per channel)
* column major

These files are optional and may be removed once QC is complete. 

### Application notes

The .bin binary files are raw CMOS movie data recorded with `MatrixWriter` Bonsai node (https://bonsai-rx.org/docs/api/Bonsai.Dsp.MatrixWriter.html).

The photometry data is generated...

### Relationship to aind-data-schema

procedures.json documents the relevant fiber probe implantation metadata (stereotactic coordinates) and viral injection metadata (stereotactic coordinates, materials). session.json documents the intended measurement (e.g. norepinephrine, dopamine, etc) for each channel of each probe. 

### File Quality Assurances

Identical to the `File Quality Assurances` section in the `Acquisition/Raw Data Format` section.

