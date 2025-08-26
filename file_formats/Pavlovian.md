# Standards on Pavlovian Conditioning data

## Version

`0.1.0`

## Introduction
This document describes the standards for the acquisition of Pavlovian conditioning behavior in the Allen Institute for Neural Dynamics. So far, this behavior has been combined with fiber photometry. Experimental control and data acquisition codes can be found in this [repo](https://github.com/AllenNeuralDynamics/PavlovianCond_Bonsai).

## Raw Data Format
Following SciComp standards, behavior related files are all saved in the subfolder named "behavior". Other modalities such as FIP data should be saved in their own subfolder named "fib" (short for "fiber photometry"). 

A single session of behavior data should be organized under the `behavior` directory. An acquisition for a single session should be nested under a sub directory named following the core standards for file naming convention found [here](https://github.com/AllenNeuralDynamics/aind-file-standards/blob/main/core/core-standards.md#filename-conventions).  Mostly, this is for cases where the recording gets interrupted. When the system restarts under the same session, it can be added to a new folder. A session folder structure should look like the following:


```plaintext
📦 Session Folder
┣ 📂 <behavior>
┃ ┣ HarpMessages_34YYYY-MM-DDTHH_MM_SS.bin
┃ ┣ HarpMessages_49YYYY-MM-DDTHH_MM_SS.bin
┃ ┣ HarpMessages_51YYYY-MM-DDTHH_MM_SS.bin
┃ ┣ HarpMessages_78YYYY-MM-DDTHH_MM_SS.bin
┃ ┣ HarpMessages_95YYYY-MM-DDTHH_MM_SS.bin
┃ ┣ SoundCardMessages_YYYY-MM-DDTHH_MM_SS.bin
┃ ┣ PavParams_YYYY-MM-DDTHH_MM_SS.csv
┃ ┣ TrialN_TrialType_ITI_YYYY-MM-DDTHH_MM_SS.csv
┃ ┣ TS_Airpuff_YYYY-MM-DDTHH_MM_SS.csv
┃ ┣ TS_CS1_YYYY-MM-DDTHH_MM_SS.csv
┃ ┣ TS_CS2_YYYY-MM-DDTHH_MM_SS.csv
┃ ┣ TS_CS3_YYYY-MM-DDTHH_MM_SS.csv
┃ ┣ TS_CS4_YYYY-MM-DDTHH_MM_SS.csv
┃ ┣ TS_FIP_YYYY-MM-DDTHH_MM_SS.csv
┃ ┣ TS_Lick_YYYY-MM-DDTHH_MM_SS.csv
┃ ┣ TS_Reward_YYYY-MM-DDTHH_MM_SS.csv
┃ ┣ TS_RewardB_YYYY-MM-DDTHH_MM_SS.csv
┃ ┣ TS_ManualAirpuff_YYYY-MM-DDTHH_MM_SS.csv
┃ ┣ TS_ManualCS1_YYYY-MM-DDTHH_MM_SS.csv
┃ ┣ TS_ManualCS2_YYYY-MM-DDTHH_MM_SS.csv
┃ ┣ TS_ManualCS3_YYYY-MM-DDTHH_MM_SS.csv
┃ ┣ TS_ManualCS4_YYYY-MM-DDTHH_MM_SS.csv
┃ ┣ TS_ManualReward_YYYY-MM-DDTHH_MM_SS.csv
┃ ┣ TS_ManualRewardB_YYYY-MM-DDTHH_MM_SS.csv
┃ 
┣ 📂 <behavior_videos>
┣ 📂 <fib>
```

### Old (~2025.April)
HarpMessages_: Raw harp messages from the HarpBehaviorBoard, see Neurogear description

SoundCardMessages_: Raw harp messages from the HarpSoundBoard, see Neurogear description

PavParams_: Parameters used to run the experiments.

TrialN_TrialType_ITI_: Trial data
- TrialNumber: int 0,1,2,3,4,...
- TrialType: 1-10:CS1; 11-20:CS2; 21-30:CS3; 31-40:CS4
- Reward: True or False
- TotalRewards: number of acquired reward# so far
- ITI_s: time from the current outcome to the next CS onset
- Punishment: True or False

TS_: Time stamps of behavior-related events. Software(Windows_OS) timestamps.

*rewardB: Big, not used in the behavior so far


### New (2025.April~)
Now all the csv files have header and for `TS_` files

The first column is Software(Windows_OS) timestamps and the second column Harp timestamps.





## Acquiring data under this format

Data acquisition code that generates data in this format is available from the [data acquisition repository](https://github.com/AllenNeuralDynamics/PavlovianCond_Bonsai).

## Relationship to aind-data-schema
rig.json and session.json define the experimental conditions.
