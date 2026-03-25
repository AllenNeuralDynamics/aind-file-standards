# Standards on behavior curriculum metadata

## Version

0.1.0

## Introduction

This document describes the standard for storing behavior curriculum metadata alongside behavior data assets. The [`aind-behavior-curriculum`](https://github.com/AllenNeuralDynamics/aind-behavior-curriculum) package provides models and resolving logic for defining behavior curricula across tasks and platforms. A key output of this system is the [`TrainerState`](https://github.com/AllenNeuralDynamics/aind-behavior-curriculum/blob/feecaf6d70fc20f23ed5b02d1be47414234b3b9c/src/aind_behavior_curriculum/trainer.py#L28) model — a serializable record of the curriculum state (active stage, policies, and task parameters) that gave rise to a given behavior session.

This standard prescribes a location, naming convention, and format for persisting the `TrainerState` so that it is:

- Immutable and mapped 1:1 to its parent session data asset;
- Self-contained and independent of `aind-data-schema`;
- Consistent across all behavior platforms that adopt `aind-behavior-curriculum`.

> [!NOTE]
> This standard is scoped to the storage of the `TrainerState` file. It does NOT prescribe how curriculum progression logic should be implemented, nor does it define the schema of the `TrainerState` itself; that is owned by the [`aind-behavior-curriculum`](https://github.com/AllenNeuralDynamics/aind-behavior-curriculum) package.

> [!IMPORTANT]
> Due to the recursive nature of the curriculum algorithm, each session is expected to interact with two `TrainerState` instances:
> - The curriculum state at the time of session acquisition, which is the output of the previous iteration of the curriculum loop and serves as the stage input for the session that is about to be acquired. This is the "ground truth" record of the curriculum state that gave rise to the session and is the primary target of this standard, and it should be thus considered immutable after being consumed by the acquisition process. This is the file described in the "Acquisition/Raw/Primary Data Format" section below.
> - The "suggestion" `TrainerState` produced by the curriculum's trainer logic at the end of a session, which serves as a suggestion for the next iteration of the curriculum loop. This file is considered ephemeral and it is NOT the target of this standard. While it can be stored with the dataset for debugging or record-keeping purposes, it is not guaranteed to be consumed/materialized by the acquisition process and should NOT be considered a reliable record of the curriculum state for a given session.


## Acquisition/Raw/Primary Data Format

A file named `trainer_state.json` SHALL be stored inside the `behavior/` modality folder of the data asset. This file contains the serialized `TrainerState` at the time of session acquisition.

```plaintext
📦<session_data_asset>
┣ 📂behavior
┃ ┣ 📜trainer_state.json
┃ ┗ ... (other behavior data files)
┗ ...
```

It should be noted that this file, following the standard naming convention, can be appended with a `datetime` suffix if multiple curriculum states need to be stored for the same session (e.g. multiple behavior streams):

```plaintext
📦<session_data_asset>
┣ 📂behavior
┃ ┣ 📜trainer_state_<datetime>.json
┃ ┗ ... (other behavior data files)
┗ ...
```

The file:

- MUST be a valid JSON file encoded in UTF-8 (see [core standards](../core/core-standards.md#file-formatting-standards)).
- MUST contain a serialized instance of the `TrainerState` model from `aind-behavior-curriculum`.
- MUST use the `.json` extension.

### Application notes

The `TrainerState` is typically produced by the curriculum's trainer logic at the end of a session. The serialization is handled by `aind-behavior-curriculum` itself:

```python
from aind_behavior_curriculum.trainer import TrainerState

# After curriculum resolution
trainer_state: TrainerState = ...  # resolved by the trainer
trainer_state_json = trainer_state.model_dump_json()
# Save to file
with open("behavior/trainer_state.json", "w", encoding="utf-8") as f:
    f.write(trainer_state_json)
```

for loading:

```python
from pathlib import Path
from aind_behavior_curriculum.trainer import TrainerState

trainer_state_file = next(Path("behavior").glob("trainer_state*.json"))
trainer_state = TrainerState.model_validate_json(trainer_state_file.read_text(encoding="utf-8"))
```

### Relationship to aind-data-schema

This standard is intentionally independent of `aind-data-schema`. The `trainer_state.json` file exists as a standalone artifact within the data asset and does not require any field in `aind-data-schema` to function.

The information in the trainer state MUST NOT be serialized into any of the metadata of `aind-data-schema` (e.g. Acquisition metadata) to avoid bloating the schema with task-specific fields. Nevertheless, users can choose to curate, and include, high-value information from the trainer state (e.g. active stage name) into `aind-data-schema` Acquisition metadata as a denormalized record for easier querying. This is outside the scope of this standard and is left to the discretion of the user.

### File Quality Assurances

- If it exists, it must be able to be found using "trainer_state*.json" glob pattern in the `behavior/` modality folder.
- The file MUST be valid JSON and parseable by `aind-behavior-curriculum`'s `TrainerState` model.
- The file MUST be encoded in UTF-8.
