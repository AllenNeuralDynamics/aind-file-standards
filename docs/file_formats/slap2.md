# Standards on SLAP2 optical physiology acquisition

## Version

0.1.0

## Introduction

This document describes the standards for SLAP2 optical physiology data assets. The standard covers both static SLAP2 structure acquisitions and dynamic SLAP2 experiment acquisitions, together with the processed assets derived from them.

## Acquisition/Raw/Primary Data Format

Following SciComp standards, SLAP2 data MUST be saved in the `slap2` modality folder. The timestamped session directory is the data asset root and contains the AIND metadata files for the acquisition. Other modality folders, such as `behavior` and `behavior-videos`, MAY exist alongside `slap2` and SHOULD follow their own standards.

Within the `slap2` folder, both static and dynamic acquisitions MUST include `vasculature_map_annotated.tif` and `session_vasculature_1p.tif`.

### File format

Static SLAP2 structure assets MUST store their modality-specific files in `slap2/static_data`:

```plaintext
📦<mouse-id>_YYYY-MM-DD_HH-MM-SS
┣ 📜rig.json
┣ 📜session.json
┣ 📜subject.json
┣ 📜data_description.json
┣ 📜metadata.nd.json
┣ 📜procedures.json
┣ 📜processing.json
┗ 📂slap2
  ┣ 📜vasculature_map_annotated.tif
  ┣ 📜session_vasculature_1p.tif
  ┗ 📂static_data
    ┣ 📜structure_YYYYMMDD_HHMMSS_DMD#.meta
    ┣ 📜structure_YYYYMMDD_HHMMSS_DMD#.dat
    ┣ 📜structure_YYYYMMDD_HHMMSS_DMD#.tif
    ┗ 📜structure_YYYYMMDD_HHMMSS_DMD#-REFERENCE.tif
```

Dynamic SLAP2 experiment assets MUST store their modality-specific files in `slap2/dynamic_data`:

```plaintext
📦<mouse-id>_YYYY-MM-DD_HH-MM-SS
┣ 📜rig.json
┣ 📜session.json
┣ 📜subject.json
┣ 📜data_description.json
┣ 📜metadata.nd.json
┣ 📜procedures.json
┣ 📜processing.json
┗ 📂slap2
  ┣ 📜vasculature_map_annotated.tif
  ┣ 📜session_vasculature_1p.tif
  ┗ 📂dynamic_data
    ┣ 📜acquisition_YYYYMMDD_HHMMSS_DMD#.meta
    ┣ 📜acquisition_YYYYMMDD_HHMMSS_DMD#-TRIAL######(-CYCLE######).dat
    ┣ 📜acquisition_YYYYMMDD_HHMMSS_DMD#-TRIAL######(-CYCLE######).tif
    ┣ 📂reference_stack
    ┃ ┣ 📜refStack_YYYYMMDD_HHMMSS_DMD#(_CONFIG#).meta
    ┃ ┣ 📜refStack_YYYYMMDD_HHMMSS_DMD#(_CONFIG#).dat
    ┃ ┣ 📜refStack_YYYYMMDD_HHMMSS_DMD#(_CONFIG#).tif
    ┃ ┗ 📜refStack_YYYYMMDD_HHMMSS_DMD#(_CONFIG#)-REFERENCE.tif
    ┗ ...
```

### Application notes

The filename stems encode the acquisition time and the DMD index used for the acquisition. Dynamic acquisitions MAY omit the per-trial TIFF files when the SLAP2 acquisition mode does not generate them, but the `.dat` payloads and their metadata are still required.

The `vasculature_map_annotated.tif` file is expected to be copied from the mouse-level vasculature reference maintained outside the session asset, while `session_vasculature_1p.tif` captures the session-specific vasculature image used with the SLAP2 acquisition.

### Relationship to aind-data-schema

The asset root SHOULD include `rig.json` and `session.json` created at acquisition time. During upload, `subject.json`, `data_description.json`, `metadata.nd.json`, `procedures.json`, and `processing.json` are added at the asset root. These metadata files describe the acquisition context but are not part of the modality-specific `slap2` payload itself.

### File Quality Assurances

The following features should be true if the data asset is to be considered valid:

- The asset MUST contain exactly one modality directory named `slap2`.
- The `slap2` directory MUST contain `vasculature_map_annotated.tif` and `session_vasculature_1p.tif`.
- Static assets MUST contain `static_data`, and dynamic assets MUST contain `dynamic_data`.
- Every `.dat` file MUST have a matching `.meta` file with the same filename stem.
- Every `structure_*` or `refStack_*` TIFF stack MUST have a matching `-REFERENCE.tif` image with the same filename stem.
- If a dynamic acquisition TIFF is present, its filename stem MUST match the corresponding acquisition `.dat` payload.

## Derived Data Format

Processed SLAP2 outputs SHOULD be written to a separate processed asset whose name includes both the original session identifier and the processing start time. A generic processed asset can use the suffix `_processed_YYYY-MM-DD_HH-MM-SS`, while modality-specific processed assets can use `_<processed modality>_YYYY-MM-DD_HH-MM-SS`.

### File format

```plaintext
📦<mouse-id>_YYYY-MM-DD_HH-MM-SS_processed_YYYY-MM-DD_HH-MM-SS
┣ 📜rig.json
┣ 📜session.json
┣ 📜subject.json
┣ 📜data_description.json
┣ 📜metadata.nd.json
┣ 📜procedures.json
┣ 📜processing.json
┣ 📜qc.json
┣ 📜trialTable.mat
┣ 📂motion_correction
┃ ┣ 📜E#T#DMD#_ALIGNMENTDATA.mat
┃ ┣ 📜E#T#DMD#_REGISTERED_DOWNSAMPLED-##Hz.tif
┃ ┗ ...
┣ 📂source_extraction
┃ ┣ 📜ExperimentSummary.mat
┃ ┗ 📜ExperimentSummary.h5
┗ 📂qc
  ┗ ...
```

### Application notes

Processed assets carry forward the acquisition metadata from the raw asset and update `processing.json` and `qc.json` to reflect the pipeline that was run. Additional modality-specific processed assets MAY replace the example processing folders above with folders named for the specific processing step they contain.

### Relationship to aind-data-schema

Processed assets SHOULD preserve the acquisition metadata files from the source asset. `processing.json` SHOULD describe the processing pipeline that generated the outputs, and `qc.json` SHOULD summarize the quality control results associated with those outputs.

### File Quality Assurances

The following features should be true if the processed asset is to be considered valid:

- The processed asset MUST preserve the acquisition metadata files from the source asset.
- The processed asset MUST include `processing.json` and `qc.json`.
- `source_extraction` outputs, when present, MUST include at least one experiment summary file.
