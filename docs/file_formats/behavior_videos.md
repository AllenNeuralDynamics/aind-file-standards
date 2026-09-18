# Standards on behavior video acquisition

## Version

0.3.0

## 1. Introduction

This document describes the standards for acquiring video data from behavior experiments. The goal is to ensure that the data is correctly acquired, logged, and stored in a way that is compatible with AIND's data processing pipelines. We will draw the line on including metadata that relates to the video data itself and NOT to the hardware or software that acquired it. This is to ensure that the data format is self-contained, maintainable and potentially reusable by other applications.

## 2. Standard for long-term storage of video data

### 2.1 Portability

Archival videos SHOULD accurately represent the captured scene across platforms:

- The container format MUST be widely supported by browsers, and SHOULD be mp4.
- An mp4 container SHOULD have fast start, with the `moov` atom at the beginning of the file, and SHOULD contain a `colr` atom.
- The video stream MUST use a widely supported codec, and SHOULD be h264 (AVC) but MAY be h265 (HEVC).
- The pixel format MUST be a widely supported YUV format, and SHOULD be yuv420p.
- The range MUST be standard (limited), not full (pc).
- The color space SHOULD be widely supported, and SHOULD be bt.709 but MAY be bt.2020 or bt.601.
- The primaries, transfer characteristic, and color matrix MUST all follow that color space.
- The transfer characteristic MUST NOT be linear.
- `ffprobe` MUST report the video stream's pixel format, range, and color space correctly.

Note: the settings during the encode may differ from the format of the produced video, due to the input requirements of the encoder. For example, p010le pixel format may be required as an input format to nvenc to produce correct YUV formatted videos.

### 2.2 Fidelity

Videos SHOULD retain as much of their visual information as §2.1 allows:

- The extrema of the image sensor's range (not of the recorded data) MUST map onto the extrema of the standard range.
- Sensor values SHOULD be quantized as little as possible. Linear sensor values SHOULD NOT be encoded into a non-linear transfer characteristic such as bt.709 at limited fixed-point precision, as a FLIR camera's on-board gamma correction does.
- The range SHOULD be narrowed at most once, as the final step, and SHOULD be dithered when it is. Intermediate steps SHOULD NOT use dithering.
- Every input frame MUST be present in the archival video, and writers MUST check that the frame counts agree.

### 2.3 Naming convention and required metadata

Following SciComp standards, video data from behavior experiments MUST be saved to the `behavior-videos` modality folder.

Inside this folder, each camera MUST have its own directory, named `<CameraName>`. Each camera folder MUST contain `video.<extension>` and `metadata.csv`. The `video.<extension>` file MUST contain the video data, and the `metadata.csv` file MUST contain the metadata for the video, and be comma-delimited with headers.

`<CameraName>` SHOULD match the name defined in the rig metadata file (`rig.json`)

The folder structure will thus be:

```plaintext
📦behavior-videos
┣ 📂BodyCamera
┃ ┣ 📜metadata.csv
┃ ┗ 📜video.mp4
┗ 📂FaceCamera
┃ ┣ 📜metadata.csv
┃ ┗ 📜video.mp4
```

If multiple streams from the same camera are acquired in the same session, an optional `datetime` suffix MAY be added to the container's name:

```plaintext
📦behavior-videos
┣ 📂BodyCamera_2023-12-25T133015
┃ ┣ 📜metadata.cs
┃ ┗ 📜video.mp4
┗ 📂BodyCamera_2023-12-25T145001
┃ ┣ 📜metadata.csv
┃ ┗ 📜video.mp4
```

The metadata file MUST contain the following columns:

- `ReferenceTime` - Time of the trigger given by hardware (e.g. Harp)

- `CameraFrameNumber` – Frame counter given by the camera API or manually added by user (e.g. using OS counter for webcams)

- `CameraFrameTime` – Frame acquisition time given by the camera API or manually added by the user (e.g. using OS scheduler for webcams).

## 3. Standard for short-term storage of video data following acquisition

Video files created by computers attached to cameras will have a format that depends on the scientific question and software/hardware constrains. Intermediate files MUST have declared color space metadata. In addition, intermediate data MUST obey the naming conventions and metadata requirements in §2.3, with the exception that the video container MAY NOT be a `.mp4` file. We strongly discourage the use of RAW, uncompressed data.

## 4. Reference implementation

### 4.1 Recipe for creating short-term videos by computers acquiring video data

This section describes the camera configuration and ffmpeg encoding settings that allow for high-quality 'online' encoding of video by acquiring computers attached to many high-speed cameras.

If acquiring cameras are FLIR or do not have advanced on-chip image processors, then they MUST acquire images without on-board gamma correction. This prevents unnecessary quantization that would result from using the image sensor's limited fixed precision representation of the image data. The color space MUST be tagged in the output video, and the temporary video file SHOULD be saved in a `video.mkv` matroska container which is robust to abnormal termination. The following nvidia-accelerated ffmpeg settings produce high-quality temporary files that are compliant with §2.2.

  - output arguments: `-vf "scale=out_range=full,setparams=range=full:colorspace=bt709:color_primaries=bt709:color_trc=linear" -c:v h264_nvenc -pix_fmt yuv420p -color_range full -colorspace bt709 -color_trc linear -tune hq -preset p3 -rc vbr -cq 18 -b:v 0M -metadata author="Allen Institute for Neural Dynamics" -maxrate 700M -bufsize 350M -f matroska -write_crc32 0`
  - input_arguments: `-colorspace bt709 -color_primaries bt709 -color_range full -color_trc linear`

These settings have been validated and benchmarked to keep up with 3x500fps monochrome cameras with modern computers. They are accessible in python environments through `aind-video-utils`.

### 4.2 Recipe for converting short-term videos into archival long-term videos

This transcode step can happen 'offline' after the data have been saved in a temporary video file, and there is no longer time pressure to encode frames in real time. The following ffmpeg settings have been validated to convert videos that declare their color space and have well-ordered time stamps into high-quality archival videos that comply with §2.1:

- output arguments: `-vf "scale=out_color_matrix=bt709:out_range=full:sws_dither=none,format=yuv420p10le,colorspace=ispace=bt709:all=bt709:dither=none,scale=out_range=tv:sws_dither=none,format=yuv420p" -c:v libx264 -preset veryslow -crf 18 -pix_fmt yuv420p -metadata author="Allen Institute for Neural Dynamics" -movflags +faststart+write_colr`

The output MUST be named `video.mp4`.

These settings are a combination of a video filter chain that convert input pixel data into bt.709 color space, and codec settings that compress it using a high-quality codec into a standard video format that is widely supported.

#### 4.2.1 Converting non-compliant inputs into archival long-term videos

The offline filters rely on the presentation timestamps and color tags. Many other sources fail to tag the color space, or mangle presentation time stamps , such as h264 in AVI. In this case, the transcoder can repair whichever is wrong ahead of the offline filters:

```
-vf "setpts=N/(FPS)/TB,setparams=color_primaries=bt709:color_trc=linear:colorspace=COLORSPACE:range=RANGE,<offline filters>"
```

- `setpts` re-stamps each frame from its index `N` at the recorded rate `FPS`. AVI stores no presentation timestamps, so ffmpeg reconstructs them, and a frame stamped ahead of its neighbours makes the frames after it look out of order. ffmpeg drops those: 6 of the first 1000 in one 500 fps AIND recording, behind a single frame stamped 6 frames ahead. Re-stamping leaves a conforming source unchanged and discards nothing this standard relies on, since `metadata.csv` carries the timing.
- `setparams` needs to set only the tags a source lacks or has wrong. AIND's Bonsai recordings hold linear light, hence `color_trc=linear`, with no primary rotation, hence `color_primaries=bt709`. `COLORSPACE` is `gbr` for RGB pixel formats, and otherwise the matrix that converted to YUV: `smpte170m` if libswscale's default did. `RANGE` is `pc` or `tv` as recorded. A wrong value shifts black and white levels, and some AIND mpeg4 yuv420p recordings are TV range despite carrying no tag.


### 4.3 Higher bit-depth recordings

For higher bit depth (more than eight) recordings, change the online encoding arguments to:
  - output arguments: `-vf "format=yuv420p10le,scale=out_range=full,setparams=range=full:colorspace=bt709:color_primaries=bt709:color_trc=linear" -c:v hevc_nvenc -pix_fmt p010le -color_range full -colorspace bt709 -color_trc linear -tune hq -preset p4 -rc vbr -cq 12 -b:v 0M -metadata author="Allen Institute for Neural Dynamics" -maxrate 700M -bufsize 350M -f matroska -write_crc32 0`
  - input_arguments: `-colorspace bt709 -color_primaries bt709 -color_range full -color_trc linear`

The intermediate video must be named `video.mkv`.

For 10-bit storage the offline encoder must also change:

```
-vf "colorspace=ispace=bt709:all=bt709:dither=none,scale=out_range=tv:sws_dither=none,format=yuv420p10le"
-c:v libx264 -preset veryslow -crf 18 -pix_fmt yuv420p10le -metadata author="Allen Institute for Neural Dynamics" -movflags +faststart+write_colr
```

### 4.4 Application notes

We currently support the following cameras:
    - `Blackfly S BFS-U3-16S2M`
    - `Blackfly S BFS-U3-04S2M`

Additional cameras could be supported but the user should provide the necessary information to integrate it with the current pipeline.

> [!CAUTION]
> It is the user's responsibility to ensure that:
> 
> - The camera is correctly calibrated and that the settings are appropriate for the experiment.
> 
> - Unless there is a reason not to, the default logging pattern should always follow the following logic: (Stop trigger if needed) -> Start logging -> Start Camera -> Start Trigger -> Acquire data -> Stop Trigger -> Stop Logging. This guarantees that all relevant events are recorded.
> 
> - Trigger generation only starts AFTER the camera hardware has been initialized. This is to ensure that the camera is ready to receive the first trigger signal.
> 
> - For each trigger of the trigger source (e.g. Harp Behavior board) a corresponding camera exposure should occur. One example where this can be violated is if the set exposure is greater than the trigger frequency.
> 
> - In absence of dropped frames (defined as skips in the FrameNumber > 1) the metadata.csv file is expected to be aligned with the video file.
> 
> - (Optional) Start trigger and Stop trigger events should be available for QC.
> 
> - (Optional) The logs of all triggers (regardless of whether they are logged in the metadata.csv) should be saved for redundancy.

#### 4.4.1 Acquisition and Logging

Acquisition can be made using Bonsai. An operator that instantiates the camera can be found in [AllenNeuralDynamics.Core package](https://allenneuraldynamics.github.io/Bonsai.AllenNeuralDynamics/api/AllenNeuralDynamics.Core.AindSpinnakerCapture.html).
This operator is a wrapper around the Spinnaker SDK and provides a simple interface to acquire video data. Since it forces the camera into the correct settings (e.g. Trigger mode, disabled gamma correction, etc...), it guarantees that camera metadata is static and thus easier to track.

Logging can be implemented via the [FFMPEG operator](https://allenneuraldynamics.github.io/Bonsai.AllenNeuralDynamics/api/AllenNeuralDynamics.Core.FfmpegVideoWriter.html).

While we suggest using the aforementioned recipes, the user is free to use any software that can acquire video data, provided it is validated and logged in the correct format.

### 4.5 Relationship to aind-data-schema

`<CameraName>` SHOULD match the name defined in the rig metadata file (`rig.json`). Several fields in the metadata can be automatically extracted from this file format (e.g. start and stop of the stream, resolution of the video). However, the user SHOULD ensure that any data pertaining to the hardware configuration (e.g. camera model, exposure time, gain, camera position, etc...) is logged independently from this file format herein described.

### 4.6 File Quality Assurances

The following features should be true if the data asset is to be considered valid:

- The number of frames in the encoded video MUST match the number of recorded frames and the number of frames in the metadata.

- Check if dropped frames occurred. This should be done in two ways:

  - The difference between adjacent FrameNumber is ALWAYS 1;

  - The difference between adjacent Seconds and adjacent FrameTime SHOULD be very close (<0.5ms);

> [!NOTE]
> While dropped frames are not ideal, they do not necessarily invalidate the data. However, the user should be aware of the potential consequences and/or ways to correct the data asset.

- If using a stable frame rate (this should be inferred from a rig configuration file), the average frame rate SHOULD match the theoretical frame rate;

(optional) If the optional start and stop events are provided, the following temporal order SHOULD be asserted: `All(StartTrigger < Frames  < StopTrigger>)`
