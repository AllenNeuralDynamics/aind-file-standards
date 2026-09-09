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

## Derived Data Format - Image Processing

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

Results are saved to `merged_soma_locations.csv`, containing soma locations in CCF and specimen space (*document columns*)

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

## Derived Data Format - Neuron Reconstructions

### File format

Neuron reconstructions are saved in three formats: SWC, parquet, and Neuroglancer precomputed.

###  neuron-reconstruction parquet

A neuron-reconstruction parquet file MUST include an `nr` key in the Parquet metadata (see [FileMetaData::key_value_metadata](https://github.com/apache/parquet-format#metadata)). The value of this key MUST be a JSON-encoded UTF-8 string representing the file metadata that validates against the neuron-reconstruction metadata JSON schema (TO BE ADDED). The metadata fields are described below.

| Field name | Type | Description |
| --- | --- | --- |
| `atlas_annotation_set` | string | **REQUIRED.** Identifier and version of the atlas annotation set used for the reconstruction. |
| `atlas_coordinate_space` | string | **REQUIRED.** Identifier and version of the atlas coordinate space used for the reconstruction. |
| `subject_id` | string | **REQUIRED.** Unique identifier for the subject from which the cell was obtained. |
| `cell_id` | string | **REQUIRED.** Unique identifier for the reconstructed cell. |
| `annotator` | string | **OPTIONAL.** Name of the person who created the reconstruction annotation. |
| `peer_reviewer` | string | **OPTIONAL.** Name of the peer reviewer who assessed the reconstruction. |
| `proofreader` | string | **OPTIONAL.** Name of the person who proofread the reconstruction. |
| `doi` | string | **OPTIONAL.** Digital Object Identifier associated with the reconstruction. |
| `doi_cell` | string | **OPTIONAL.** Digital Object Identifier associated with the cell (linking all versions of reconstruction). |
| `date` | string | **OPTIONAL.** Date the reconstruction was created, formatted as ISO 8601. |
| `version` | string | **OPTIONAL.** Version identifier for the reconstruction. |
| `genotype` | string | **OPTIONAL.** Genotype of the subject. |
| `label_fluorophore` | string | **OPTIONAL.** Fluorophore used to label the reconstructed cell. |
| `label_virus` | string | **OPTIONAL.** Viral construct used to label the reconstructed cell. |

It also MUST include a set of standardized columns (compatible with the SWC format), described below. Additional columns MAY be included as needed for specific use cases.

| Column name | Type | Description |
| --- | --- | --- |
| `id` | integer | **REQUIRED.** Unique identifier for the node. |
| `type` | integer | **REQUIRED.** SWC node type identifier. |
| `x` | float | **REQUIRED.** Node x-coordinate in the atlas coordinate space. |
| `y` | float | **REQUIRED.** Node y-coordinate in the atlas coordinate space. |
| `z` | float | **REQUIRED.** Node z-coordinate in the atlas coordinate space. |
| `parent` | integer | **REQUIRED.** Identifier of the node's parent; use `-1` for a root node. |
| `radius` | float | **OPTIONAL.** Radius of the node in the atlas coordinate space. |
| `atlas_annotation_id` | integer | **OPTIONAL.** Atlas annotation identifier at the node location; MAY be null when no annotation is assigned. |