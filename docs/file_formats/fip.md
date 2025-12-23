# Standards on FIP fiber photometry acquisition

## Version

`0.5.0`

## Introduction

This document describes the standards for the acquisition of frame-projected independent-fiber photometry (FIP) data in the Allen Institute for Neural Dynamics.

## Terminology

This document uses specific terminology to distinguish between different components of the FIP system:

* **Fibers**: Optical fibers surgically implanted in the mouse's brain. Mice have variable numbers of implanted fibers depending on scientific requirements. Fiber implantation details (locations, stereotactic coordinates) should be documented in metadata. See the 'Relationship to aind-data-schema' section below for details on how this is documented in the aind-data-schema.

* **Patch cords**: Fiber optic cables that are permanently part of the FIP hardware system. The current FIP system has exactly 4 patch cords, but the file standard is agnostic to this number. At experiment time, experimenters physically connect patch cords to implanted fibers. Not all patch cords are necessarily connected during every experiment.

* **Fiber bundle**: The assembly of all patch cords whose termini are visible to the imaging cameras.

* **ROIs (Regions of Interest)**: Circular regions drawn on the camera image over the visible ends of the patch cords in the fiber bundle. Each ROI defines the camera area used to extract a timeseries.

Numbering on fibers, patch cords and ROIs is always 0-indexed.

**Notation**: Throughout this document, we use:
- **N** to represent the total number of implanted fibers in a given mouse (1 ≤ N ≤ K)
- **K** to represent the total number of patch cords/ROIs defined by the hardware (current rigs use K = 4, but this document is written to allow other values)
- **n** to represent a fiber index (0-based, n ∈ {0, …, N-1})
- **k** to represent a patch cord/ROI index (0-based, k ∈ {0, …, K-1})

The mapping between ROIs and patch cords is implicitly defined by the software (ROI_k is drawn over patch_cord_k). However, the mapping between patch cords and implanted fibers is determined by the experimenter at the time of the experiment and should be documented in metadata (see the "Relationship to aind-data-schema" section below for more detail).

## Raw Data Format

Following SciComp standards, FIP data should be saved in their own folder named "fib" (short for "fiber photometry"). Data from other modalities go in separate folders.

### File format 

In most cases, FIP data will be saved in `CSV` files, where each file corresponds to a different channel in the photometry rig. In addition to the timeseries fluorescence data, files containing metadata and raw image data are also available. A single session of FIP data should be organized under a the `fib` directory. An acquisition for a single session should be nested under a sub directory named following the core standards for file naming convention found [here](https://github.com/AllenNeuralDynamics/aind-file-standards/blob/main/core/core-standards.md#filename-conventions).  Mostly, this is for cases where the recording gets interrupted. When the system restarts under the same session, it can be added to a new folder. A sessions folder structure should look like the following:

```plaintext
📦 fib
┣ 📂 <fip_YYYY-MM-DDTHHMMSS>
┃ ┣ green.csv
┃ ┣ red.csv
┃ ┣ iso.csv
┃ ┣ green.bin
┃ ┣ red.bin
┃ ┣ iso.bin
┃ ┣ [Optional]background_green.bin
┃ ┣ [Optional]background_red.bin
┃ ┣ [Optional]background_iso.bin
┃ ┣ [Optional]background_green.csv
┃ ┣ [Optional]background_red.csv
┃ ┣ [Optional]background_iso.csv
┃ ┣ green_metadata.json
┃ ┣ red_metadata.json
┃ ┣ iso_metadata.json
┃ ┣ camera_green_iso_metadata.csv
┃ ┣ camera_red_metadata.csv
┃ ┗ regions.json
┗ 📂 <fip_YYYY-MM-DDTHHMMSS>
  ┣ green.csv
  ┣ <...>
  ┗ regions.json
```

Data is generally organized by the emission channel that gave rise to the data (`green`, `red`, and `iso`), respectively. For details on the rig setup, please refer to the [data acquisition repository](https://github.com/AllenNeuralDynamics/FIP_DAQ_Control).

#### Fluorescence data

Each fiber photometry session will primarily be analyzed by using the average signal from regions of interest (ROIs) placed on top of raw video frames during acquisition. To simplify analysis, we average the signal from all pixels within the ROIs during online acquisition and make it available as time series data in `CSV` files. These are `green.csv`, `red.csv`, and `iso.csv` files, respectively. All files share the same format, where each row corresponds to a single frame of the video and each column can be described as follows:

* `ReferenceTime` Time of the trigger given by hardware (Harp)
* `CameraFrameNumber` Frame counter given by the camera API
* `CameraFrameTime` Frame acquisition time given by the camera API
* `Background` CMOS dark count floor signal
* `Fiber_0`, `Fiber_1`, …, `Fiber_{K-1}` Average signal values from patch_cord_k's ROI (one column per patch cord/ROI)

Note: There are always exactly K `Fiber_n` columns (n = 0 … K-1) corresponding to the configured patch cords and ROIs for the rig. If N < K (where N is the number of implanted fibers), then patch cords N through K-1 are unused and their corresponding columns contain data from unconnected patch cords.

**Note on naming convention**: The column names `Fiber_0`, `Fiber_1`, …, `Fiber_{K-1}` are somewhat misleading - these columns actually represent data from patch_cord_0, patch_cord_1, …, patch_cord_{K-1}, respectively. The naming persists for backward compatibility. The relationship between patch cords and implanted fibers in the mouse is not captured in this file format and should be documented separately in metadata (see Relationship to aind-data-schema section below). If N < K (where N is the number of implanted fibers), then patch cords N through K-1 are unused and their corresponding columns contain data from unconnected patch cords.

#### Raw sensor data

Raw sensor data (i.e., camera frames) that generated the fluorescence data is saved in raw binary files. These files share the same naming convention as the fluorescence data files, but with a `.bin` extension. During acquisition, operators place circular ROIs over the images, and photometry readouts are obtained by averaging the signal inside these regions.

To open these files, users need additional information to parse the binary data. Data is stored in a `ColumnMajor` layout format, where each frame can be parsed with the information available in the corresponding `.json` file. Each `.json` file contains the following fields:

* `Width`: Imaging width (200 px by default)
* `Height`: Imaging height (200 px by default)
* `Depth`: Bit depth (U16 by default)
* `Channel`: Channel (1 channel by default)

See the Application Notes section for an example of how to parse the binary files.

#### Sensor background data (optional)

In some experiments, operators may choose to record background frames without any illumination. These frames can be used to estimate the camera's dark count floor and subtract it from the raw data during post-processing. If background frames are recorded, they will mirror the naming convention of the raw sensor data files and append `background_` to the beginning of the filename. While optional, these files are expected to still honor the `<color>_metadata.json` and `regions.json` specifications.

If the background files are not present, users can assume that no background frames were recorded during the session.

If the background files are present they must contain at least one frame (i.e. row) in the corresponding `<color>_background.csv` file.

If one background file is present, all background files must be present.

#### Recovering the regions of interest

The regions of interest (ROIs) used during the experiment are saved as a single `JSON` file named `regions.json`. Each ROI is defined as a `Circle` with a center coordinate (`[x,y]`) and a radius (`r`) in pixels. The units (pixels) are the same as in the parsed `.bin` file. This file contains the following fields:

```plaintext
regions.json
├── camera_green_iso_background: Circle[[x, y], r]
├── camera_red_background:       Circle[[x, y], r]
├── camera_green_iso_roi:        list of Circle[[x, y], r]
├── camera_red_roi:              list of Circle[[x, y], r]
```

An image like the one below can be generated by combining the previous two files.

![image](https://github.com/user-attachments/assets/30900798-5d51-43ba-99fc-41b07d4a75dd)

#### Camera Metadata

The fiber imaging system uses a single camera to capture data from two distinct light sources (`iso` and `green` channels) through temporal multiplexing. As a result, only two metadata files are generated - one for each camera. These files can be used to ensure data integrity during post-processing. The metadata files are named as follows:

* `camera_green_iso_metadata.csv`: metadata from the camera recording both green and iso channels
* `camera_red_metadata.csv`: metadata from the camera recording the red channel

Within the metadata files are the following columns:

* `ReferenceTime` Time of the trigger given by hardware (Harp)
* `CameraFrameNumber` Frame counter given by the camera API
* `CameraFrameTime` Frame acquisition time given by the camera API
* `CpuTime` Software timestamp from the OS, in timezone-aware ISO8061 format. Users should consider these timestamps low-precision and rig-dependent, and should not rely on them for analysis.

Under expected operating conditions, these files will contain all the rows present in the `<color>.csv` and `background_<color>.csv` files.

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

The FIP file format documents ROI-based measurements from patch cords. To fully interpret this data, additional metadata is required. For details on how this metadata is formatted under the AIND data schema, see the [AIND Data Schema ReadTheDocs](https://aind-data-schema.readthedocs.io/en/latest/). But briefly:

* **procedures.json**: Documents implanted fiber locations (stereotactic coordinates) and viral injection metadata (stereotactic coordinates, materials, viral constructs)

* **acquisition.json**: Documents which patch cords were connected to which implanted fibers during the experiment. This is contained in the [connections](https://aind-data-schema.readthedocs.io/en/latest/components/connections.html#connection) list in the [DataStream object](https://aind-data-schema.readthedocs.io/en/latest/acquisition.html#datastream). This mapping is critical for correctly interpreting the data, as the `Fiber_n` columns in the CSV files represent patch_cord_n data, and experimenters may not always connect patch_cord_n to fiber_n (e.g., if a particular implanted fiber is damaged or if a different configuration is needed for the experiment). Also documents the intended measurement for each fiber (e.g., norepinephrine, dopamine, calcium) which is stored in the [channel](https://aind-data-schema.readthedocs.io/en/latest/components/configs.html#channel) config of each [PatchCordConfig](https://aind-data-schema.readthedocs.io/en/latest/components/configs.html#patchcordconfig), assuming that this information was provided by the scientist in the surgical request.

A standard convention is for patch cords 0 through N-1 to connect to fibers 0 through N-1, with patch cords N through K left unused, but this convention is not enforced by the acquisition software. There is currently no method for capturing intentional or inadvertent variances from this convention (again, see [this issue](https://github.com/AllenNeuralDynamics/Aind.Physiology.Fip/issues/40).)

### File Quality Assurances

The following are expected to be true for all FIP data collected under this standard:

* The number of frames in the raw binary files shall match the number of frames in the corresponding `CSV` files (e.g., `green.csv` and `green.bin`).
* The number of frames across all `CSV` files shall be the same (i.e., `green.csv` = `red.csv` = `iso.csv`) and, by extension, the number of frames in the corresponding binary files.
* Camera metadata files shall contain no dropped frames. This can be verified by checking the `CameraFrameNumber` column in the metadata files. The difference between consecutive frames must ALWAYS be 1. If a dropped frame is present, data may be corrupted and should be flagged for manual review. 
    > [!WARNING]
    > Dropped frames are not normal and should not be taken lightly. If you encounter dropped frames, please contact the data acquisition team for further investigation.
* The difference between the derivative of `CameraFrameTime` and `ReferenceTime` is expected to be very small (i.e.: abs(max(diff(`CameraFrameTime`) - diff(`ReferenceTime`))) < 0.2ms). If this is not the case, it may indicate a problem with frame exposure.
* All rows in the `<color>.csv` files will be present in the corresponding camera metadata files. The opposite is not guaranteed to be true.
* A `<color>.csv` file always contains exactly K `Fiber_n` columns (`Fiber_0` through `Fiber_{K-1}`) corresponding to the patch cords for the rig. A `Background` column is always present. The order of the columns in the `<color>.csv` files is not guaranteed to be the same across different sessions. It is thus recommended to use the header as the index for the columns.
* The naming of `Fiber_n` columns in the `<color>.csv` files is guaranteed to be sequential, starting from `Fiber_0` and going up to `Fiber_{K-1}`. **Important**: These column names reflect patch cord indices (k = 0 … K-1), not necessarily the indices of implanted fibers (n = 0 … N-1). If N < K (where N is the number of implanted fibers), then patch cords N through K-1 are unused. Consult acquisition.json metadata to determine the patch_cord-to-fiber mapping for each session.
* The `regions.json` in the FIP session are guaranteed to be static within a session. The number and order of the ROIs are expected to be the same across the two cameras.