# Documentation Standard for Code Ocean Capsules

A Code Ocean capsule is a containerized computational environment that can be used for reproducible code execution, either as a standalone analysis or as part of a pipeline. This standard defines the minimum documentation requirements for Code Ocean capsules to ensure they are usable and understandable by other users.

# Minimum README Contents

Every Code Ocean capsule **must** contain the following sections in its README.

## Capsule Name and Purpose

The top level of the README should contain the capsule name, followed by a concise description of what the capsule does. This should be clear enough for a researcher to understand if this capsule is relevant to their needs.

For example:
```
# Data Quality Checker

This capsule performs automated quality checks on electrophysiology data, including signal-to-noise ratio calculations, spike detection validation, and artifact identification.
```

## Cross-References

The README should contain links to both:
1. The GitHub repository where the code is maintained
2. The Code Ocean location where the capsule is hosted

This ensures users can find the capsule and associated repo regardless of where they encounter it first.

## Primary developers/maintainers

There should be a list of people and email addresses to contact with questions about the capsule. This doesn't need to be a full list of contributors. Only a list of primary contacts.

## Input Data Structure

The README should specify the expected input data structure. This is critical for pipeline usage, where the capsule will be processing new datasets. The documentation should include:

1. The expected file format(s)
2. The required file structure (e.g., directory hierarchy)
3. Any required metadata or configuration files
4. Any assumptions about the data (e.g., sampling rate, units)

For example:
```
## Input Data Structure

This capsule expects electrophysiology data in the following format:
- Raw data files in .nwb format
- Files must be organized in a directory structure: `subject_id/session_id/recording_id.nwb`
- Each .nwb file must contain a 'raw_data' dataset with sampling rate of 30kHz
- A metadata.json file must be present in the root directory with subject information
```

## Output Data Structure

The README should specify what the capsule produces, including:

1. The output file format(s)
2. The output directory structure
3. A description of each output file and its contents
4. Any metadata or log files that are generated

For example:
```
## Output Data Structure

The capsule produces:
- A quality_metrics.csv file containing:
  - signal_to_noise_ratio
  - artifact_percentage
  - spike_count
- A quality_report.html with visualizations
- A log.txt file with processing details
```

## Usage Instructions

The README should provide basic instructions for using the capsule, including:

1. How to run the capsule as part of a pipeline
2. Any required parameters or configuration options
3. Any environment variables that need to be set

For example:
```
## Usage Instructions

To use this capsule in a pipeline:
1. Set the input data directory using the `INPUT_DIR` environment variable
2. Set the output directory using the `OUTPUT_DIR` environment variable
3. Optional: Configure quality thresholds in `config.json`

The capsule will process all .nwb files in the input directory and produce quality metrics in the output directory.
```

# Notes on Different Use Cases

Code Ocean capsules can be used in multiple ways. Depending on the primary use case intended by the developer, the documentation may differ somewhat.

## Pipeline Usage
When used as part of a pipeline, the capsule should be documented as a function that:
1. Takes input data in a specified format
2. Processes it according to defined parameters
3. Produces output in a specified format

The documentation should focus on the input/output interface and any configuration options.

## Reproducible Run Usage
When used for reproducible runs, the capsule should be documented as a complete analysis that:
1. Processes a specific dataset
2. Produces a specific set of results

The documentation should focus on the specific dataset and results, while still maintaining the input/output structure documentation for potential pipeline use.

## Exploration Usage
When used for exploratory data analysis or as an educational resource (e.g., with example notebooks), the documentation should focus on:
1. What the example notebooks and any other sample code demonstrates
2. How to modify them for different datasets
3. Any interactive features or visualization tools 