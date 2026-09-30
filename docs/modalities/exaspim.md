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

## Derived Data Format

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
