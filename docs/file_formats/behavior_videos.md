# Standards on behavior video acquisition

## Version

0.3.0

## Introduction

This document describes the standards for acquiring video data from behavior experiments. The goal is to ensure that the data is correctly acquired, logged, and stored in a way that is compatible with AIND's data processing pipelines. We will draw the line on including metadata that relates to the video data itself and NOT to the hardware or software that acquired it. This is to ensure that the data format is self-contained, maintainable and potentially reusable by other applications.

## Acquisition/Raw/Primary Data Format

Following SciComp standards, video data from behavior experiments MUST be saved to the `behavior-videos` modality folder.

Inside this folder, each camera MUST have its own directory, named `<CameraName>`. Each camera folder MUST contain `video.<extension>` and `metadata.csv`, and SHOULD also contain the preview and poster described below. The `video.<extension>` file MUST contain the video data, and the `metadata.csv` file MUST contain the metadata for the video.

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

The metadata file is expected to contain the following columns:

- `ReferenceTime` - Time of the trigger given by hardware (e.g. Harp)

- `CameraFrameNumber` – Frame counter given by the camera API or manually added by user (e.g. using OS counter for webcams)

- `CameraFrameTime` – Frame acquisition time given by the camera API or manually added by the user (e.g. using OS scheduler for webcams).


As for the video, since the format will depend on the scientific question and software/hardware constrains, we will not enforce a specification. However, we strongly discourage the use of RAW, uncompressed data, and should the user not have a preference, the following default SHOULD be used:

Use a separate online encoder and offline encoder for use during acquisition, and long-term storage, respectively

For the online encoder:

- MUST acquire without any gamma correction
- SHOULD acquire with the mkv format so that files are not corrupted if acquisition is
  abnormally terminated, i.e. the video files should be named like `video.mkv`
- Use `ffmpeg` with the following encoding codec string for online encoding (optimized for compression quality and speed):

  Note: this has been tested with monochrome videos with the raw pixel format
  `gray`. For color videos, the input arguments might need to be altered to
  match the color space of the input.

  - output arguments: `-vf "scale=out_range=full,setparams=range=full:colorspace=bt709:color_primaries=bt709:color_trc=linear" -c:v h264_nvenc -pix_fmt yuv420p -color_range full -colorspace bt709 -color_trc linear -tune hq -preset p3 -rc vbr -cq 18 -b:v 0M -metadata author="Allen Institute for Neural Dynamics" -maxrate 700M -bufsize 350M -f matroska -write_crc32 0`
  - input_arguments: `-colorspace bt709 -color_primaries bt709 -color_range full -color_trc linear`


For offline re-encoding (optimized for quality and size):

- Use mp4 container for the final video, i.e. the video should be named like `video.mp4`.
- output arguments: `-vf "scale=out_color_matrix=bt709:out_range=full:flags=accurate_rnd+full_chroma_int+full_chroma_inp:sws_dither=none,format=yuv420p10le,colorspace=all=bt709:dither=none,scale=out_range=tv:flags=accurate_rnd+full_chroma_int:sws_dither=bayer,format=yuv420p" -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -metadata author="Allen Institute for Neural Dynamics" -movflags +faststart+write_colr`

#### Scaler settings

The offline recipes set libswscale's flags and dither options explicitly. With
ffmpeg 8.1.2 (libswscale 9.5):

- `accurate_rnd` changed no output value from full-range RGB or 4:4:4 input,
  but changed 39% of luma samples from a synthetic 4:2:0 TV-range source.
- `full_chroma_int` and `full_chroma_inp` keep chroma at full resolution. Only
  the first `scale` takes `full_chroma_inp`, since the second reads subsampled
  chroma. They changed nothing for a source with neutral chroma, but did change
  an AIND h264 gbrp recording whose R, G and B planes differ by up to 23 codes.
- The 8-bit recipe's final `scale` is the one step that loses depth, compressing
  full-range 10-bit to TV-range 8-bit. libswscale dithers that step with a fixed
  8x8 ordered matrix whatever `sws_dither` says (`ed`, `none` and `bayer` gave
  identical output on every source tested), so the recipe names `bayer`. No
  other step loses depth, and each sets dithering off.

> [!NOTE]
> That dither rounds full-scale 10-bit white to 236 as well as 235, which put
> 0.1% of luma samples above 235, and none below 16, in one AIND recording.
> BT.709 permits those values and players clip them to white, so the recipes
> add no limiter.

#### Non-conforming sources

The offline filters rely on the presentation timestamps and colour tags the
online recipe writes. A source recorded any other way, such as h264 in AVI, may
carry neither correctly, and a transcoder MUST repair whichever is wrong ahead
of the offline filters:

```
-vf "setpts=N/(FPS)/TB,setparams=color_primaries=bt709:color_trc=linear:colorspace=COLORSPACE:range=RANGE,<offline filters>"
```

- `setpts` re-stamps each frame from its index `N` at the recorded rate `FPS`.
  AVI stores no presentation timestamps, so ffmpeg reconstructs them, and a
  frame stamped ahead of its neighbours makes the frames after it look out of
  order. ffmpeg drops those: 6 of the first 1000 in one 500 fps AIND
  recording, behind a single frame stamped 6 frames ahead.
  Re-stamping leaves a conforming source unchanged and discards nothing this
  standard relies on, since `metadata.csv` carries the timing.
- `setparams` needs to set only the tags a source lacks or has wrong. AIND's
  Bonsai recordings hold linear light, hence `color_trc=linear`, with no
  primary rotation, hence `color_primaries=bt709`. `COLORSPACE` is `gbr` for
  RGB pixel formats, and otherwise the matrix that converted to YUV:
  `smpte170m` if libswscale's default did. `RANGE` is `pc` or `tv` as recorded.
  A wrong value shifts black and white levels, and some AIND mpeg4 yuv420p
  recordings are TV range despite carrying no tag.

#### Higher bit-depth recordings

For higher bit depth (more than eight) recordings, change the online encoding arguments to:
  - output arguments: `-vf "format=yuv420p10le,scale=out_range=full,setparams=range=full:colorspace=bt709:color_primaries=bt709:color_trc=linear" -c:v hevc_nvenc -pix_fmt p010le -color_range full -colorspace bt709 -color_trc linear -tune hq -preset p4 -rc vbr -cq 12 -b:v 0M -metadata author="Allen Institute for Neural Dynamics" -maxrate 700M -bufsize 350M -f matroska -write_crc32 0`
  - input_arguments: `-colorspace bt709 -color_primaries bt709 -color_range full -color_trc linear`

That is the 8-bit online recipe with `format=yuv420p10le` at the head of the
chain, `-c:v hevc_nvenc`, `-pix_fmt p010le`, `-preset p4` and `-cq 12`. The
input arguments are the same, and are what keep `scale=out_range=full` from
reading an untagged rig stream as limited range and stretching it: without them
99.1% of luma samples came out different, by up to 83 of 1023.

NVENC encodes 10 bits only as HEVC, in the `p010le` pixel format, a 10-bit
yuv420: `h264_nvenc` refused both 10-bit formats with "No capable devices
found" on a GPU that encodes 8-bit H.264 fine. NVENC stores no more than 10
bits even from a camera acquiring 12. Keep `.mkv` at the rig, to reduce the
risk of data loss.

`format=yuv420p10le` ahead of the `scale` is REQUIRED for gray input: without
it `hevc_nvenc` writes near-zero chroma and the video plays green, mean RGB
(4, 197, 0) against (124, 124, 124). The 8-bit recipe is unaffected.

For 10-bit storage the offline encoder MUST also change:

```
-vf "scale=out_color_matrix=bt709:out_range=full:flags=accurate_rnd+full_chroma_int+full_chroma_inp:sws_dither=none,format=yuv420p10le,colorspace=all=bt709:dither=none,scale=out_range=tv:flags=accurate_rnd+full_chroma_int:sws_dither=none,format=yuv420p10le"
-c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p10le
-metadata author="Allen Institute for Neural Dynamics" -movflags +faststart+write_colr
```

That is the 8-bit recipe with three changes: `format=yuv420p10le` at the end,
`sws_dither=none` on the last `scale`, since nothing then loses depth, and
`-pix_fmt yuv420p10le`. Everything else stays, the leading `scale` included: it
takes the RGB sources `colorspace` rejects and keeps the transfer conversion
above 8 bits, without which an 8-bit source came out with 226 distinct luma
levels instead of 824.

Acquiring 10 bits before gamma encoding makes the offline encode more accurate,
though 8-bit storage is enough for many applications.

### Preview videos

AIND behavior video runs at 500 fps (62% of 11,202 AVI recordings) or 120 fps
(28%), so a browser streaming `video.mp4` decodes hundreds of frames per second
of playback. A preview for QC in a browser or dashboard SHOULD therefore reduce
the frame rate and keep the source resolution, which is already small enough to
stream. A preview SHOULD be written beside the archival video as
`video_preview.mp4`:

```plaintext
📦behavior-videos
┗ 📂BodyCamera
┃ ┣ 📜metadata.csv
┃ ┣ 📜video.mp4
┃ ┣ 📜video_preview.mp4
┃ ┗ 📜video_poster.jpg
```

A preview MUST drop whole frames rather than resample, so that for a decimation
factor `N`, preview frame `k` is source frame `k * N` (both counted from 0). A
resampling filter such as `fps` keeps unevenly spaced frames whenever the rate
ratio is not an integer, which breaks that mapping.

`N` SHOULD put `source_fps / N` in a 25 to 35 fps band, preferring a
whole-number rate and otherwise the rate closest to the 30 fps target. The band
keeps the whole-number preference from degenerating: unbounded, a 499 fps
source would decimate to
1 fps, its nearest whole-number rate. If no factor lands in the band,
`N = round(source_fps / 30)`, so a source slower than the band keeps every
frame. A 500 fps source gets `N = 20` and a 25 fps preview.

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
- `+write_colr` matches the archival recipe; ffmpeg 8.1.2 writes the mp4 colour
  atom with or without it.
- H.264 `yuv420p` in mp4 is the most widely playable combination.
- Sweeps on one 720x540, 501 fps AIND recording, judged side by side, settled
  on `-preset medium` and CRF 27. Across presets at CRF 24, the preview's size
  varied by 8% and the encode took at most 1.3 s longer than the 12.8 s
  archive alone, but `veryfast` scored 4-6 VMAF below every other preset. At
  `medium`, each CRF step of 3 shrank the preview by 37-47%, and CRF 27 runs
  about 1.6 Mbps with VMAF 85.9 against its lossless decimated frames.

Encode the preview as a second output of the archival ffmpeg process, branching
after the colour chain. A separate pass over the finished `video.mp4` would add
a generation of loss and a second full decode.

A preview can end up to `N - 1` source frames before `video.mp4` (38 ms at
500 fps).

> [!IMPORTANT]
> The File Quality Assurances frame-count requirement applies only to
> `video.mp4`: a preview drops frames by construction, and a poster holds one.

### Poster images

A poster SHOULD be written beside the archival video as `video_poster.jpg`,
giving a QC page, dashboard or `<video poster=...>` a frame without decoding
video.

Browsers display a JPEG that has no ICC profile as sRGB, and ffmpeg embeds none,
so a poster MUST be encoded as sRGB.

Derive the poster from the source rather than from `video.mp4`. On a synthetic
16-band luma ramp, sRGB encoded from linear light was within 2 code values of
exact. Converting the finished BT.709 video to sRGB erred by up to 27, worse
than the 16 of no conversion, because zimg (behind `zscale`) implements BT.709
as the BT.1886 display transfer rather than the camera OETF.

- output arguments, sampling source frame `FRAME`:

  ```
  -vf "select=eq(n\,FRAME),scale=out_color_matrix=bt709:out_range=full:flags=accurate_rnd+full_chroma_int+full_chroma_inp:sws_dither=none,zscale=t=iec61966-2-1:r=full"
  -c:v mjpeg -pix_fmt yuvj420p -q:v 3 -frames:v 1 -update 1
  ```

`select` runs first so the conversion processes one frame. `FRAME` SHOULD be
the frame one second in, `round(FPS)`, since the first frame can be blank or
dark, and MUST NOT exceed `nb_frames - 1`: a `select` matching no frame writes
no file and still exits zero.

A grayscale JPEG would suit monochrome sources, but ffmpeg's `mjpeg` encoder
promotes `-pix_fmt gray` to three-component `yuvj444p`, which is larger than
`yuvj420p` (68,547 against 66,323 bytes on a 720x540 AIND frame).

The poster omits `-metadata`: ffmpeg writes none of it into a JPEG, whose only
comment is the encoder version.

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

### Relationship to aind-data-schema

`<CameraName>` SHOULD match the name defined in the rig metadata file (`rig.json`). Several fields in the metadata can be automatically extracted from this file format (e.g. start and stop of the stream, resolution of the video). However, the user SHOULD ensure that any data pertaining to the hardware configuration (e.g. camera model, exposure time, gain, camera position, etc...) is logged independently from this file format herein described.

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
