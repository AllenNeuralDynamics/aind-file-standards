# AIND File Standards

This repository contains the specifications for file formats across all data modalities at the Allen Institute for Neural Dynamics. These standards define both the input (raw data from acquisition systems) and output (processed/NWB) formats for each modality.  

Here the term "modality" is meant to encompass any unique recording system, behavior task or stimulus delivery system that could potentially be used in isolation or paired with another modality. 

## Purpose

This repository serves as the single source of truth for file format specifications. All data pipeline repositories should reference these standards rather than maintaining their own copies. Any proposed changes to file formats should be submitted as pull requests to this repository.

This allows us to define the unique file structure/format for each modality and also the expected format of the modality-specific NWB file. 

This information can serve as the basis for modality-specific processing pipelines, which will generate modality-specific NWB files. Processes downstream of these modality-specific pipelines will be built for combining the modality-specific NWB files into a single NWB file containing all data from a given experiment (e.g. behavior + physiology).

## Structure

Each modality has its own markdown file following a standardized format:

- `<modality-name>.md` - Contains the complete specification for the input/outoput data for a given modality

## Modality Standard Template

All modality standards documents must include the following sections (naming should be consistent to maintain machine readability):

### Version Information
- Current version number following semantic versioning (MAJOR.MINOR.PATCH)
- Version history (optional)

### Introduction
- Brief description of the modality
- Scope of the standard

### Raw Data Format
- Complete specification of the format for raw data coming directly from acquisition systems
- Folder structure (using ASCII folder diagrams)
- File naming conventions
- File formats and internal organization

### File Quality Assurance (for Raw Data) [Optional]
- Validation criteria for raw data files
- Tests that should be performed to ensure data integrity

### NWB File Format
- Specification for how data should be stored in Neurodata Without Borders (NWB) format
- Required NWB components and extensions
- Organization of modality-specific data within the NWB structure
- Validation criteria for NWB files

### Application Notes
- Tools and libraries for reading/writing the data
- Example code snippets
- Common usage patterns

### Relationship to aind-data-schema
- How the modality relates to fields in acquisition.json, instrument.json, etc.
- Which schema fields are required for this modality
- Ideally a link to the associated metadata mapper

### Vocabulary
- Definitions of domain-specific terms used in the standard

## Contributing

1. Submit a pull request with your proposed changes
2. Include justification for the change
3. Update the version number according to semantic versioning principles
4. Notify affected pipeline teams of the proposed change and include them as reviewers on the PR