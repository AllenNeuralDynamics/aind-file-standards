# Standards on FIP fiber photometry acquisition

## Version

`0.2.0`

## Introduction

This document describes the standards for the acquisition of frame-projected independent-fiber photometry (FIP) data in the Allen Institute for Neural Dynamics.

## Raw Data Format

Following SciComp standards, FIP data should be saved in their own folder named "fib" (short for "fiber photometry"). Data from other modalities go in separate folders.

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
┣ FIP_RawR_2024-06-05T08_25_33.bin
┣ FIP_ROIsG-Iso_2024-06-05T08_25_33.csv
┗ FIP_ROIsR_2024-06-05T08_25_33.csv
```
The file names are `FIP_[channel-name]_[datetime].csv`.  The `[channel-name]` token can be one of the following:

* `DataG`: data for green channel
* `DataR`: data for red channel
* `DataIso`: data for isosbestic channel
  
#### Photometry Readout CSV files

These files contain photometry readouts. The files have no headers. Each column is a timeseries, ordered as follows:

* `timestamp` (in millisecond, total time of the day)
* `ROI0` (corresponding to fiber branch1) values
* `ROI1` (corresponding to fiber branch2) values
* `...`  (depending on how many fibers are used; in most of the experiments: ROI0-3/4branches)
* `Blank ROI`: CMOS dark count floor signal

#### BIN files

These are movies that document the fiber implants during the recording. During data acquisition, operators place circular ROIs 
over the videos. The photometry readouts above are integrated signal inside these ROIs.

* 200x200 pixels
* 16bit depth
* 20Hz (effective sampling frequency per channel)
* column major

These files are optional and may be removed once QC is complete. Quality Control consists of verifying that ROIs were placed in the
correct location, and not, for example, shifted with respect to the visual display on the rig due to e.g. physical bumping of the hardware.

#### ROI CSV files

The ROI CSV files contain the vector representation of the ROIs used to integrate BIN video signal. There is one CSV file per camera, corresponding to G and Iso 
(time-multiplexing) and the other camera is recording only R. The CSV files can be used to reconstitute images like this:

![image](https://github.com/user-attachments/assets/30900798-5d51-43ba-99fc-41b07d4a75dd)

Each row of a CSV is a point position. The columns are, in this order:
* `RoiIndex`: 0->N index of which ROI the point lives on
* `PointIndex`: 0->N index of the point within an ROI
* `X`: horizontal position of the point
* `Y`: vertical position of the point

### Application notes

The .bin binary files are raw CMOS movie data recorded with `MatrixWriter` Bonsai node (https://bonsai-rx.org/docs/api/Bonsai.Dsp.MatrixWriter.html).

### Relationship to aind-data-schema

procedures.json documents the relevant fiber probe implantation metadata (stereotactic coordinates) and viral injection metadata (stereotactic coordinates, materials). session.json documents the intended measurement (e.g. norepinephrine, dopamine, etc) for each channel of each probe. 

### File Quality Assurances

None.

