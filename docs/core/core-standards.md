# AIND - File Formats Standards

## Core Standards

The goal of this document is NOT to be exhaustive and opinionated. Instead, it should include a minimal list of common patterns that can be easily referenced and reused across all data formats standards guaranteeing a minimal level of consistency and quality.

### Requirements Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this repository are to be interpreted as described in [RFC 2119](https://tools.ietf.org/html/rfc2119).


### Filename conventions

In general, filename conventions will be defined by the specific data format standard. However, some general rules will be enforced:

- Filenames MUST not contain spaces or special characters. [Use this as a reference for special characters](https://en.wikipedia.org/wiki/Filename#Reserved_characters_and_words).
- "Underscore" `_` MUST be used instead of "-" or any other special character to separate words.
- Filenames SHOULD always contain a file extension.
- **Any** file name can be suffixed with a `datetime`. This suffix will ALWAYS be the last suffix in the filename, in case multiple suffixes are used, and will follow the ISO 8601 format. Following Scientific Computing guidelines, if a `datetime` field is added we will adopt the [format `YYYY-MM-DDTHHMMSS` e.g. `2023-12-25T133015`]. The `datetime` will always be read as local-time zone. Should universal time (i.e. UTC) or time-zone information be necessary, users should look into the metadata asset potentially generated with the data.

  - As an example, if two files (`data_stream.bin`) are generated as part of two different acquisition [streams](https://aind-data-schema.readthedocs.io/en/latest/session.html):

    ```plaintext
       📂Modality
        ┣ 📜data_stream_2023-12-25T133015.bin
        ┗ 📜data_stream_2023-12-25T145235.bin
    ```

  - This rule can be generalized to container-like file formats by adding the suffix to the container:

    ```plaintext
        📂Modality
        ┣ 📂FileContainer_2023-12-25T133015
        ┃ ┣ 📜file1.bin
        ┃ ┗ 📜file2.csv
        ┣ 📂FileContainer_2023-12-25T145235
        ┃ ┣ 📜file1.bin
        ┗ ┗ 📜file2.csv
    ```

### Datetime

All `datetime` used in data formats MUST follow the [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) standard. This standard is widely used and supported by most programming languages and libraries. In most cases, we expect `datetime` to be timezone aware, however if no suffix is added, `datetime` will be considered time-zone unaware and representing local time.

The following formats are supported by the ISO 8601 standard and MAY be used:

```plaintext
YYYY-MM-DDTHHMMSS e.g. 2023-12-25T133015

YYYY-MM-DDTHHMMSSZ e.g. 2023-12-25T133015Z

YYYY-MM-DDTHHMMSS±HHMM e.g. 2023-12-25T133015+1200
```

The following examples show how to parse these formats in Python:

``` python
import datetime

tz_unaware = "2023-12-25T133015"
utc = "2023-12-25T133015Z"
tz_aware = "2023-12-25T133015+1200"

print(datetime.datetime.fromisoformat(tz_unaware))
#  2023-12-25 13:30:15
print(datetime.datetime.fromisoformat(utc))
#  2023-12-25 13:30:15+00:00
print(datetime.datetime.fromisoformat(tz_aware))
#  2023-12-25 13:30:15+12:00
```

### Tabular formats

The supported tabular formats are:

#### Comma-separated values (CSV)

CSV files MUST follow a subset of the [RFC 4180](https://tools.ietf.org/html/rfc4180) standard. The following rules will be enforced:

- The first row will ALWAYS be the header row.
- The separator will ALWAYS be a comma `,`.
- The file will ALWAYS be encoded in UTF-8.
- The extension of the file will ALWAYS be `.csv`.
