# Standards on FIP fiber photometry acquisition

## Version

`0.2.2`

## Introduction

This document describes the standards for the acquisition of frame-projected independent-fiber photometry (FIP) data in the Allen Institute for Neural Dynamics.

## Raw Data Format

Following SciComp standards, FIP data should be saved in their own folder named "fib" (short for "fiber photometry"). Data from other modalities go in separate folders.

### File format 

In most cases, FIP fiber photometry data will be stored in 3 photometry readout CSV files (extracted traces + timestamp; 6 time-series), 3 bin files (raw camera-detector movie file), and 2 ROI coordinate CSVs.

For example:

```plaintext
📦 fib
┣📂 SoftwareEvents
┃ ┣📜RepositoryStatus.json
┃ ┗📜Region.json
┣ green.csv
┣ red.csv
┣ iso.csv
┣ green.bin
┣ red.bin
┣ iso.bin
┣ roi_green_iso.csv
┣ roi_red.csv
┣ camera_green_iso_metadata.csv
┗ camera_red_metadata.csv
```

#### Photometry CSV files

Data files are named by the color of the channel.

* `green.csv`: data for green channel
* `red.csv`: data for red channel
* `iso.csv`: data for isosbestic channel

These files contain photometry readouts. Each row describes the average signal of pixels within each ROI for a single video frame. The values are computed online during data acquisition. These are the string header values required for each csv. Each column is a timeseries defined below:

* `SoftwareTS` (software timestamp, in milliseconds, total time of the day)
* `Fiber_0` Average signal values for Fiber_0's selected ROI.
* `...`  
* `Fiber_N` Average signal values for Fiber_N's selected ROI.
* `Background`: CMOS dark count floor signal
* `HarpTS` (Harp timestamp, in XXXunit, from Harp device reference)


#### ROI Coordinate CSV files

The ROI CSV files contain the vector representation of the ROIs used to integrate BIN video signal. 

There is one CSV file per camera, corresponding to G and Iso (time-multiplexing) and the other camera is recording only R. 

* `roi_green_iso.csv`: ROI metadata for the green and isosbestic channels
* `roi_red.csv`: ROI metadata for the red channel

Each row of a CSV is a point position in an ROI. Column headers defined below must be included in the csv:

* `RoiIndex`: 0->N index of which ROI the point lives on
* `PointIndex`: 0->N index of the point within an ROI
* `X`: pixel coordinate of the ROI point on the first (horizontal) dimension of the video 
* `Y`: pixel coordinate of the ROI point on the second (vertical) dimension of the video

The CSV files can be used to reconstitute images like this:

![image](https://github.com/user-attachments/assets/30900798-5d51-43ba-99fc-41b07d4a75dd)




#### BIN files

Data files are named by the color of the channel.

* `green.bin`: data for green channel
* `red.bin`: data for red channel
* `iso.bin`: data for isosbestic channel

These are movies that document the fiber implants during the recording. During data acquisition, operators place circular ROIs 
over the videos. The photometry readouts above are integrated signal inside these ROIs.

* 200x200 pixels
* 16bit depth
* 20Hz (effective sampling frequency per channel)
* column major

These files are optional and may be removed once QC is complete. Quality Control consists of verifying that ROIs were placed in the
correct location, and not, for example, shifted with respect to the visual display on the rig due to e.g. physical bumping of the hardware.

These files can be read by specifying the structure of the videos as follows:

```python
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

### Software Events

Software events contain XXX(regions are already stored in csv and are not an event. What is the RepositoryStatus?) 

### Metadata

The fiber imaging system uses a single camera to capture data from two distinct light sources through temporal multiplexing. Because of that, only two metadata files are dropped; one for each camera. The temporally multiplexed channels are indicated in the file naming format below. These files can be used to QC the cameras.

* `camera_green_iso_metadata.csv`: metadata from the camera recording from both green and iso channels
* `camera_red_metadata.csv`: metadata from the camera recording from the red channel

Within the metadata files are the following columns

* `CameraFrameNumber` Camera frame number provided by camera hardware
* `ReferenceTime` Camera reference time XXX more description here
* `CameraFrameTime`  XXX
* `CpuTime`  Software timestamp from the OS, in timezone (XXX)

### Application notes

The .bin binary files are raw CMOS movie data recorded with `MatrixWriter` Bonsai node (https://bonsai-rx.org/docs/api/Bonsai.Dsp.MatrixWriter.html).

When plotting ROI points on a video in matplotlib, the Y coordinate must be flipped vertically relative to the video frame. 

### Relationship to aind-data-schema

procedures.json documents the relevant fiber probe implantation metadata (stereotactic coordinates) and viral injection metadata (stereotactic coordinates, materials). session.json documents the intended measurement (e.g. norepinephrine, dopamine, etc) for each channel of each probe. 

### File Quality Assurances

None.

