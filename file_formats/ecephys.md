# Standards on electrophysiology acquisition
Version: 0.0.1

## Acquisition/Raw Data Format

Following SciComp standards, ecephys data from experiments should be saved to the "ecephys" modality folder.

The **primary data format** is a folder produced by the Open Ephys GUI (version>=0.6.0), which is organized as outlined in the official [Open Ephys Documentation](https://github.com/open-ephys/gui-docs/blob/b608d57a155b5af86f39048238492728fcd4e161/source/User-Manual/Recording-data/Binary-format.rst).

### Application notes

[example SpikeInterface script]

### Relationship to aind-data-schema Session

[how key metadata is related to files in the format - e.g. "this fluorophore/wavelength corresponds to channel0.zarr"]

## Primary Data Format

Before the data is uploaded to the cloud, it undergoes a data transformation to compress 
the raw data using the [aind-data-transformation](https://github.com/AllenNeuralDynamics/aind-data-transformation). 
The original Open Ephys folder is kept, but the `.dat` files 
are clipped to reduce the file size maintaining maintain the original folder structure. This clipped Open 
Ephys folder is saved in the `ecephys_clipped` folder.
The `.dat` files are compressed to `zarr` using the 
[SpikeInterface](https://spikeinterface.readthedocs.io/en/latest/index.html) library.
The compressed data is saved in the `ecephys_compressed` folder.

The **secondary data format**, therefore, is organized as follows:

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

### "ecephys_clipped" folder

The `ecephys_clipped` folder contains all the original Open Ephys folders and files, with the only difference that 
the `.dat` files are clipped to 100 samples. Therefore, this folder can be opened by the normal sowtware tools 
that can read Open Ephys data, such as the [open-ephys-python-tools](https://github.com/open-ephys/open-ephys-python-tools)
and the [SpikeInterface](https://spikeinterface.readthedocs.io/en/latest/index.html) library.

### "ecephys_compressed" folder

The `ecephys_compressed` folder contains the compressed data in the `zarr` format. 
Data from different Open Ephys "experiments" and different streams are saved in different `.zarr` files.
The `zarr` file is produced from the `spikeinterface.BaseRecording.save_to_zarr()` function, 
which saves and compresses the data and its metadata to a `.zarr` file. In case of multiple Open Ephys "recordings",
the data is saved in different "segments" (e.g. `traces_seg0`, `traces_seg1`, etc.).

Here is a bried description of the content of the `.zarr` file:

- `channel_ids`: list of channel ids from the original Open Ephys data
- `properties`: dictionary with the properties of the recording (e.g. `channel_locations`, `gains`, etc.)
- `times_seg*K-1*`: Open Ephys timestamps for each segment
- `traces_seg*K-1*`: compressed traces for each segment

### Compression details

The `traces_seg*K-1*` is chunked in (30000, 384), so that each chunk corresponds to 1 second of data for all channels.
By default, we use the [`wavpack`](https://www.wavpack.com/) codec, implemented as a `zarr` compressor 
in the [wavpack-numcodecs](https://github.com/AllenNeuralDynamics/wavpack-numcodecs) package. Prior to compression,
the LSB (least significant bit) offset is subtracted from each channel, using the 
`spikeinterface.preprocessing.correct_lsb()` function. This is done to ensure that the data is centered around 0,
which improves the compression ratio. For more information, see [Buccino et al. 2023](https://iopscience.iop.org/article/10.1088/1741-2552/acf5a4).

### Application notes

[example SpikeInterface script] 

## File Quality Assurance and Assumptions

[e.g. "the timestamps are sorted in time already", "how to detect dropped frames in this format", "the frames in this file match the number of rows in this CSV"] 
