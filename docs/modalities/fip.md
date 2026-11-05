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
- **N** to represent the total number of implanted fibers in a given mouse. The number of total implanted fibers may differ from the number of recorded implanted fibers in a given acquisition.
- **K** to represent the total number of ROIs in each camera ROI list in `regions.json`.
- **i** to represent an individual ROI's number, where 0 ≤ i ≤ K-1.

The mapping between ROIs and implanted fibers is determined by the experimenter at the time of the experiment and should be documented in metadata (see the "Relationship to aind-data-schema" section below for more detail).

## Raw Data Format

Following SciComp standards, FIP data should be saved in their own folder named "fib" (short for "fiber photometry"). Data from other modalities go in separate folders.

### File format 

In most cases, FIP data will be saved in `CSV` files, where each file corresponds to a different channel in the photometry rig. In addition to the timeseries fluorescence data, files containing metadata and raw image data are also available. A single session of FIP data should be organized under the `fib` directory. An acquisition for a single session should be nested under a sub directory named following the core standards for file naming convention found [here](https://github.com/AllenNeuralDynamics/aind-file-standards/blob/main/core/core-standards.md#filename-conventions).  Mostly, this is for cases where the recording gets interrupted. When the system restarts under the same session, it can be added to a new folder. A sessions folder structure should look like the following:

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
* `ROI_i` Average signal values from the corresponding ROI `i` (one column per enabled ROI)

**Note:** For `green.csv` and `iso.csv`, `ROI_i` refers to entry `i` in `camera_green_iso_roi` from `regions.json`. For `red.csv`, it refers to entry `i` in `camera_red_roi`.  The relationship between ROIs and implanted fibers in the mouse is not captured in this file format and should be documented separately in metadata (see Relationship to aind-data-schema section below).

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

If the background files are present, they must contain at least one frame (i.e. row) in the corresponding `background_<color>.csv` file.

If one background file is present, all background files must be present.

#### Recovering the regions of interest

The regions of interest (ROIs) used during the experiment are saved as a single `JSON` file named `regions.json`. ROI coordinates and radii are in pixels, matching the units in the parsed `.bin` file. This file contains the following fields:

```plaintext
regions.json
├── camera_green_iso_background: FipCircle
├── camera_red_background:       FipCircle
├── camera_green_iso_roi:        list of FipCircle
├── camera_red_roi:              list of FipCircle
```

Where each FipCircle is defined by:

```plaintext
FipCircle
├── center
│   ├── x: number                 pixel coordinate
│   └── y: number                 pixel coordinate
├── radius: number                pixels
├── roi_number: integer | null    zero-based ROI number
├── fiber_number: integer | null  operator-specified implanted fiber assignment
├── name: string | null           optional label
└── enabled: boolean              whether its signal is written to the CSV
```
Each FipCircle contains `center: {x, y}` and `radius`. Entries in the camera ROI lists also contain `roi_number`, `fiber_number`, optional `name`, and `enabled` state.

Background circles describe the regions used to calculate the Background signal. They use the same FipCircle model, but only their center and radius values are used to define the background region. `roi_number`, `fiber_number`, and `name` do not determine whether a `Background` column in `<color>.csv` is present.

**Note:** Presence of a `fiber_number` on an ROI does not, by itself, indicate that a fiber exists or that it was connected during the acquisition; this information should be documented separately in the metadata (see Relationship to aind-data-schema section below).

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

* **procedures.json**: Documents implanted fiber numbers and locations (stereotactic coordinates) and viral injection metadata (stereotactic coordinates, materials, viral constructs)

* **acquisition.json**: Documents which patch cords were connected to which implanted fibers during the experiment. This mapping is stored in the [connections](https://aind-data-schema.readthedocs.io/en/latest/components/connections.html#connection) list in the [DataStream object](https://aind-data-schema.readthedocs.io/en/latest/acquisition.html#datastream).
    * The aind-data-schema does not define ROIs as a separate concept independent of patch cords; therefore, acquisitions following this schema MUST follow the convention that `ROI_i` is drawn over the end of patch cord `i`, such that the column `ROI_i` in each CSV contains data from patch cord `i`. 
    * Our standard convention is to define one patch cord configuration `i` for each ROI `i` with `enabled: true` and a `fiber_number` that corresponds to an actual fiber implant number in the `procedures.json`.
    * To identify the implanted fiber represented by each `ROI_i` column in a `<color>.csv` using this metadata, first associate ROI `i` with patch cord `i`, then use this metadata's `DataStream.connections` to find the implanted fiber connected to patch cord `i`. Refer to `procedures.json` to identify that fiber’s implant details.
    * If `acquisition.json` is available for a recording, use its connection metadata as the authoritative, ground-truth mapping between patch cords and implanted fibers. 
    * The fiber to patch cord mapping is critical for correctly interpreting the data, as experimenters may not always connect a given patch cord to the implanted fiber with the same number (e.g., if a particular implanted fiber is damaged or if a different configuration is needed for the experiment). This also documents the intended measurement for each fiber (e.g., norepinephrine, dopamine, calcium) which is stored in the [channel config](https://aind-data-schema.readthedocs.io/en/latest/components/configs.html#channel) of each [PatchCordConfig](https://aind-data-schema.readthedocs.io/en/latest/components/configs.html#patchcordconfig), as provided by the scientist in the surgical request.

### File Quality Assurances

The following are expected to be true for all FIP data collected under this standard:

* The number of frames in the raw binary files shall match the number of frames in the corresponding `CSV` files (e.g., `green.csv` and `green.bin`).
* The number of frames across all `CSV` files shall be the same (i.e., `green.csv` = `red.csv` = `iso.csv`) and, by extension, the number of frames in the corresponding binary files.
* Camera metadata files shall contain no dropped frames. This can be verified by checking the `CameraFrameNumber` column in the metadata files. The difference between consecutive frames must ALWAYS be 1. If a dropped frame is present, data may be corrupted and should be flagged for manual review. 
    > [!WARNING]
    > Dropped frames are not normal and should not be taken lightly. If you encounter dropped frames, please contact the data acquisition team for further investigation.
* The difference between the derivative of `CameraFrameTime` and `ReferenceTime` is expected to be very small (i.e.: max(abs(diff(`CameraFrameTime`) - diff(`ReferenceTime`))) < 0.2ms). If this is not the case, it may indicate a problem with frame exposure.
* All rows in the `<color>.csv` files will be present in the corresponding camera metadata files. The opposite is not guaranteed to be true.
* A `<color>.csv` file contains exactly one `ROI_i` column for every entry marked `enabled: true` in its corresponding camera list from `regions.json`, and no ROI column for an entry marked `enabled: false`. A `Background` column is always present. The order of the columns in the `<color>.csv` files is not guaranteed to be the same across different sessions. It is thus recommended to use the header as the index for the columns.
* The ROI column numbers in a `<color>.csv` file are not guaranteed to be consecutive, and may have gaps (e.g. ROI_0, ROI_1, ROI_3)
* The `regions.json` in one FIP acquisition folder are guaranteed to be static for that session. `roi_number` is determined by an ROI's position in the camera lists `camera_green_iso_roi` and `camera_red_roi`. In each list, the entry at zero-based index `i` must have `roi_number: i`. The two lists must have the same number and order of ROIs, so ROI `i` refers to the same patch cord in both lists.  Their circle coordinates may differ because they use different camera images. 
