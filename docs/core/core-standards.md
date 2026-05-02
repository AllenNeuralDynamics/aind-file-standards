# AIND - File Formats Standards

## Core Standards

The goal of this document is NOT to be exhaustive and opinionated. Instead, it should include a minimal list of common patterns that can be easily referenced and re-used across all data formats standards guaranteeing a minimal level of consistency and quality.

### Filename conventions

In general, filename conventions will be defined by the specific data format standard. However, some general rules will be enforced:

- Filenames must not contain spaces or special characters. [Use this as a reference for special characters](https://en.wikipedia.org/wiki/Filename#Reserved_characters_and_words).
- "Underscore" `_` should be used instead of "-" or any other special character to separate words.
- Filenames must always contain a file extension.
- **Any** file name can be suffixed with a `datetime`. This suffix will ALWAYS be the last suffix in the filename, in case multiple suffixes are used. Following Scientific Computing guidelines, if a `datetime` field is added we will adopt the [format `YYYY-MM-DDTHHMMSS` e.g. `2023-12-25T133015Z`, `2023-12-25T123015-0100`]. For backwards compatibility, the `datetime` is allowed to be time-zone unaware (i.e. no `Z` or offset suffix), however this practice is discouraged.


  - As an example, if two files (`data_stream.bin`) are generated as part of two different acquisition [streams](https://aind-data-schema.readthedocs.io/en/latest/session.html):

    ```plaintext
       📂Modality
        ┣ 📜data_stream_2023-12-25T133015Z.bin
        ┗ 📜data_stream_2023-12-25T145235Z.bin
    ```

  - This rule can be generalized to container-like file formats by adding the suffix to the container:

    ```plaintext
        📂Modality
        ┣ 📂FileContainer_2023-12-25T133015+1000
        ┃ ┣ 📜file1.bin
        ┃ ┗ 📜file2.csv
        ┣ 📂FileContainer_2023-12-25T145235+1000
        ┃ ┣ 📜file1.bin
        ┗ ┗ 📜file2.csv
    ```

#### Datetime format in filenames

All `datetime` used in data formats should closely follow the [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) standard. This standard is widely used and supported by most programming languages and libraries. Unfortunately, the strict ISO specification is not always compatible with filenames due to special characters. To address this, we will instead target the parsing formats supported by the Python standard library  [`datetime.datetime.fromisoformat`](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat) method.

In most cases, we expect `datetime` to be timezone aware, however if no suffix is added, `datetime` will be considered time-zone unaware.

The following formats are supported, in order of preference:

```plaintext
YYYY-MM-DDTHHMMSSZ e.g. 2023-12-25T133015Z

YYYY-MM-DDTHHMMSS±HHMM e.g. 2023-12-25T133015+1200

YYYY-MM-DDTHHMMSS e.g. 2023-12-25T133015
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

### Datetime

In all other cases where a `datetime` field is used (e.g. data, metadata fields), the full ISO 8601 standard should be respected. To ensure consistency, make sure you use datetime libraries that support ISO 8601 parsing and serialization. For example, in Python, the `datetime` module can be used to parse and serialize ISO 8601 `datetimes`:

``` python
import datetime
dt = datetime.datetime.fromisoformat("2023-12-25T13:30:15+12:00")
```

or using `pydantic`:

```python
from pydantic import BaseModel, AwareDatetime
class Event(BaseModel):
    timestamp: datetime.datetime
    enforced_aware: AwareDatetime

event = Event(timestamp="2023-12-25T13:30:15+12:00", enforced_aware="2023-12-25T13:30:15+12:00")
event.model_dump_json()
```

As in filenames, in order of preference:

  - Use UTC `datetime`s whenever possible.
  - Use timezone-aware `datetime`s whenever possible.
  - If timezone information is not available, use timezone-unaware `datetime`s.

### Tabular formats

The supported tabular formats are:

#### Comma-separated values (CSV)

CSV files will follow a subset of the [RFC 4180](https://tools.ietf.org/html/rfc4180) standard. The following rules will be enforced:

- The first row will always be the header row.
- The separator will always be a comma `,`.
- The file will always be encoded in UTF-8.
- The extension of the file will always be `.csv`.
