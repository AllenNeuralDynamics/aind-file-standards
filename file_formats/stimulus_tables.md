# Standards on `<data-format/modality>` acquisition

## Version

`1.0.0`

## Introduction

The stimulus table is used to temporally represent the stimulus dispensed throughout a session. There are three kinds of stimulus tables; basic stim tables, which contain visual stimulus information from the screen, opto tables, which represent the various optogenetic laser conditions. There should be one basic stim table, and there may be one opto table.


## Raw Data Format

### File format

Stim tables may be produced from any source format. In the aind-metadata-mapper, there are various ETL objects each associated with different projects and rig types. These ETLs should identify the correct source file containing stimulus info and generate a proper stim table in the form of a .CSV. For instance, the `CamstimEphysSessionEtl` ETL uses either a `*.stim.pkl` or a `*.behavior.pkl` depending on which is present, and uses an `*.opto.pkl` if it is present. The ETL is responsible for handling the variations between the structure of these files. In this case the directory structure may look as follows.

e.g.:

```plaintext

📦np-exp (or other session directory)
┣ 📂<session_id> (e.g 0123456789_123456_20250101)
┃  ┗ 📜<session_id>.behavior.pkl
┃  ┗ 📜<session_id>.opto.pkl
...
```

### Application notes

TODO
This section is reserved to provide additional information on how to acquire the data in the data format described above. It can include information relative to the hardware (e.g. supported models), software interface (e.g. SoftwareFoo with version >= 1.0.0), ideally, some easy to deploy or follow examples that can get anyone to reproduce the data format.



### Relationship to aind-data-schema

There is no relationship between the raw data and the aind-data-schema that is relevant here. The raw stimulus information relates to the aind-data-schema through the derived asset, which is described below.


### File Quality Assurances

TODO
This section is reserved to describe what features of the data format should be true if the data asset is to be considered valid. Conceptually, this section should describe features that can be easily tested and validated by unit tests. Examples include:
- "There will always be two files: `data.dat` and `metadata.txt`"
- "For each frame in `video.avi`, there will be a corresponding row in `metadata.csv`"
- "Field `Bar` will always be a positive integer"
- "The first timestamp value in `metadata_camera.csv` will always be greater than the first one in `metadata_behavior.csv`
- The `Time` column in `file.bin` is assumed to be aligned (sharing the same time domain) with `Time` column of `another_file.csv`


## Primary Data Format

### File format

#### Basic Stimulus Table
The stim tables are stored as `.CSV` tables. At minimum, it must include the following columns:
- `start_time`: float representing the time, in seconds, the stimulus began
- `stop_time`: float representing the time, in seconds, the stimulus ended
- `stim_name`: string representing the unique kind of stim shown. E.g "receptive_field_mapping", "drifting_gratings", "natural_movie_1"

Any stimulus which is not procedurally generated should have additional columns. 
For image sequences:
- `image_name`: string representing the name of the image. This is used to associate the stimulus with a stim_template object/file which should have the same name in subsequent data packaging.
- `image_index`: integer representing the position of the image in the sequence. If there is no canonical or expected order for the sequence of images this is not necessary, but may still be helpful.

For movies:
- `movie_name`: string representing the name of the movie. This is used to associate the stimulus with a stim_template object/file which should have the same name in subsequent data packaging.
- `frame_index`: integer representing the index of the frame in the regular forward-playing movie. If the movie is scrambled or played backward, the `frame_index` should represent the position of the frame if it were in the unaltered movie.

Additionally, it can be helpful to include:
- `n_repeats`: integer representing the number of times an image sequence or movie has been repeated.

Additional columns include useful information about the stimulus. IT should include enough information to be able to reproduce the stimulus exactly, given you know the meaning of every column. For instance, a `gratings_presentations` stim may need the columns `size`, `orientation`, `x_position`, `y_position`. It can also be helpful to include units columns such as `size_unit`, `orientation_unit`. Columns may contain empty values (which should be interpreted as np.nan). When you have a column which expresses a parameter that only pertains to one kind of stimulus (`size`, for instance, won't mean anything on an image presentation), the rest of the column values should be blank.

The optotagging table is a subset of the stimulus table. In addition to the `start_time`, `stop_time`, and `stim_name` columns, it should include:
- `level`: Float representing the laser amplitude
- `pulse_type`: String describing the wave frequency and shape (e.g. "20hz" "square")
- `pulse_duration`: String describing the length of the pulses during this row (e.g. "2ms")



### Application notes

As mentioned above, stim tables can be generated using the ETL objects in the aind-metadata-mapper. This is the recommended way, but for certain use cases it may be benefiticial to write some other application to generate stim tables that comply with this format.


### Relationship to aind-data-schema

This stim table is used via the `aind-metadata-mapper` to generate the stimulus epochs section of the `aind-data-schema`'s `session.json`. An epoch is considered a contiguous set of rows that all have the same `stim_name` (ignoring rows where `stim_name` is "spontaneous"). `start_time` and `stop_time` are used to determine the timing of this epoch. Most of the remaining columns (with specific exceptions) are used to extract the parameters for that epoch. For each column name, the parameters are given as the set of unique values in that column for that epoch. If there are over 1000 values, they are not provided to that epoch's parameters.



### File Quality Assurances

The columns `start_time`, `stop_time`, and `stim_name` should be present and should have columns that contain no empty values. Every row must have a `stop_time` greater than its associated `start_time`, and every `start_time` must be greater than or equal to the `stop_time` of the previous row. Times must be non-negative.


## Derived Data Format

### File format

In addition to providing information to the `aind-data-schema`'s `session.json`, stimulus tables are packaged into NWB files using PyNWB. When this is done, the stimulus table is split into many pandas dataframes based on the `stim_name` column and added as separate `intervals` objects in the NWB. The optotagging table is also added, without splitting based on `stim_name`.


### Application notes

This is done on codeocean in the [aind-stimulus-camstim-nwb](https://codeocean.allenneuraldynamics.org/capsule/4510069/tree) capsule. A CO asset must be provided that contains a stim table named of the form `*stim*.csv`, looking in the directory specified with the capsule's `Input CSV Dir` directory. In the same directory it will also look for a file named such as `*opto*.csv` for an associated opto table. An existing NWB must also be provided to package the stimulus interval object into.


### Relationship to aind-data-schema

No relation.


### File Quality Assurances

NWB Files get validated during subsequent file upload to DANDI using the DANDI library's validation.