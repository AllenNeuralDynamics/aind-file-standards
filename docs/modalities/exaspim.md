# Standards on exaSPIM platform data

## Version

0.1.1

## Introduction

This document describes the standards and file formats used for data acquired on the exaSPIM platform (expansion-assisted selective plane illumination microscopy).

## Raw Data Format

The raw IMS files are converted to OME-ZARR during upload and the original IMS files are not preserved. The raw IMS format is not part of this specification.

## Primary Data Format

### File format

Images are uploaded in OME-ZARR format to the path `SPIM.ome.zarr` in the primary data asset. These files are removed following processing and replaced by a placeholder `SPIM.ome.zarr.deleted`

## Derived Data Format - Image Processing

### File format

Processed assets must be named with the `_processed` suffix and consist of subfolders for each component process. A complete asset must include folders `tile_alignment`, `fusion`,  `ccf_alignment`, and `soma_detection`, with contents specified below.
Additional process folders may be added as needed during processing, but should be removed from the final asset once they are no longer needed.

#### `tile_alignment`

Tile alignment outputs are organized in a set of specified subfolders; exact contents of these may vary across versions of the processing code.

Folder structure:
```
tile_alignment/
├── ch_ccf_xmls
├── interest_point_detection
├── ip_affine_alignment
├── ip_rigid_alignment
├── ip_split_affine_alignment
├── quality_control
└── split_dataset
```
#### `fusion`

Fused image (composite of all aligned tiles) is saved to `fusion/fused.zarr`, with two channels, *signal and CCF*.

#### `ccf_alignment`

Transformations from CCF alignment are saved in the structure defined below, in formats expected by ANTs: `mat` (binary matrix format) for affine transforms and `nii.gz` (compressed NIfTI format) for nonlinear warp transforms.

Transformed image volumes and annotation label volumes must be saved in `zarr` format, and may include an additional copy in `nii.gz` format.

Folder structure:
```
ccf_alignment
├── <subject_id>_to_exaSPIM_SyN_0GenericAffine.mat
├── <subject_id>_to_exaSPIM_SyN_1InverseWarp.nii.gz
├── <subject_id>_to_exaSPIM_SyN_1Warp.nii.gz
├── ccf_aligned.zarr
└── ccf_anno_to_sample
    ├── ccf_anno_in_sample_space.nii.gz
    └── ccf_anno_in_sample_space.zarr
```

#### `soma_detection`

Results must be saved to `soma_detection/soma_locations.csv`, containing soma locations in specimen and CCF space in columns `xyz_raw` and `xyz_ccf_auto`.

#### Other processes
Other processing steps including `flatfield_correction` and `denoising` must contribute processing metadata to processing.json, 
and may temporarily store intermediate outputs used by downstream processing. These must be removed after they are no longer needed to save space.

### Application notes

These data assets are **not immutable** (an exception to the usual requirement), but instead have process subfolders
added incrementally as they progress through the pipeline. Other than metadata, existing files must not be modified in place, 
but new files may be added and existing files from non-required steps may be removed once they are no longer needed.

### Relationship to aind-data-schema

Each component process must write a `processing.json` file compliant with the Processing schema in the process-specific subfolder, 
and must also concatenate this Processing entry onto the top-level `processing.json`.

### File Quality Assurances

The following features must be true if the data asset is to be considered valid:
- if processing is complete, all subfolders and contents listed above must be present
- if processing is in progress, all subfolders and contents that have been generated so far must be present (following the component order above).

## Derived Data Format - Neuron Reconstructions

### File format

Neuron reconstructions are saved in three formats: SWC, parquet, and Neuroglancer precomputed.

###  neuron-reconstruction parquet

A neuron-reconstruction parquet file MUST include an `nr` key in the Parquet metadata (see [FileMetaData::key_value_metadata](https://github.com/apache/parquet-format#metadata)). The value of this key MUST be a JSON-encoded UTF-8 string representing the file metadata that validates against the [neuron-reconstruction metadata JSON schema](resources/neuron-reconstruction.metadata.schema.json). The metadata fields are described below.

| Field name | Type | Description |
| --- | --- | --- |
| `atlas_annotation_set` | string | **REQUIRED.** Identifier and version of the atlas annotation set used for the reconstruction. SHOULD be empty if no annotations are assigned. |
| `atlas_coordinate_space` | string | **REQUIRED.** Identifier and version of the atlas coordinate space used for the reconstruction. SHOULD be empty if reconstruction is not registered to an atlas, in which case coordinates MUST be physical coordinates of the sample. |
| `subject_id` | string | **REQUIRED.** Unique identifier for the subject from which the cell was obtained. |
| `cell_id` | string | **REQUIRED.** Unique identifier for the reconstructed cell. |
| `annotator` | string | **OPTIONAL.** Name(s) of the person who created the reconstruction annotation. |
| `peer_reviewer` | string | **OPTIONAL.** Name(s) of the peer reviewer who assessed the reconstruction. |
| `proofreader` | string | **OPTIONAL.** Name(s) of the person who proofread the reconstruction. |
| `doi` | string | **OPTIONAL.** Digital Object Identifier associated with the reconstruction (specific version). |
| `doi_cell` | string | **OPTIONAL.** Digital Object Identifier associated with the cell (linking all versions of reconstruction). |
| `date` | string | **OPTIONAL.** Date the reconstruction was created, formatted as ISO 8601. |
| `version` | string | **OPTIONAL.** Version identifier for the reconstruction. |
| `genotype` | string | **OPTIONAL.** Genotype of the subject. |
| `label_fluorophore` | string | **OPTIONAL.** Fluorophore used to label the reconstructed cell. |
| `label_virus` | string | **OPTIONAL.** Viral construct used to label the reconstructed cell. |

It also MUST include a set of standardized columns (compatible with the SWC format), described below. Additional columns MAY be included as needed for specific use cases.
Usage of the `type` column SHOULD be restricted to the commonly used SWC node types 1-4, which correspond to soma, axon, dendrite, and apical dendrite, respectively.
Where necessary, additional positive integer values MAY be used, following the full SWC standard (swc-specification.readthedocs.io/en/1.0.3/swc.html) with the addition of NULL rather than 0 for unspecified values.

| Column name | Type | Description |
| --- | --- | --- |
| `id` | positive integer | **REQUIRED.** Unique identifier for the node. |
| `type` | positive integer | **REQUIRED.** SWC node type identifier. |
| `x` | float | **REQUIRED.** Node x-coordinate in the coordinate space, in micrometers. |
| `y` | float | **REQUIRED.** Node y-coordinate in the coordinate space, in micrometers. |
| `z` | float | **REQUIRED.** Node z-coordinate in the coordinate space, in micrometers. |
| `parent` | integer | **REQUIRED.** Identifier of the node's parent; MUST be `-1` for the root node and a positive integer for all other nodes. |
| `radius` | float | **REQUIRED.** Radius of the node in the coordinate space, in micrometers. SHOULD be null if the radius is not available. |
| `atlas_annotation_value` | integer | **OPTIONAL.** Atlas annotation value at the node location, defining a unique label in the atlas terminology; SHOULD be null for nodes without an annotation, and absent entirely if no atlas annotations are assigned. SHOULD refer to the most specific annotation available (leaf nodes of terminology). |