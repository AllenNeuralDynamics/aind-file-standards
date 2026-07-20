# AIND File Standards

This repository contains the file standards for the Allen Institute for Neural Dynamics (AIND).

## Goal

The overarching goal of this effort is to give users, developers, and any system that produces or consumes information within AIND a clear set of specifications for structuring acquired data. This will make it easier to validate acquisition pipelines, ensure a more consistent user experience, and equip everyone with a common set of tools for working with that data.

## Contributing

Contributions are welcome! These will likely fall into one of the following categories:

- **New Proposals**: If you have a new specification to add, place it in the directory that matches its scope:
  - `docs/file_formats` for a self-contained, reusable format specification (e.g. `harp`, `nwb`).
  - `docs/modalities` for a specification covering a whole acquisition modality that composes several file formats (e.g. `ecephys`, `fip`).

  See [docs/core/contributing.md](docs/core/contributing.md) for the distinction between the two.
- **Improvements to Existing Formats**: If you have suggestions for improving existing specifications, please submit a pull request with your changes.

For more information on how to submit contributions, refer to [docs/core/contributing.md](docs/core/contributing.md).
