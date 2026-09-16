# Standards on behavior video acquisition

## Version

0.3.0

## 1. Introduction

This document describes the standards for acquiring video data from behavior experiments. The goal is to ensure that the data is correctly acquired, logged, and stored in a way that is compatible with AIND's data processing pipelines. We will draw the line on including metadata that relates to the video data itself and NOT to the hardware or software that acquired it. This is to ensure that the data format is self-contained, maintainable and potentially reusable by other applications.

The spec is divided into an informational background section to motivate why a spec is needed, a normative long-term storage specification for how videos should be stored at rest, a normative short-term storage specification for computers acquiring video, and a reference set of ffmpeg settings that meet both short-term and long-term specifications. Finally, extensions specifications for preview videos and preview poster images are also presented.

## 2. Background

Despite the importance of behavior, the video record of behaviors is an afterthought in most experiments. Experimenters want the to be able to view what happened in a behavior, and assume that video files faithfully represent what happened. But achieving that requires that we make correct decisions about each of the many steps that happen between a lens forming an image onto an image sensor, and light coming out of a monitor when the file is played. Consumer-oriented systems make these choices for you, making the process seem simple. But in behavior experiments, we often use machine vision cameras which leave the decisions to the experimenter. At AIND our experimental setups use machine vision cameras, and so we must understand the steps between acquisition and display if we want the video record to reflect what happened. Without a basic understanding of what goes into a video format, it is only too easy distort how your video data appears on a screen.

Most people that have worked with image data in programs might find this surprising. An image is just a grid of RGB pixels, right? It seems like a simple representation, until you wonder how the values in your matrix correspond to light levels, or how the computer knows which red you were referring to. These simple representations of image data use many layers of standards that are built around human visual system. Without knowledge of these standards, it's easy to make mistakes such as assuming that the RGB values linearly represent the amount of light, when they are instead logarithmic, or that all you need to do is pipe your camera's intensities to a ffmpeg process writing a mp4 and you'll get an accurate representation of what happened - which is far from true.

This standard specifies decisions at many steps between acquiring an image and producing long-term video records. It is out of scope to explain each of these terms here, but we will briefly introduce the ones that we make a statement about.

A video file such a `video.mp4` is a digital multimedia container following a certain format, in this case mp4. These containers wrap different types of media, such as video, audio, and text, each of which is stored as a stream of information. The video stream is a compressed representation of a sequence of images. There are a few standard video compression algorithms (codecs), such as h264 (AVC) or h265 (HEVC) which lossily compress images in a way that is tuned to keep what's important to our visual system, and discards what we're not sensitive to. The images themselves have different physical representations in computer memory, called pixel format, and the most common of which is not RGB but instead YUV which separates the lightness of each pixel from the color. Each pixel value encodes a particular combination of light to be presented to the viewer as a point in a color space, which is a named coordinate system that combines particular primary red green and blue colors with a transfer function that maps points in the coordinate system to light levels through an exponential function. The portion of the digital representation that codes for light also varies, and usually does not use the entire range in a 8 bit representation, instead using a 'standard range' within it even though it's a limited subset of the full range. The video container, and the video stream within it, often declares the details required to interpret the images and correctly present it to a viewer.

Computer operating systems, screens, and the web have settled on some dominant standards at each of these levels. Most devices and browsers support mp4 containers, h264 codec, yuv420p pixel format (a variant of a YUV representation), and bt.709 color space with standard (limited) range. While you can create video files that do not adhere to these standards, many devices, video players, and browsers, will misinterpret the video data and distort the images when they are viewed. We therefore want to produce standard videos with correct metadata that allows most viewers of our videos files to see what actually happened in an experiment, as it happened.


## 3. Standard for long-term storage of video data

### 3.1 Portability

Archival videos SHOULD accurately represent the captured scene across platforms, and therefore should obey the following properties. The container format MUST be widely supported by browsers, and SHOULD be a mp4 container. If mp4 is used, it SHOULD be optimized for web view and SHOULD have fast start where the `moov` atom is at the beginning of the file, and SHOULD contain a `colr` atom to allow accurate display. The video stream MUST use a widely supported codec, and SHOULD be h264 (AVC) but MAY be h265 (HEVC). The pixel format in the video stream MUST be a widely supported YUV format, and SHOULD be yuv420p. The range MUST be standard (limited) and MUST NOT be full (pc). The color space SHOULD be a widely supported one and SHOULD be bt.709 but MAY be bt.2020 or bt.601. The color space used MUST extend to the primaries, transfer characteristic, and color matrix. The transfer characteristic MUST NOT be linear. The video stream MUST correctly report its pixel format, range, and color space when probed with `ffprobe`.

Note: the settings during the encode may differ from the format of the produced video, due to the input requirements of the encoder. For example, p010le pixel format may be required as an input format to nvenc to produce correct YUV formatted videos.

### 3.2 Fidelity

Videos SHOULD retain as much of their visual information as possible while satisfying the requirements of §3.1. The entire chain packaging camera data into archival videos must therefore be careful to avoid artificially truncating, limiting, or unnecessarily quantizing image sensor pixel values.

The dynamic range of the image sensor MUST be cleanly mapped onto the range of the archival video. This means that the extrema of an image sensor's range (not realized data) MUST map onto the extrema of the standard range during processing. The image sensor's reads SHOULD be quantized as little as possible. As a consequence, encoding linear sensor values into logarithmic transfer characteristic representations such as bt.709 SHOULD NOT be done in limited fixed point precision, such as on board the FLIR image sensor itself. When the range is narrowed, it SHOULD be done at most once as a final step and SHOULD use dithering to avoid visual banding. Intermediate steps SHOULD NOT use dithering.

Input frames MUST all be present in the archival result. Temporary intermediate files that are not standard, such as .avi files that contain h264 encoded video streams, often cause frames to be dropped when converting to the standards outlined above. When generating the archival video files, writers MUST ensure the frame counts agree.

### 3.3 Naming convention and required metadata

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

## 4. Standard for short-term storage of video data following acquisition

Video files created by computers attached to cameras will have a format that depends on the scientific question and software/hardware constrains. Intermediate files MUST have declared color space metadata. In addition, intermediate data MUST obey the naming conventions and metadata requirements in §3.3, with the exception that the video container MAY NOT be a `.mp4` file. We strongly discourage the use of RAW, uncompressed data.

## 5. Reference implementation

### 5.1 Motivation for reference architecture

We split the process of creating videos appropriate for long-term storage from video data into two phases. The first phase is designed to allow computers acquiring video data to keep up with potentially many cameras each acquiring at high frame rates, and storing that video data in video files that are manageable to write, store, and transmit while retaining visual quality. The second stage converts this temporary video into an archival video offline, which eliminates the time pressure of keeping up with camera frames as they arrive. By separating the two phases, we can have the 'best of both worlds' where acquiring computers can handle large numbers of frames per second, and allow the production of archival videos that accurately represent the behavioral experiment while being highly compressed and widely portable.

### 5.2 Recipe for creating short-term videos by computers acquiring video data

This section describes the camera configuration and ffmpeg encoding settings that allow for high-quality 'online' encoding of video by acquiring computers attached to many high-speed cameras.

If acquiring cameras are FLIR or do not have advanced on-chip image processors, then they MUST acquire images without on-board gamma correction. This prevents unnecessary quantization that would result from using the image sensor's limited fixed precision representation of the image data. The color space MUST be tagged in the output video, and the temporary video file SHOULD be saved in a `video.mkv` matroska container which is robust to abnormal termination. The following nvidia-accelerated ffmpeg settings produce high-quality temporary files that are compliant with §3.2.

  - output arguments: `-vf "scale=out_range=full,setparams=range=full:colorspace=bt709:color_primaries=bt709:color_trc=linear" -c:v h264_nvenc -pix_fmt yuv420p -color_range full -colorspace bt709 -color_trc linear -tune hq -preset p3 -rc vbr -cq 18 -b:v 0M -metadata author="Allen Institute for Neural Dynamics" -maxrate 700M -bufsize 350M -f matroska -write_crc32 0`
  - input_arguments: `-colorspace bt709 -color_primaries bt709 -color_range full -color_trc linear`

These settings have been validated and benchmarked to keep up with 3x500fps monochrome cameras with modern computers. They are accessible in python environments through `aind-video-utils`.

### 5.3 Recipe for converting short-term videos into archival long-term videos

This transcode step can happen 'offline' after the data have been saved in a temporary video file, and there is no longer time pressure to encode frames in real time. The following ffmpeg settings have been validated to convert videos that declare their color space and have well-ordered time stamps into high-quality archival videos that comply with §3.1:

- output arguments: `-vf "scale=out_color_matrix=bt709:out_range=full:flags=accurate_rnd+full_chroma_int+full_chroma_inp:sws_dither=none,format=yuv420p10le,colorspace=all=bt709:dither=none,scale=out_range=tv:flags=accurate_rnd+full_chroma_int:sws_dither=bayer,format=yuv420p" -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -metadata author="Allen Institute for Neural Dynamics" -movflags +faststart+write_colr`

The output MUST be named `video.mp4`.

These settings are a combination of a video filter chain that convert input pixel data into bt.709 color space, and codec settings that compress it using a high-quality codec into a standard video format that is widely supported.

#### 5.3.1 Converting non-compliant inputs into archival long-term videos

The offline filters rely on the presentation timestamps and color tags. Many other sources fail to tag the color space, or mangle presentation time stamps , such as h264 in AVI. In this case, the transcoder can repair whichever is wrong ahead of the offline filters:

```
-vf "setpts=N/(FPS)/TB,setparams=color_primaries=bt709:color_trc=linear:colorspace=COLORSPACE:range=RANGE,<offline filters>"
```

- `setpts` re-stamps each frame from its index `N` at the recorded rate `FPS`. AVI stores no presentation timestamps, so ffmpeg reconstructs them, and a frame stamped ahead of its neighbours makes the frames after it look out of order. ffmpeg drops those: 6 of the first 1000 in one 500 fps AIND recording, behind a single frame stamped 6 frames ahead. Re-stamping leaves a conforming source unchanged and discards nothing this standard relies on, since `metadata.csv` carries the timing.
- `setparams` needs to set only the tags a source lacks or has wrong. AIND's Bonsai recordings hold linear light, hence `color_trc=linear`, with no primary rotation, hence `color_primaries=bt709`. `COLORSPACE` is `gbr` for RGB pixel formats, and otherwise the matrix that converted to YUV: `smpte170m` if libswscale's default did. `RANGE` is `pc` or `tv` as recorded. A wrong value shifts black and white levels, and some AIND mpeg4 yuv420p recordings are TV range despite carrying no tag.


### 5.4 Higher bit-depth recordings

For higher bit depth (more than eight) recordings, change the online encoding arguments to:
  - output arguments: `-vf "format=yuv420p10le,scale=out_range=full,setparams=range=full:colorspace=bt709:color_primaries=bt709:color_trc=linear" -c:v hevc_nvenc -pix_fmt p010le -color_range full -colorspace bt709 -color_trc linear -tune hq -preset p4 -rc vbr -cq 12 -b:v 0M -metadata author="Allen Institute for Neural Dynamics" -maxrate 700M -bufsize 350M -f matroska -write_crc32 0`
  - input_arguments: `-colorspace bt709 -color_primaries bt709 -color_range full -color_trc linear`

The intermediate video must be named `video.mkv`.

For 10-bit storage the offline encoder must also change:

```
-vf "scale=out_color_matrix=bt709:out_range=full:flags=accurate_rnd+full_chroma_int+full_chroma_inp:sws_dither=none,format=yuv420p10le,colorspace=all=bt709:dither=none,scale=out_range=tv:flags=accurate_rnd+full_chroma_int:sws_dither=none,format=yuv420p10le" -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p10le -metadata author="Allen Institute for Neural Dynamics" -movflags +faststart+write_colr
```

### 5.5 Application notes

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

#### 5.5.1 Acquisition and Logging

Acquisition can be made using Bonsai. An operator that instantiates the camera can be found in [AllenNeuralDynamics.Core package](https://allenneuraldynamics.github.io/Bonsai.AllenNeuralDynamics/api/AllenNeuralDynamics.Core.AindSpinnakerCapture.html).
This operator is a wrapper around the Spinnaker SDK and provides a simple interface to acquire video data. Since it forces the camera into the correct settings (e.g. Trigger mode, disabled gamma correction, etc...), it guarantees that camera metadata is static and thus easier to track.

Logging can be implemented via the [FFMPEG operator](https://allenneuraldynamics.github.io/Bonsai.AllenNeuralDynamics/api/AllenNeuralDynamics.Core.FfmpegVideoWriter.html).

While we suggest using the aforementioned recipes, the user is free to use any software that can acquire video data, provided it is validated and logged in the correct format.

### 5.6 Relationship to aind-data-schema

`<CameraName>` SHOULD match the name defined in the rig metadata file (`rig.json`). Several fields in the metadata can be automatically extracted from this file format (e.g. start and stop of the stream, resolution of the video). However, the user SHOULD ensure that any data pertaining to the hardware configuration (e.g. camera model, exposure time, gain, camera position, etc...) is logged independently from this file format herein described.

### 5.7 File Quality Assurances

The following features should be true if the data asset is to be considered valid:

- The number of frames in the encoded video MUST match the number of recorded frames and the number of frames in the metadata.

- Check if dropped frames occurred. This should be done in two ways:

  - The difference between adjacent FrameNumber is ALWAYS 1;

  - The difference between adjacent Seconds and adjacent FrameTime SHOULD be very close (<0.5ms);

> [!NOTE]
> While dropped frames are not ideal, they do not necessarily invalidate the data. However, the user should be aware of the potential consequences and/or ways to correct the data asset.

- If using a stable frame rate (this should be inferred from a rig configuration file), the average frame rate SHOULD match the theoretical frame rate;

(optional) If the optional start and stop events are provided, the following temporal order SHOULD be asserted: `All(StartTrigger < Frames  < StopTrigger>)`

## 6. Extensions

### 6.1 Preview video

#### 6.1.1 Motivation

AIND behavior video runs at 500 fps (62% of 11,202 AVI recordings) or 120 fps (28%), so a browser streaming `video.mp4` decodes hundreds of frames per second of playback. A preview for QC in a browser or dashboard SHOULD therefore reduce the frame rate and keep the source resolution, which is already small enough to stream.

#### 6.1.2 Fidelity

A preview video MUST be an accurate preview of the archival video. Specifically, the frames SHOULD be derived from the same source as individual frames in the archival video. Transcoding the archival video itself may introduce more loss than intended, as it is already compressed for long-term storage. Instead, the preview SHOULD be generated from the same source as the archival video, and ideally it SHOULD use the same exact filter chain so the archival video and previews are alternate compressions of the same exact pixel data.

The preview SHOULD have a clear frame mapping to the archival video. A preview MUST drop whole frames rather than resample, so that for a decimation factor `N`, preview frame `k` is source frame `k * N` (both counted from 0). A resampling filter such as `fps` keeps unevenly spaced frames whenever the rate ratio is not an integer, which breaks that mapping.

#### 6.1.3 Streaming performance

`N` SHOULD put `source_fps / N` in a 25 to 35 fps band, preferring a whole-number rate and otherwise the rate closest to the 30 fps target. The band keeps the whole-number preference from degenerating: unbounded, a 499 fps source would decimate to 1 fps, its nearest whole-number rate. If no factor lands in the band, `N = round(source_fps / 30)`, so a source slower than the band keeps every frame. A 500 fps source gets `N = 20` and a 25 fps preview. The group of pictures (GOP) SHOULD be around two seconds for seeking performance.

#### 6.1.4 Reference implementation

The following ffmpeg settings produce high-quality previews of the archival video, using the same source and having a clear mapping between the preview frames and the archival frames.

- output arguments, for a decimation factor `N` and preview rate `PREVIEW_FPS`:

  ```
  -vf "select=not(mod(n\,N))" -fps_mode passthrough
  -c:v libx264 -preset medium -crf 27 -pix_fmt yuv420p -g <2 * PREVIEW_FPS>
  -metadata author="Allen Institute for Neural Dynamics" -movflags +faststart+write_colr
  ```

- `-fps_mode passthrough` is REQUIRED. `select` leaves the advertised frame
  rate at the source's, so any constant-frame-rate stage duplicates the retained
  frames back up to it: 999 frames instead of 50 from a 1000-frame, 500 fps
  source. `passthrough` rules that out whatever ffmpeg's default for the muxer.
- `-g` caps keyframe spacing at two seconds; x264's 250-frame default is 10 s
  at 25 fps, which makes scrubbing in a browser sluggish. Scene-change
  detection still inserts some keyframes sooner.

Encode the preview as a second output of the archival ffmpeg process, branching after the color chain. A separate pass over the finished `video.mp4` would add a generation of loss and a second full decode.

A preview can end up to `N - 1` source frames before `video.mp4` (38 ms at 500 fps).

### 6.2 Poster image

#### 6.2.1 Motivation

A poster SHOULD be written beside the archival video as `video_poster.jpg`,
giving a QC page, dashboard or `<video poster=...>` a frame without decoding
video.

#### 6.2.2 Fidelity

Browsers display a JPEG that has no ICC profile as sRGB, and ffmpeg embeds none,
so a poster MUST be encoded as sRGB. Posters SHOULD be derived from the source
rather than from archival `video.mp4`.

#### 6.2.3 Reference implementation
- output arguments, sampling source frame `FRAME`:

  ```
  -vf "select=eq(n\,FRAME),scale=out_color_matrix=bt709:out_range=full:flags=accurate_rnd+full_chroma_int+full_chroma_inp:sws_dither=none,zscale=t=iec61966-2-1:r=full"
  -c:v mjpeg -pix_fmt yuvj420p -q:v 3 -frames:v 1 -update 1
  ```

`select` runs first so the conversion processes one frame. `FRAME` SHOULD be
the frame one second in, `round(FPS)`, since the first frame can be blank or
dark, and MUST NOT exceed `nb_frames - 1`: a `select` matching no frame writes
no file and still exits zero.

Encode the poster as an additional of the archival ffmpeg process, branching before the color chain.

### 6.3 Naming convention
A preview and poster SHOULD be written beside the archival video as
`video_preview.mp4`:

```plaintext
📦behavior-videos
┗ 📂BodyCamera
┃ ┣ 📜metadata.csv
┃ ┣ 📜video.mp4
┃ ┣ 📜video_preview.mp4
┃ ┗ 📜video_poster.jpg
```
