# Standards on behavior video acquisition

## Version

0.3.1

## Introduction

This document describes the standards for acquiring video data from behavior experiments. The goal is to ensure that the data is correctly acquired, logged, and stored in a way that is compatible with AIND's data processing pipelines. We will draw the line on including metadata that relates to the video data itself and NOT to the hardware or software that acquired it. This is to ensure that the data format is self-contained, maintainable and potentially reusable by other applications.

## Raw Data Format

### File format

Raw videos are the files written by the computers attached to the cameras. Unlike most raw data, they are compressed as they are acquired. Their format depends on the scientific question and on software and hardware constraints, but:

- Raw videos MUST declare their color space metadata.
- Cameras without advanced on-chip image processors, such as FLIR cameras, MUST acquire images without on-board gamma correction.
- Raw videos SHOULD be saved in a matroska container, `video.mkv`, which is robust to abnormal termination.

We strongly discourage the use of RAW, uncompressed data.

Following SciComp standards, video data from behavior experiments MUST be saved to the `behavior-videos` modality folder.

Inside this folder, each camera MUST have its own directory, named `<CameraName>`. Each camera folder MUST contain `video.<extension>` and `metadata.csv`. The `video.<extension>` file MUST contain the video data, and the `metadata.csv` file MUST contain the metadata for the video, and be comma-delimited with headers.

`<CameraName>` SHOULD match the name defined in the rig metadata file (`rig.json`)

The folder structure will thus be:

```plaintext
📦behavior-videos
┣ 📂BodyCamera
┃ ┣ 📜metadata.csv
┃ ┗ 📜video.mkv
┗ 📂FaceCamera
┃ ┣ 📜metadata.csv
┃ ┗ 📜video.mkv
```

If multiple streams from the same camera are acquired in the same session, an optional `datetime` suffix MAY be added to the container's name:

```plaintext
📦behavior-videos
┣ 📂BodyCamera_2023-12-25T133015
┃ ┣ 📜metadata.csv
┃ ┗ 📜video.mkv
┗ 📂BodyCamera_2023-12-25T145001
┃ ┣ 📜metadata.csv
┃ ┗ 📜video.mkv
```

The metadata file MUST contain the following columns:

- `ReferenceTime` - Time of the trigger given by hardware (e.g. Harp)

- `CameraFrameNumber` – Frame counter given by the camera API or manually added by user (e.g. using OS counter for webcams)

- `CameraFrameTime` – Frame acquisition time given by the camera API or manually added by the user (e.g. using OS scheduler for webcams).

### Application notes

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

#### Acquisition and Logging

Acquisition can be made using Bonsai. An operator that instantiates the camera can be found in [AllenNeuralDynamics.Core package](https://allenneuraldynamics.github.io/Bonsai.AllenNeuralDynamics/api/AllenNeuralDynamics.Core.AindSpinnakerCapture.html).
This operator is a wrapper around the Spinnaker SDK and provides a simple interface to acquire video data. Since it forces the camera into the correct settings (e.g. Trigger mode, disabled gamma correction, etc...), it guarantees that camera metadata is static and thus easier to track.

Logging can be implemented via the [FFMPEG operator](https://allenneuraldynamics.github.io/Bonsai.AllenNeuralDynamics/api/AllenNeuralDynamics.Core.FfmpegVideoWriter.html).

While we suggest using the aforementioned recipes, the user is free to use any software that can acquire video data, provided it is validated and logged in the correct format.

#### Online encoding

The following nvidia-accelerated ffmpeg settings encode video on acquiring computers attached to many high-speed cameras, and produce raw videos that meet the fidelity requirements of the [Primary Data Format](#primary-data-format):

  - output arguments: `-vf "scale=out_range=full,setparams=range=full:colorspace=bt709:color_primaries=bt709:color_trc=linear" -c:v h264_nvenc -pix_fmt yuv420p -color_range full -colorspace bt709 -color_trc linear -tune hq -preset p3 -rc vbr -cq 18 -b:v 0M -metadata author="Allen Institute for Neural Dynamics" -maxrate 700M -bufsize 350M -f matroska -write_crc32 0`
  - input_arguments: `-colorspace bt709 -color_primaries bt709 -color_range full -color_trc linear`

These settings have been validated and benchmarked to keep up with 3x500fps monochrome cameras with modern computers. The input arguments and `setparams` flags are appropriate for monochrome videos with full color range.

#### Higher bit-depth recordings

For higher bit depth (more than eight) recordings, change the online encoding arguments to:
  - output arguments: `-vf "scale=out_range=full,format=yuv420p10le,setparams=range=full:colorspace=bt709:color_primaries=bt709:color_trc=linear" -c:v hevc_nvenc -pix_fmt p010le -color_range full -colorspace bt709 -color_trc linear -tune hq -preset p4 -rc vbr -cq 12 -b:v 0M -metadata author="Allen Institute for Neural Dynamics" -maxrate 700M -bufsize 350M -f matroska -write_crc32 0`
  - input_arguments: `-colorspace bt709 -color_primaries bt709 -color_range full -color_trc linear`

The pixel format given to the encoder can differ from the pixel format of the video it writes: NVENC takes `p010le` input to write a 10-bit YUV video, which GPUs before NVIDIA's Blackwell generation can encode as HEVC but not as H.264. NVENC only supports 10 bit depth recordings: higher-bit-depth recordings will be downsampled to 10 bits with the settings above.

The `format=yuv420p10le` step is required for `gray` input: without it, `hevc_nvenc` writes near-zero chroma and the video plays green. It follows `scale` because, placed first, it converts the frames to limited range and discards levels that `scale` cannot restore.

#### Python implementation and availability of online encoding settings

They are accessible in python environments through `aind-video-utils`.

### Relationship to aind-data-schema

`<CameraName>` SHOULD match the name defined in the rig metadata file (`rig.json`). Several fields in the metadata can be automatically extracted from this file format (e.g. start and stop of the stream, resolution of the video). However, the user SHOULD ensure that any data pertaining to the hardware configuration (e.g. camera model, exposure time, gain, camera position, etc...) is logged independently from this file format herein described.

aind-data-schema gives uploaded assets a `data_level` of `raw`, so primary videos live in the raw data asset rather than a derived one, even though it has been converted during upload.

### File Quality Assurances

The following features should be true if the data asset is to be considered valid:

- The number of frames in the encoded video MUST match the number of recorded frames and the number of frames in the metadata.

- Check if dropped frames occurred. This should be done in two ways:

  - The difference between adjacent FrameNumber is ALWAYS 1;

  - The difference between adjacent Seconds and adjacent FrameTime SHOULD be very close (<0.5ms);

> [!NOTE]
> While dropped frames are not ideal, they do not necessarily invalidate the data. However, the user should be aware of the potential consequences and/or ways to correct the data asset.

- If using a stable frame rate (this should be inferred from a rig configuration file), the average frame rate SHOULD match the theoretical frame rate;

(optional) If the optional start and stop events are provided, the following temporal order SHOULD be asserted: `All(StartTrigger < Frames  < StopTrigger>)`

## Primary Data Format

### File format

Primary videos are the archival videos an uploaded data asset holds, converted from raw videos by the upload job. A primary video keeps the folder structure and `metadata.csv` of the [Raw Data Format](#raw-data-format), and MUST be named `video.<extension>` and SHOULD be named `video.mp4`.

Archival videos SHOULD accurately represent the captured scene across platforms:

- The container SHOULD be mp4. It SHOULD have fast start, with the `moov` atom at the beginning of the file, and SHOULD contain a `colr` atom.
- The codec MUST be h264 (AVC) or h265 (HEVC), and SHOULD be h264.
- The pixel format MUST be either yuv420p or yuv420p10le. Implementations SHOULD use yuv420p unless 10-bit precision is required.
- The range MUST be standard (limited), not full (pc).
- The color space SHOULD be bt.709, and MAY be bt.2020 or bt.601.
- The primaries, transfer characteristic, and color matrix MUST all follow that color space.
- The transfer characteristic MUST NOT be linear.

Writers SHOULD retain as much of the raw video's visual information as these requirements allow:

- Writers MUST map sensor zero to black and sensor full scale to white, whatever the recorded content. Exposure is the experimenter's choice.
- Sensor values SHOULD be quantized as little as possible. Linear sensor values SHOULD NOT be encoded into a non-linear transfer characteristic such as bt.709 at limited fixed-point precision, as a FLIR camera's on-board gamma correction does.
- The range SHOULD be narrowed at most once, as the final step, and SHOULD be dithered when it is. Intermediate steps SHOULD NOT use dithering.

### Application notes

#### Offline encoding

This transcode step can happen 'offline' after the data have been saved in a temporary video file, and there is no longer time pressure to encode frames in real time. The following ffmpeg settings have been validated to convert videos that declare their color space and have well-ordered time stamps into high-quality archival videos that meet the [Primary Data Format](#primary-data-format):

- output arguments: `-vf "scale=out_color_matrix=bt709:out_range=full:flags=accurate_rnd+full_chroma_int+full_chroma_inp:sws_dither=none,format=yuv420p10le,colorspace=all=bt709:dither=none,scale=out_range=tv:flags=accurate_rnd+full_chroma_int:sws_dither=bayer,format=yuv420p" -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -metadata author="Allen Institute for Neural Dynamics" -movflags +faststart+write_colr`

These settings are a combination of a video filter chain that convert input pixel data into bt.709 color space, and codec settings that compress it using a high-quality codec into a standard video format that is widely supported.

#### Converting non-compliant inputs into archival long-term videos

The offline filters rely on the presentation timestamps and color tags. Many other sources fail to tag the color space, or mangle presentation timestamps, such as h264 in AVI. In this case, the transcoder can repair whichever is wrong ahead of the offline filters:

```
-vf "setpts=N/(FPS)/TB,setparams=color_primaries=bt709:color_trc=linear:colorspace=COLORSPACE:range=RANGE,<offline filters>"
```

- `setpts` re-stamps each frame from its index `N` at the recorded rate `FPS`. AVI stores no presentation timestamps, so ffmpeg reconstructs them, and a frame stamped ahead of its neighbours makes the frames after it look out of order. ffmpeg drops those: 6 of the first 1000 in one 500 fps AIND recording, behind a single frame stamped 6 frames ahead. Re-stamping leaves a conforming source unchanged and discards nothing this standard relies on, since `metadata.csv` carries the timing.
- `setparams` needs to set only the tags a source lacks or has wrong. AIND's Bonsai recordings hold linear light, hence `color_trc=linear`, with no primary rotation, hence `color_primaries=bt709`. `COLORSPACE` is `gbr` for RGB pixel formats, and otherwise the matrix that converted to YUV: `smpte170m` if libswscale's default did. `RANGE` is `pc` or `tv` as recorded. A wrong value shifts black and white levels, and some AIND mpeg4 yuv420p recordings are TV range despite carrying no tag.

#### Higher bit-depth recordings

For 10-bit storage, change the offline encoding arguments to:

```
-vf "scale=out_color_matrix=bt709:out_range=full:flags=accurate_rnd+full_chroma_int+full_chroma_inp:sws_dither=none,format=yuv420p10le,colorspace=all=bt709:dither=none,scale=out_range=tv:flags=accurate_rnd+full_chroma_int:sws_dither=none,format=yuv420p10le"
-c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p10le -metadata author="Allen Institute for Neural Dynamics" -movflags +faststart+write_colr
```

### File Quality Assurances

- `ffprobe` MUST report the video stream's pixel format, range, and color space correctly.
- The primary data format MUST honor the quality assurance of the raw data format.
