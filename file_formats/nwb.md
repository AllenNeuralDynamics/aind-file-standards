# Standards on Neurodata Without Borders files

## Version

`0.1.0-draft`

## Introduction

Neurodata Without Borders (NWB) files are a standard file format for neurophysiology data, however there are many topics where NWB is not opinionated. This documents defines AIND's opinions. 

## Basics

We also take this opportunity to remind readers about some NWB basics:

- raw data goes in the `acquisition` group
- processed data goes in the `processing` group
- all timestamps are globally aligned and internally consistent

## Timestamps

- If there is a harp board available, all timestamps will be aligned to the harp clock.

## Events 

- Any other events should be packaged using the [ndx-events](https://github.com/rly/ndx-events) NWB extension.
- Events have `timestamp`, and arbitrary property names and corresponding values.
- Property values can have `meaning`s (e.g. property name "lick" with value "0" means "the mouse licked the left water port").
- All event properties and values must be described by [HED tags](https://www.hedtags.org/) or part of AIND's HED extension.

### Trials Events

- Trials have the same representation as events, but also fill in a `duration` property.

### Application Notes 

[BIDS](https://bids-specification.readthedocs.io/en/stable/) and [HED](https://www.hed-resources.org/en/latest/index.html) have defined two file formats that can generically describe events in a task-agnostic fashion. First, [events.csv](https://bids-specification.readthedocs.io/en/stable/modality-specific-files/task-events.html): 
```
| onset  | duration | <additional columns> | ... |
--------------------------------------------------
| float  | float    | ...                  | ... |
```

Second, [meanings.csv](https://www.hed-resources.org/en/latest/BidsAnnotationQuickstart.html#four-column-spreadsheet-format-anchor):
```
| column_name | column_value | description | HED |
--------------------------------------------------
| str         | Any          | str         | str |
```

A general-purpose, task-agnostic utility for packaging trials into NWB could write this without any custom code necessary.

### Relationship to aind-data-schema

TBD

### File Quality Assurances

TBD
