# Standards on FIP fiber photometry acquisition

## Version

`0.2.1`

## Introduction

This document describes the standards for the acquisition of frame-projected independent-fiber photometry (FIP) data in the Allen Institute for Neural Dynamics.

## Raw Data Format

Following SciComp standards, FIP data should be saved in their own folder named "fib" (short for "fiber photometry"). Data from other modalities go in separate folders.

### File format 

In most cases, FIP fiber photometry data will be stored in 3 photometry readout CSV files (extracted traces + timestamp; 6 time-series), 3 bin files (raw camera-detector movie file), and 2 ROI coordinate CSVs.

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

These files contain photometry readouts. Each row describes the average signal of pixels within each ROI for a single video frame. The values are computed online during data acquisition. The files have no headers. Each column is a timeseries, ordered as follows:

* `timestamp` (software timestamp, in milliseconds, total time of the day)
* `ROI0` (corresponding to fiber branch1) values
* `ROI1` (corresponding to fiber branch2) values
* `...`  (depending on how many fibers are used; in most of the experiments: ROI0-3/4branches)
* `Blank ROI`: CMOS dark count floor signal

#### ROI Coordinate CSV files

The ROI CSV files contain the vector representation of the ROIs used to integrate BIN video signal. The files have no headers. 
There is one CSV file per camera, corresponding to G and Iso (time-multiplexing) and the other camera is recording only R. 
The CSV files can be used to reconstitute images like this:

![image](https://github.com/user-attachments/assets/30900798-5d51-43ba-99fc-41b07d4a75dd)

Each row of a CSV is a point position in an ROI. The columns are, in this order:
* `RoiIndex`: 0->N index of which ROI the point lives on
* `PointIndex`: 0->N index of the point within an ROI
* `X`: pixel coordinate of the ROI point on the first (horizontal) dimension of the video 
* `Y`: pixel coordinate of the ROI point on the second (vertical) dimension of the video

#### BIN files

These are movies that document the fiber implants during the recording. During data acquisition, operators place circular ROIs 
over the videos. The photometry readouts above are integrated signal inside these ROIs.

* 200x200 pixels
* 16bit depth
* 20Hz (effective sampling frequency per channel)
* column major

These files are optional and may be removed once QC is complete. Quality Control consists of verifying that ROIs were placed in the
correct location, and not, for example, shifted with respect to the visual display on the rig due to e.g. physical bumping of the hardware.

These files can be read by specifying the structure of the videos as follows:

```code
import numpy as np

frame_width = 200
frame_height = 200
bit_depth = 16  # 16-bit
dtype = np.uint16  # 16-bit
frame_size = frame_width * frame_height * 2

def load_average_frame(video_file, start_frame, end_frame, frame_size, dtype, frame_width, frame_height):
    
    Parameters:
        video_file (str): Path to the video file.
        start_frame (int): Index of the starting frame.
        end_frame (int): Index of the ending frame (exclusive).
        frame_size (int): Byte size of a single frame.
        dtype (numpy.dtype): Data type of the frame.
        frame_width (int): Width of the frame.
        frame_height (int): Height of the frame.

    Returns:
        numpy.ndarray: Average image (frame_height x frame_width).
    """
    num_frames = end_frame - start_frame
    if num_frames <= 0:
        raise ValueError("Invalid frame range specified.")
    
    accumulated_frame = np.zeros((frame_height, frame_width), dtype=np.float64)
    
    with open(video_file, "rb") as f:
        for frame_index in range(start_frame, end_frame):
            f.seek(frame_index * frame_size)
            frame_data = np.frombuffer(f.read(frame_size), dtype=dtype)
            
            if frame_data.size != frame_width * frame_height:
                raise ValueError("Reached end of file.")
            
            accumulated_frame += frame_data.reshape((frame_height, frame_width))
    
    return (accumulated_frame / num_frames).astype(dtype)
```

### Application notes

The .bin binary files are raw CMOS movie data recorded with `MatrixWriter` Bonsai node (https://bonsai-rx.org/docs/api/Bonsai.Dsp.MatrixWriter.html).

When plotting ROI points on a video in matplotlib, the Y coordinate must be flipped vertically relative to the video frame. 

### Relationship to aind-data-schema

procedures.json documents the relevant fiber probe implantation metadata (stereotactic coordinates) and viral injection metadata (stereotactic coordinates, materials). session.json documents the intended measurement (e.g. norepinephrine, dopamine, etc) for each channel of each probe. 

### File Quality Assurances

None.

