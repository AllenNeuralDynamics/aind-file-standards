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

- If there is a harp board available, all timestamps will be aligned to the harp clock regardless of the recording device.

## Events 

- Any other events should be packaged using the [ndx-events](https://github.com/rly/ndx-events) NWB extension.
- All event names must be [HED tags](https://www.hedtags.org/)  or part of AIND's HED extension.
- Events have `timestamp`, and arbitrary property names and corresponding values.
- Property values can have `meaning`s (e.g. property name "lick" with value "0" means "the mouse licked the left water port").

### Trials Events

- Trials have the same representation as events, with an additional `duration` property.

### Application Notes 

Should acquisition software produce a `events.csv` file:
```
| timestamp  | property_1 | property_2 | ... |
----------------------------------------------
| float      | Any        | Any        | ... |
```
and a `meanings.csv` file like this:
```
| property_name | property_value | meaning |
--------------------------------------------
| str           | str            | str     |
```

A general-purpose, task-agnostic utility for packaging trials into NWB could write this without any custom code necessary.

### Relationship to aind-data-schema

TBD

### File Quality Assurances

TBD
