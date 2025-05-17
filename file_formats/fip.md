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
┣ green.csv
┣ red.csv
┣ iso.csv
┣ green.bin
┣ red.bin
┣ iso.bin
┣ roi_green_iso.csv
┣ roi_red.csv
┣ camera_green_iso_metadata.csv
┣ camera_red_metadata.csv
┗ regions.json
```

### CSV Files

The fiber photometry rig outputs CSV files containing metadata and data. All metadata and data files must contain headers. The order of the headers will not be enforced. Documented below for each type of CSV, the file and header names are specified.

#### Photometry CSV files

Data files are named by the color of the channel and contain the photometry readouts.

* `green.csv`: data for green channel
* `red.csv`: data for red channel
* `iso.csv`: data for isosbestic channel

Each row describes the average signal of pixels within each ROI for a single video frame. The values are computed online during data acquisition. The headers include:

* `Fiber_0` Average signal values for Fiber_0's selected ROI.
* `...`  
* `Fiber_N` Average signal values for Fiber_N's selected ROI.
* `Background`: CMOS dark count floor signal
* `ReferenceTime` Time of the trigger given by hardware (Harp)
* `CameraFrameNumber` Frame counter given by the camera API or manually added by user (e.g. using OS counter for webcams)
* `CameraFrameTime` frame acquisition time given by the camera API.


#### ROI metadata files

Three files contain the metadata for each channel:

* `roi.meta`: ROI metadata for the green and isosbestic channels
* `green.meta`: ROI metadata for the red channel
* `iso.meta`: Metadata

Each file contains a datastructure with the following fields:

* `Width`: Imaging width
* `Height`: Imaging height
* `Depth`: Bit depth
* `Channel`: Channel

Example structure:

```
{
    Width=200, 
    Height=200, 
    Depth=U16, 
    Channels=1
}
```


### JSON files

#### Regions

This json file contains the ROI coordinates. The coordinates are given by the center (x,y) coordinate and the radius of the ROI in pixels.

```
{
    "camera_green_iso_background": {
        "center": {
            "x": 10.0,
            "y": 10.0
        },
        "radius": 10.0
    },
    "camera_red_background": {
        "center": {
            "x": 10.0,
            "y": 10.0
        },
        "radius": 10.0
    },
    "camera_green_iso_roi": [
        {
            "center": {
                "x": 50.0,
                "y": 50.0
            },
            "radius": 20.0
        },
        {
            "center": {
                "x": 50.0,
                "y": 150.0
            },
            "radius": 20.0
        },
        {
            "center": {
                "x": 150.0,
                "y": 50.0
            },
            "radius": 20.0
        },
        {
            "center": {
                "x": 150.0,
                "y": 150.0
            },
            "radius": 20.0
        }
    ],
    "camera_red_roi": [
        {
            "center": {
                "x": 50.0,
                "y": 50.0
            },
            "radius": 20.0
        },
        {
            "center": {
                "x": 50.0,
                "y": 150.0
            },
            "radius": 20.0
        },
        {
            "center": {
                "x": 150.0,
                "y": 50.0
            },
            "radius": 20.0
        },
        {
            "center": {
                "x": 150.0,
                "y": 150.0
            },
            "radius": 20.0
        }
    ]
}
```

An image like the one below can be drawn from these coordinates

![image](https://github.com/user-attachments/assets/30900798-5d51-43ba-99fc-41b07d4a75dd)

### BIN files

Data files are named by the color of the channel.

* `green.bin`: data for green channel
* `red.bin`: data for red channel
* `iso.bin`: data for isosbestic channel

These are movies that document the fiber implants during the recording. During data acquisition, operators place circular ROIs over the videos. The photometry readouts above are integrated signal inside these ROIs.

These files are optional and may be removed once QC is complete. Quality Control consists of verifying that ROIs were placed in the
correct location, and not, for example, shifted with respect to the visual display on the rig due to e.g. physical bumping of the hardware.

These files can be read by specifying the structure of the videos as follows:

```python
import numpy as np
import json


def load_average_frame(video_file, start_frame, end_frame, frame_size, dtype, frame_width, frame_height):
    """
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


if __name__ == '__main__':
    with open('red.meta', 'r') as j:
        meta_data = j.read()[0]
    meta_data = json.load(metadata)
    video_fp = '/path/to/file.bin'
    start_frame = 0
    end_frame = 1000
    average_frame = load_average_frame(
        video_fp,
        start_frame,
        end_frame,
        np.dtype(meta['Depth']),
        meta['Width'],
        meta['Height']
    )
```

### Metadata

The fiber imaging system uses a single camera to capture data from two distinct light sources through temporal multiplexing. Because of that, only two metadata files are dropped; one for each camera. The temporally multiplexed channels are indicated in the file naming format below. These files can be used to QC the cameras.

* `camera_green_iso_metadata.csv`: metadata from the camera recording from both green and iso channels
* `camera_red_metadata.csv`: metadata from the camera recording from the red channel

Within the metadata files are the following columns

* `ReferenceTime` Time of the trigger given by hardware (Harp)
* `CameraFrameNumber` Frame counter given by the camera API or manually added by user (e.g. using OS counter for webcams)
* `CameraFrameTime` Fame acquisition time given by the camera API or manually added by the user (e.g. using OS scheduler for webcams)
* `CpuTime`  Software timestamp from the OS, in timezone-aware ISO8061 format. Users should consider these timestamps low-precision and rig-dependent, and should not rely on them for analysis.

### Application notes

The .bin binary files are raw CMOS movie data recorded with `MatrixWriter` Bonsai node (https://bonsai-rx.org/docs/api/Bonsai.Dsp.MatrixWriter.html).

When plotting ROI points on a video in matplotlib, the Y coordinate must be flipped vertically relative to the video frame. 

### Relationship to aind-data-schema

procedures.json documents the relevant fiber probe implantation metadata (stereotactic coordinates) and viral injection metadata (stereotactic coordinates, materials). session.json documents the intended measurement (e.g. norepinephrine, dopamine, etc) for each channel of each probe. 

### File Quality Assurances

None.

