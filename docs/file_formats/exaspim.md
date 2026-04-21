# Standards on `<data-format/modality>` acquisition

## Version

0.1.0

## Introduction

This section should briefly introduce the data format and its purpose.

## Raw Data Format

*I don't think we want anything under "raw"?*

## Primary Data Format

### File format

Images are uploaded in OME-ZARR format to the path `SPIM.ome.zarr`. These files are removed following processing and replaced by a placeholder `SPIM.ome.zarr.deleted`

## Derived Data Format

### File format

Processed assets consist of subfolders for each component process, with required components `ccf_alignment`, `fusion`, and `tile_alignment`.

#### tile_alignment

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
#### fusion

Fused image is saved to `fused.n5`, with two channels, *signal and CCF*.

#### ccf_alignment

Transformations are saved in `mat` (affine) or `nii.gz` formates (warp), as expected by ANTS.

Transformed image volumes are saved in `zarr` format, possibly with a copy in `nii.gz` format.

Folder structure:
```
ccf_alignment
├── 784896_to_exaSPIM_SyN_0GenericAffine.mat
├── 784896_to_exaSPIM_SyN_1InverseWarp.nii.gz
├── 784896_to_exaSPIM_SyN_1Warp.nii.gz
├── ccf_aligned.zarr
└── ccf_anno_to_sample
    ├── ccf_anno_in_sample_space.nii.gz
    └── ccf_anno_in_sample_space.zarr
```

#### soma_detection

*NOT CURRENTLY PRESENT*

Output is a single table in `csv` format containing soma locations in CCF and specimen space (*document columns*)

#### Other processes
Other processes including `flatfield_correction` and `denoising` only contribute processing metadata to the final asset
(outputs used by downstream processing are removed after to save space).

### Application notes

These data assets are **not immutable** (an exception to the usual requirement), but instead have process subfolders
added incrementally as they progress through the pipeline.

### Relationship to aind-data-schema

Each component process writes a `processing.json` file compliant with the Processing schema in the process-specific subfolder, 
and also concatenates this Processing entry onto the top-level `processing.json`.

### File Quality Assurances

The following features should be true if the data asset is to be considered valid:
- if processing is complete, all subfolders and contents listed above must be present
- ...

The following outputs are saved to the QC schema to facilitate additional evaluation
- tile_alignment produces a Neuroglancer link and series of overlay images to visually assess alignment.
- ...
