# Standards on FIP fiber photometry acquisition

## Version

`0.1.0`

## Introduction
This document describes the standards for the acquisition of frame-projected independent-fiber photometry (FIP) data acquired with "StimIntegratedRigs", dedicated FIP rigs for Ophys_IndicatorBenchmarking project in the Allen Institute for Neural Dynamics. StimIntegratedRigs are using HARP behavior board to trigger behavaior cameras but are not using HARP system for aligning FIP data and Optogenetic stimulations. Instead, Optogenetic Stimulation is directly controled by the same microcontroller, Teensy as the one used for FIP control (both 2 excitation LEDs and a CMOS), and thus, they are already time aligned. Data acquisition codes can be found in this [repo](https://github.com/AllenNeuralDynamics/Ophys_SensorScreening_ExperimetalControl) (to be better organized)

## Raw Data Format
Following SciComp standards, FIP data should be saved in their own folder named "fib" (short for "fiber photometry"). Data from other modalities go in separate folders.
In older dataset, individual files are all stored directly under each session folder.

### File format 
In most cases, FIP data will be saved in `CSV` files, where each file corresponds to a different channel in the photometry rig. In addition to the timeseries fluorescence data, files containing metadata and raw image data are also available. A single session of FIP data should be organized under the `fib` directory. An acquisition for a single session should be nested under a sub directory named following the core standards for file naming convention found [here](https://github.com/AllenNeuralDynamics/aind-file-standards/blob/main/core/core-standards.md#filename-conventions).  Mostly, this is for cases where the recording gets interrupted. When the system restarts under the same session, it can be added to a new folder. A sessions folder structure should look like the following:

### Old 
```plaintext
📦 Session Folder
┣ Signal_YYYY-MM-DDTHH_MM_SS.csv
┣ Iso_YYYY-MM-DDTHH_MM_SS.csv
┣ Stim_YYYY-MM-DDTHH_MM_SS.csv
┣ Raw_Signal_YYYY-MM-DDTHH_MM_SS.bin
┣ Raw_Iso_YYYY-MM-DDTHH_MM_SS.bin
┣ Raw_Stim_YYYY-MM-DDTHH_MM_SS.bin
┣ TS_FLIR_YYYY-MM-DDTHH_MM_SS.csv
┗ FIP_ROI_YYYY-MM-DDTHH_MM_SS.csv
```

### New 
```plaintext
📦 Session Folder
┣ 📂 <fib>
┃ ┣ Signal_YYYY-MM-DDTHH_MM_SS.csv
┃ ┣ Iso_YYYY-MM-DDTHH_MM_SS.csv
┃ ┣ Stim_YYYY-MM-DDTHH_MM_SS.csv
┃ ┣ Raw_Signal_YYYY-MM-DDTHH_MM_SS.bin
┃ ┣ Raw_Iso_YYYY-MM-DDTHH_MM_SS.bin
┃ ┣ Raw_Stim_YYYY-MM-DDTHH_MM_SS.bin
┃ ┣ TS_FLIR_YYYY-MM-DDTHH_MM_SS.csv
┃ ┗ FIP_ROI_YYYY-MM-DDTHH_MM_SS.csv
┃
┣ 📂 <behavior>
```


#### Fluorescence data
Data is generally organized by the emission channel that gave rise to the data (`Signal`, `Iso`, and `Stim`), respectively, in this order. 

```
             --->|   |<--- period = 16.67 ms
Blue/Yellow LED  ████░░░░░░░░░░░████░░░░░░░░░░░████░░░░░░░░░░░████░░░░░░░░░░░████░░░░░░░░░░░

Iso LED (415)    ░░░░░████░░░░░░░░░░░████░░░░░░░░░░░████░░░░░░░░░░░████░░░░░░░░░░░████░░░░░░

Stim Laser       ░░░░░░░░░░████░░░░░░░░░░░████░░░░░░░░░░░████░░░░░░░░░░░████░░░░░░░░░░░████░

Single CMOS      ████░████░████░████░████░████░████░████░████░████░████░████░████░████░████░  

                ───────────────────────────────────────────────────────────────────────────►
                                    Time
```

#### Raw sensor data

Raw sensor data (i.e., camera frames) that generated the fluorescence data is saved in raw binary files. These files share the same naming convention as the fluorescence data files, but with a `.bin` extension. During acquisition, operators place circular ROIs over the images, and photometry readouts are obtained by averaging the signal inside these regions.

To open these files, users need additional information to parse the binary data. Data is stored in a `ColumnMajor` layout format, where each frame can be parsed with the information available in the corresponding `.json` file. Each `.json` file contains the following fields:

* `Width`: Imaging width (100 px by default) Note, not 200 px
* `Height`: Imaging height (100 px by default) Note, not 200 px 
* `Depth`: Bit depth (U16 by default)
* `Channel`: Channel (1 channel by default)

See the Application notes below for an example of how to parse the binary files.


### Application notes

#### Parsing raw binary files

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
        metadata = j.read()[0]
    metadata = json.load(metadata)
    video_fp = '/path/to/file.bin'
    start_frame = 0
    end_frame = 1000
    average_frame = load_average_frame(
        video_fp,
        start_frame,
        end_frame,
        frame_width * frame_height * np.dtype(metadata['Depth']).itemsize,
        np.dtype(metadata['Depth']),
        metadata['Width'],
        metadata['Height']
    )
```

#### Acquiring data under this format

Data acquisition code that generates data in this format is available from the [data acquisition repository](https://github.com/AllenNeuralDynamics/FIP_DAQ_Control).

### Relationship to aind-data-schema

procedures.json documents the relevant fiber probe implantation metadata (stereotactic coordinates) and viral injection metadata (stereotactic coordinates, materials). session.json documents the intended measurement (e.g. norepinephrine, dopamine, etc) for each channel of each probe. 

