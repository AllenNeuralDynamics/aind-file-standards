# Standards on `Pavlovian conditioning (behavior)` acquisition

## Version

`0.1.0`
See Contributing.md for more information on versioning.

## Introduction

This section should briefly introduce the data format and its purpose.

## Raw Data Format

### File format

This section describes the raw data format of the asset. Data is considered in its Raw format when it is directly acquired from the hardware and logged without any lossy / compression transformation. The resulting data asset will be considered immutable.

The section should also include a brief description of the folder directory that results from the generation of the data asset. We recommend using the [`file-tree-generator`](https://marketplace.visualstudio.com/items?itemName=Shinotatwu-DS.file-tree-generator) vscode extension or the `tree` command in the terminal to generate a tree structure of the data asset.

e.g.:

```plaintext

📦behavior
┣ 📂foo
┃  ┗ 📂bar_datetime
┃     ┣ 📜baz.dat
┃     ┗ 📜baz_metadata.txt
...
```

### Application notes

This section is reserved to provide additional information on how to acquire the data in the data format described above. It can include information relative to the hardware (e.g. supported models), software interface (e.g. SoftwareFoo with version >= 1.0.0), ideally, some easy to deploy or follow examples that can get anyone to reproduce the data format.

### Relationship to aind-data-schema

This section is reserved to describe how the data format relates and/or is represented by the aind-data-schema library. Examples include how the hardware and software metadata information should be encoded in the schemas, how data acquired should exist as `Epochs` and other critical conventions. It is important to note that this section should create a one-way dependency, where data formats should NOT depend on the schema and instead stand on their own. `aind-data-schema` should instead be used to provide extra information, context and validation to the data asset.

### File Quality Assurances

This section is reserved to describe what features of the data format should be true if the data asset is to be considered valid. Conceptually, this section should describe features that can be easily tested and validated by unit tests. Examples include:
- "There will always be two files: `data.dat` and `metadata.txt`"
- "For each frame in `video.avi`, there will be a corresponding row in `metadata.csv`"
- "Field `Bar` will always be a positive integer"
- "The first timestamp value in `metadata_camera.csv` will always be greater than the first one in `metadata_behavior.csv`
- The `Time` column in `file.bin` is assumed to be aligned (sharing the same time domain) with `Time` column of `another_file.csv`

## Primary Data Format

### File format

This section describes the primary data format of the asset, which is the format of the data as it is uploaded. Primary data can have minimal processing applied, usually a compression or file format transformation. This section describes that transformation (if any), and the format of the resulting data.
Similarly to the raw data format, it is considered immutable.

### Application notes

Identical to the `Application notes` section in the `Acquisition/Raw Data Format` section. It should ideally contain information on how to generate the primary data format from the raw data format.

### Relationship to aind-data-schema

Identical to the `Relationship to aind-data-schema Session` section in the `Acquisition/Raw Data Format` section.

### File Quality Assurances

Identical to the `File Quality Assurances` section in the `Acquisition/Raw Data Format` section.


## Derived Data Format

### File format

This section is reserved to describe any derived data format from the primary data format. Derived data formats are considered to be post-processed data assets (potentially lossy) that are generated from the raw or primary data format. These are generally generated after the data has been acquired and uploaded.
While immutable after created, derived data can be regenerated from primary data assets.

### Application notes

Identical to the `Application notes` section in the `Acquisition/Raw Data Format` section. It should ideally contain information on how to generate the derived data format from the raw and/or primary data format.

### Relationship to aind-data-schema

Identical to the `Relationship to aind-data-schema Session` section in the `Acquisition/Raw Data Format` section.

### File Quality Assurances

Identical to the `File Quality Assurances` section in the `Acquisition/Raw Data Format` section.
