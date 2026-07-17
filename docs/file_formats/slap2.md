# Standards on SLAP2 optical physiology acquisition

## Version

0.1.0

## Introduction

This document describes the standards for SLAP2 optical physiology data assets. The standard covers both static SLAP2 structure acquisitions and dynamic SLAP2 experiment acquisitions.

## Vocabulary

**Static data**

SLAP2 structure-acquisition files stored under `slap2/static_data`. These files capture structural or reference information associated with a session.

**Dynamic data**

SLAP2 experiment-acquisition files stored under `slap2/dynamic_data`. These files capture the trial-based recordings collected during an experiment session.

**Reference stack**

The `reference_stack` subdirectory within `slap2/dynamic_data`. It contains the required reference image for the dynamic acquisition and MAY also include companion stack files when those files are not already captured in a separate static SLAP2 asset.

## Acquisition/Raw/Primary Data Format

Following SciComp standards, SLAP2 data MUST be saved in the `slap2` modality folder. The timestamped session directory is the data asset root and contains the AIND metadata files for the acquisition. Other modality folders, such as `behavior` and `behavior-videos`, MAY exist alongside `slap2` and SHOULD follow their own standards.

Within the `slap2` folder, `session_vasculature_1p.tif` SHOULD be included when a session-specific 1p vasculature image was collected. If that image is not available, `acquisition.json` SHOULD document the imaging location coordinates. `vasculature_map_annotated.tif` SHOULD be included when available.

### File format

Static SLAP2 structure assets MUST store their modality-specific files in `slap2/static_data`. A common naming convention is:

```plaintext
📂slap2
┣ 📜vasculature_map_annotated.tif (preferred)
┣ 📜session_vasculature_1p.tif (if collected)
┗ 📂static_data
  ┣ 📜structure_YYYYMMDD_HHMMSS_DMD#.meta
  ┣ 📜structure_YYYYMMDD_HHMMSS_DMD#.dat
  ┣ 📜structure_YYYYMMDD_HHMMSS_DMD#.tif
  ┗ 📜structure_YYYYMMDD_HHMMSS_DMD#-REFERENCE.tif
```

Dynamic SLAP2 experiment assets MUST store their modality-specific files in `slap2/dynamic_data`. A common naming convention is:

```plaintext
📂slap2
┣ 📜vasculature_map_annotated.tif (preferred)
┣ 📜session_vasculature_1p.tif (if collected)
┗ 📂dynamic_data
  ┣ 📜acquisition_YYYYMMDD_HHMMSS_DMD#.meta
  ┣ 📜acquisition_YYYYMMDD_HHMMSS_DMD#-TRIAL######(-CYCLE######).dat
  ┣ 📜acquisition_YYYYMMDD_HHMMSS_DMD#-TRIAL######(-CYCLE######).tif
  ┣ 📂reference_stack
  ┃ ┣ 📜refStack_YYYYMMDD_HHMMSS_DMD#(_CONFIG#)-REFERENCE.tif
  ┃ ┣ 📜refStack_YYYYMMDD_HHMMSS_DMD#(_CONFIG#).meta (optional)
  ┃ ┣ 📜refStack_YYYYMMDD_HHMMSS_DMD#(_CONFIG#).dat (optional)
  ┃ ┗ 📜refStack_YYYYMMDD_HHMMSS_DMD#(_CONFIG#).tif (optional)
  ┗ ...
```

### Application notes

The filename stems encode the acquisition time and the DMD index used for the acquisition. The `structure_`, `acquisition_`, and `refStack_` prefixes shown above are recommended conventions rather than required literals; producers MAY use different leading stems provided that companion files still share the same filename stem and preserve the timestamp, DMD, trial, cycle, and `-REFERENCE` semantics. Dynamic acquisitions MAY omit the per-trial TIFF files when the SLAP2 acquisition mode does not generate them, but the `.dat` payloads and their metadata are still required.

The `vasculature_map_annotated.tif` file is preferred and, when present, is expected to be copied from the mouse-level vasculature reference maintained outside the session asset. `session_vasculature_1p.tif` captures the session-specific vasculature image used with the SLAP2 acquisition. If no session-specific 1p vasculature image is available, `acquisition.json` SHOULD document the imaging location coordinates instead.

Within `reference_stack`, a `-REFERENCE.tif` image matching the reference-stack filename stem is required. The corresponding `.meta`, `.dat`, and `.tif` files are optional when the same reference-stack content is already available through a separate static SLAP2 asset.

### Relationship to aind-data-schema

The asset root SHOULD include `instrument.json` and `acquisition.json` created at acquisition time. During upload, `subject.json`, `data_description.json`, `metadata.nd.json`, `procedures.json`, and `processing.json` are added at the asset root. These metadata files describe the acquisition context but are not part of the modality-specific `slap2` payload itself.

### File Quality Assurances

This QA guidance is still in development and may be refined as the SLAP2 workflow matures.

The following features should be true if the data asset is to be considered valid:

- The asset MUST contain exactly one modality directory named `slap2`.
- If a 1p vasculature image was collected for the session, the `slap2` directory MUST contain `session_vasculature_1p.tif`; otherwise, `acquisition.json` SHOULD record the imaging location coordinates.
- The `slap2` directory SHOULD contain `vasculature_map_annotated.tif`.
- Static assets MUST contain `static_data`, and dynamic assets MUST contain `dynamic_data`.
- If a dynamic acquisition TIFF is present, its filename stem MUST match the corresponding acquisition `.dat` payload.
- Every `.dat` file MUST have a matching `.meta` file with the same filename stem.
- Every structure TIFF stack MUST have a matching `-REFERENCE.tif` image with the same filename stem.
- Every reference-stack `.meta`, `.dat`, or `.tif` file, when present, MUST have a matching `-REFERENCE.tif` image with the same filename stem.
