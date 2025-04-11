# Standards on Neurodata Without Borders files

## Version

`0.1.0-draft`

## Introduction

Neurodata Without Borders (NWB) files are a standard file format for neurophysiology data, however there are many topics where NWB is not opinionated. This documents defines AIND's opinions. 

## Basics

We also take this opportunity to remind readers about some general NWB basics:

- Raw data goes in the `acquisition` group
- Processed data goes in the `processing` group
- The root level `session_start_time` is a timezone-aware datetime defining the start of acquisition.
- All timestamps must be relative to the same point in time and require no additional alignment to compare. This is defined in the root level `timestamps_reference_time`, which defaults to `session_start_time`.
- It is not required that timestamps for different data streams be identical (i.e. resample data such that all timeseries have exactly the same timestamps).

## HARP

- At AIND, if there is a HARP board available, timestamps must utilize HARP TTLs to transform timestamps to a common timebase. It is insufficient to store a lookup table.
- If it is necessary to preserve the original, misaligned timestamps for a timeseries, they can be stored separately in an appropriately named `DynamicTable`, e.g. `ephys_temporal_alignment` with an `original_timestamps` column. 

## Events 

- Any events should be packaged using the [ndx-events](https://github.com/rly/ndx-events) NWB extension.
- We represent all events in an `EventTable` and all event descriptions in a `MeaningsTable` table.
- Events have a `timestamp` property, and arbitrary property names and corresponding values.
- Property values can have `meaning`s (e.g. property name "lick" with value "0" means "the mouse licked the left water port").
- All event properties and values must be described by [HED tags](https://www.hedtags.org/) or part of AIND's HED extension.
- Trials are represented as events, but also fill in the event `duration` property.

### Application Notes 

[BIDS](https://bids-specification.readthedocs.io/en/stable/) and [HED](https://www.hed-resources.org/en/latest/index.html) have defined two file formats that can generically describe events in a task-agnostic fashion. 

First, [events.csv](https://bids-specification.readthedocs.io/en/stable/modality-specific-files/task-events.html), which describes individual events: 
```
| onset  | duration | HED | <additional columns> | ... |
--------------------------------------------------
| float  | float    | str | ...                  | ... |
```

Second, [event-descriptions.csv](https://www.hed-resources.org/en/latest/BidsAnnotationQuickstart.html#four-column-spreadsheet-format-anchor), which describes event types and their values:
```
| column_name | column_value | description | HED |
--------------------------------------------------
| str         | Any          | str         | str |
```

BIDS likewise has a standard JSON representations of [event descriptions](https://www.hed-resources.org/en/latest/BidsAnnotationQuickstart.html#json-event-sidecars).

A general-purpose, task-agnostic utility for could write this in to NWB ***without any custom code necessary*** ([for example](https://gist.github.com/dyf/3e9aef7330ead36f14f0a11099ab619c)).

### Relationship to aind-data-schema

TBD

### File Quality Assurances

TBD
