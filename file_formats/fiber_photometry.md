# Fiber Photometry Files

## FIP

In most cases, FIP fiber photometry data will be stored in 3 CSV files (extracted traces + timestamp; 6 time-series) and 3 bin files (raw camera-detector movie file).

For example:

```plaintext
📦 fib
┣ FIP_DataG_2024-06-05T08_25_33.csv
┣ FIP_DataIso_2024-06-05T08_25_33.csv
┣ FIP_DataR_2024-06-05T08_25_33.csv
┣ FIP_RawG_2024-06-05T08_25_33.bin
┣ FIP_RawIso_2024-06-05T08_25_33.bin
┗ FIP_RawR_2024-06-05T08_25_33.bin
```
The file names are `FIP_[channel-name]_[datetime].csv`.  The `[channel-name]` token can be one of the following:

* `DataG`: data for green channel
* `DataR`: data for red channel
* `DataIso`: data for isosbestic channel
  
### CSV files

These files have no headers. Each column is a timeseries, ordered as follows:

* timestamp (in millisecond, total time of the day)
* ROI0 (corresponding to fiber branch1) values
* ROI1 (corresponding to fiber branch2) values
* ...  (depending on how many fibers are used; in most of the experiments: ROI0-3/4branches)
* Blank ROI: CMOS dark count floor signal

### BIN files

[TBD - how to interpret these files?]

Flat binary file of the raw CMOS movie data recorded with `MatrixWriter` Bonsai node (https://bonsai-rx.org/docs/api/Bonsai.Dsp.MatrixWriter.html).

* 200x200 pixles
* 16bit depth
* 20Hz (effective sampling frequency per channel)
* column major

These files are optional and may be removed once QC is complete. 
