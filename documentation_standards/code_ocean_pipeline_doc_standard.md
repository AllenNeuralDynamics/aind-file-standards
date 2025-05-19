# Documentation Standard for Code Ocean Pipelines

A Code Ocean pipeline is a computational workflow that combines multiple capsules to process data in a defined sequence. This standard defines the minimum documentation requirements for Code Ocean pipelines to ensure they are usable and understandable by other users.

# Minimum README Contents

Every Code Ocean pipeline **must** contain the following sections in its README.

## Pipeline Name and Purpose

The top level of the README should contain the pipeline name, followed by a concise description of what the pipeline does. This should be clear enough for a researcher to understand if this pipeline is relevant to their needs.

For example:
```
# Electrophysiology Processing Pipeline

This pipeline processes raw electrophysiology data through a series of quality checks, spike sorting, and analysis steps to produce standardized, analysis-ready datasets.
```

## Cross-References

The README must contain links to both:
1. The GitHub repository where the pipeline is maintained
2. The Code Ocean location where the pipeline is hosted

This ensures users can find the pipeline and associated repo regardless of where they encounter it first.

## Primary developers/maintainers

There should be a list of people and email addresses to contact with questions about the pipeline. This doesn't need to be a full list of contributors. Only a list of primary contacts.

## Pipeline Overview

The README must provide a high-level overview of the pipeline, including:
1. A description of the overall workflow
2. The purpose of each processing stage
3. Any assumptions about the input data
4. The expected output data

For example:
```
## Pipeline Overview

This pipeline processes electrophysiology data through three main stages:
1. Quality Control: Checks signal quality and identifies artifacts
2. Spike Sorting: Clusters spikes into putative single units
3. Analysis: Computes firing rates and other metrics

The pipeline expects raw .nwb files and produces processed datasets suitable for downstream analysis.
```

## Pipeline Structure

The README must document the structure of the pipeline, including:

1. A list of all capsules used in the pipeline
2. The purpose of each capsule
3. Links to each capsule's documentation
4. The flow of data between capsules

For example:
```
## Pipeline Structure

This pipeline uses the following capsules in sequence:

1. **Data Quality Checker** ([Code Ocean](link) | [GitHub](link))
   - Purpose: Validates raw data quality
   - Input: Raw .nwb files
   - Output: Quality metrics and validated data

2. **Spike Sorter** ([Code Ocean](link) | [GitHub](link))
   - Purpose: Clusters spikes into units
   - Input: Validated data from Quality Checker
   - Output: Sorted spike times and cluster metrics

3. **Unit Analyzer** ([Code Ocean](link) | [GitHub](link))
   - Purpose: Computes unit statistics
   - Input: Sorted spikes from Spike Sorter
   - Output: Firing rates and other metrics
```

## Input Data Structure

The README must specify the expected input data structure for the pipeline as a whole, including:

1. The expected file format(s)
2. The required file structure (e.g., directory hierarchy)
3. Any required metadata or configuration files
4. Any assumptions about the data

For example:
```
## Input Data Structure

The pipeline expects:
- Raw data files in .nwb format
- Files must be organized in a directory structure: `subject_id/session_id/recording_id.nwb`
- Each .nwb file must contain a 'raw_data' dataset with sampling rate of 30kHz
- A metadata.json file must be present in the root directory with subject information
```

## Output Data Structure

The README must specify what the pipeline produces as a whole, including:

1. The output file format(s)
2. The output directory structure
3. A description of each output file and its contents
4. Any metadata or log files that are generated

For example:
```
## Output Data Structure

The pipeline produces:
- A processed_data/ directory containing:
  - quality_metrics.csv: Signal quality metrics for each recording
  - sorted_units.nwb: Spike-sorted data in NWB format
  - unit_metrics.csv: Firing rates and other unit statistics
- A pipeline_log.txt file with processing details
- A summary_report.html with visualizations
```

## Usage Instructions

The README must provide basic instructions for using the pipeline, including:

1. How to run the pipeline
2. Any required parameters or configuration options
3. Any environment variables that need to be set
4. How to monitor pipeline progress

For example:
```
## Usage Instructions

To run the pipeline:
1. Set the input data directory using the `INPUT_DIR` environment variable
2. Set the output directory using the `OUTPUT_DIR` environment variable
3. Optional: Configure processing parameters in `config.json`
4. Run the pipeline using the Code Ocean interface or command line

Monitor pipeline progress in the Code Ocean interface or check the pipeline_log.txt file.
```

# Additional Optional Sections

While not required, the following sections may be helpful:

* **Development** - Information for developers who want to modify the pipeline
* **Testing** - How to test the pipeline with sample data
* **Troubleshooting** - Common issues and their solutions
* **Performance** - Expected runtime and resource requirements 