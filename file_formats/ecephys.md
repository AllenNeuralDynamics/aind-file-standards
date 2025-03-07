# Standards on electrophysiology acquisition

Version: 0.0.1

## Introduction

This document describes the standards for the acquisition of electrophysiology data in the Allen Institute for Neural Dynamics, which primarily consists of extracellular electrophysiology signals
acquired using Neuropixels probes.

## Raw Data Format

Following SciComp standards, ecephys data from experiments should be saved to the "ecephys" modality folder.

### File format

The raw data format is a folder produced by the Open Ephys GUI (version>=0.6.0) in binary format and is organized as outlined in the official [Open Ephys Documentation](https://github.com/open-ephys/gui-docs/blob/b608d57a155b5af86f39048238492728fcd4e161/source/User-Manual/Recording-data/Binary-format.rst).

In addition, it is required that the Open Ephys folder is temporally aligned using the `generate_report` or the `align_timestamps` functions from the [aind-ephys-rig-qc](https://github.com/AllenNeuralDynamics/aind-ephys-rig-qc) package to ensure that different streams are synced 
with each other either *locally* or to the HARP clock (see [HARP format](harp.md)).
Time alignment will produce additional timestamps files for each continuous/event stream:
- `original_timestamps.npy`
- `localsync_timestamps.npy` (only if HARP clock is detected)

### Application notes

The raw data can be directly read using the [open-ephys-python-tools](https://github.com/open-ephys/open-ephys-python-tools) or the [SpikeInterface](https://spikeinterface.readthedocs.io/en/latest/index.html) package.

### Relationship to aind-data-schema

The `rig.json` will contain relevant metadata from the Open Ephys settings, such as the probe names and serial numbers.

### File Quality Assurance and Assumptions

The electrophysiology data is visually inspected during the experiments. In addition, after a session is acquired, a quality control report is generated using the [aind-ephys-rig-qc](https://github.com/AllenNeuralDynamics/aind-ephys-rig-qc) `generate_qc_report` function.
This report is used to assess the quality of the data and to identify potential issues with the acquisition, including timestamps misalignments, abnormal noise levels and power spectra, and excessive drift.

## Primary Data Format

### File format

Before the data is uploaded to the cloud, it undergoes a data transformation to compress 
the raw data using the [aind-data-transformation](https://github.com/AllenNeuralDynamics/aind-data-transformation). 
The original Open Ephys folder is kept, but the `.dat` files 
are clipped to reduce the file size maintaining maintain the original folder structure. This clipped Open 
Ephys folder is saved in the `ecephys_clipped` folder.
The `.dat` files are compressed to `zarr` using the 
[SpikeInterface](https://spikeinterface.readthedocs.io/en/latest/index.html) library.
The compressed data is saved in the `ecephys_compressed` folder.

The primary data format is organized as follows:

```plaintext
📦ecephys
┣ 📂ecephys_clipped
┃ ┗ 📂<Record Node *I*>
┃   ┗ 📂<experiment*J*>
┃     ┣ 📂<recording*K*>
┃     ┃ ┣ 📂<continuous>
┃     ┃ ┃ ┗ 📂<StreamName>
┃     ┃ ┃   ┣ 📜clipped continuous.dat
┃     ┃ ┃   ┗ 📜other intact files 
┃     ┃ ┣ 📂<events>
┃     ┃ ┃ ┗ 📂<StreamName>
┃     ┃ ┃   ┗ 📜 original event files
┃     ┃ ┗ 📜 structure.oebin
┃     ┗ 📜 settings.xml
┗ 📂ecephys_compressed
  ┣ 📂<experiment*J*_Record Node*I*#StreamName.zarr>
  ┃ ┗ 📂channel_ids
  ┃ ┗ 📂properties
  ┃ ┗ 📂times_seg*K-1*
  ┃ ┗ 📂traces_seg*K-1*
  ┃ ┗ 📜.zattrs
  ┗ ...
```

The `ecephys_clipped` folder contains all the original Open Ephys folders and files, with the only difference that 
the `.dat` files are clipped to 100 samples. Therefore, this folder can be opened by the normal sowtware tools 
that can read Open Ephys data, such as the [open-ephys-python-tools](https://github.com/open-ephys/open-ephys-python-tools)
and the [SpikeInterface](https://spikeinterface.readthedocs.io/en/latest/index.html) library.

The `ecephys_compressed` folder contains the compressed data in the `zarr` format. 
Data from different Open Ephys "experiments" and different streams are saved in different `.zarr` files.
The `zarr` file is produced from the `spikeinterface.BaseRecording.save_to_zarr()` function, 
which saves and compresses the data and its metadata to a `.zarr` file. In case of multiple Open Ephys "recordings",
the data is saved in different "segments" (e.g. `traces_seg0`, `traces_seg1`, etc.).

Here is a brief description of the content of the `.zarr` file:

- `channel_ids`: list of channel ids from the original Open Ephys data
- `properties`: dictionary with the properties of the recording (e.g. `channel_locations`, `gains`, etc.)
- `times_seg*K-1*`: Open Ephys timestamps for each segment
- `traces_seg*K-1*`: compressed traces for each segment

#### Compression details

The `traces_seg*K-1*` is chunked in (30000, 384), so that each chunk corresponds to 1 second of data for all channels.
By default, we use the [`wavpack`](https://www.wavpack.com/) codec, implemented as a `zarr` compressor 
in the [wavpack-numcodecs](https://github.com/AllenNeuralDynamics/wavpack-numcodecs) package. Prior to compression,
the LSB (least significant bit) offset is subtracted from each channel, using the 
`spikeinterface.preprocessing.correct_lsb()` function. This is done to ensure that the data is centered around 0,
which improves the compression ratio. For more information, see [Buccino et al. 2023](https://iopscience.iop.org/article/10.1088/1741-2552/acf5a4).

### Application notes

Here is a snippet of code that shows how to read the clipped and compressed data
using the [SpikeInterface](https://spikeinterface.readthedocs.io/en/latest/index.html) library:

```python
import spikeinterface as si
import spikeinterface.extractors as se

# read number of blocks (experiments) and streams (probes) from the clipped data
num_blocks = se.get_neo_num_blocks("openephysbinary", "ecephys/ecephys_clipped")
stream_names, stream_ids = se.get_neo_streams("openephysbinary", "ecephys/ecephys_clipped")

# read the first block and stream
block_index = 0
stream_name = stream_names[0]
recording_clipped = se.read_openephys(
  "ecephys/ecephys_clipped/",
  block_index=block_index,
  stream_name=stream_name
)

# read the openephys events
events = se.read_openephys_events("ecephys/ecephys_clipped/")

# read the compressed data for the first block and stream
recording_compressed = si.read_zarr(
  f"ecephys/ecephys_compressed/experiment{block_index+1}_{stream_name}.zarr"
)
```

### Relationship to aind-data-schema

The `processing.json` includes the compression details and parameters.

### File Quality Assurance and Assumptions

No further quality assurance is performed during the conversion from the raw data to the primary data format.

