# HSC_to_LSST
This code performs image cutout degradation from HSC to LSST-like images. It supports the *grizy* bands.

It performs the following steps:
1. Read or query HSC image cutouts and their PSF models.
2. Change the zero point of the HSC images to match LSST.
3. Convolve the HSC images with a kernel to match the LSST PSF.
4. Change the pixel scale from HSC to LSST (0.168 arcsec/pixel to 0.2 arcsec/pixel, flux-conserving).
5. Add Poisson noise to match the LSST exposure.
6. Add sky background to match LSST.
7. Save the degraded images.

## Citation
If you use this code in your research, please cite the LLST SLSC static strong lensing challenge paper:

(Clecio et al. 2026, in preparation)

## Requirements
- Python 3.9+
- numpy
- scipy
- astropy
- photutils
- tqdm
- reproject
- lenstronomy (fallback for LSST properties if not provided)
- scikit-learn==1.5.2 (gaussian mixture model to sample LSST properties)

## Installation

You can install the package using pip:

```bash
pip install git+https://github.com/furcelay/HSC_to_LSST#egg=HSC_to_LSST
```

## Usage
There are three python scripts provided (installed as console scripts):
1. `query_hsc`: queries HSC cutouts and PSF models from a .fits astropy table of object coordinates. The minimum required columns are 'ra' and 'dec'.
2. `query_degrade_hsc`: queries HSC cutouts and PSF models, degrades them to LSST-like images, and saves the results. Requires a .fits table with 'ra' and 'dec'.
3. `read_degrade_hsc`: reads HSC cutouts and PSF models from local files, degrades them to LSST-like images, and saves the results. 

You can get help on each script using the `-h` or `--help` flag, e.g.:

```bash
query_hsc -h
```

The code is easily customizable by creating new scripts or importing the functions in your own code.

## Querying HSC Cutouts
To query HSC cutouts, use the `query_hsc` script. 
The input is an astropy table .fits file with at least 'ra' and 'dec' columns. 
Other columns can be present but will be ignored.

To access the HSC database, you need to provide your HSC SSP CAS user and password. You can ask for an account
[here](https://hsc-release.mtk.nao.ac.jp/doc/index.php/data-access__pdr3/). You can provide the username and password
either via command line arguments or environment variables `HSC_SSP_CAS_USERNAME` and `HSC_SSP_CAS_PASSWORD` (recommended).

Querying is the bottleneck of the process, hence we provide options to optimize the query speed by using multiple connections
and parallel processes. The number of connections (`nc`) should be <10 to avoid overloading the server, otherwise you may get blocked.
If this happens, then wait for a while and reduce the number of connections.
Generally, 8 connections is a good choice. Note that if you are running multiple instances of the script in parallel
(e.g., running the script on two different input tables at the same time),
you should reduce the number of connections accordingly (even if they run on different machines!).

The number of parallel processes (`-np`) can be adjusted based on your CPU cores. Generally using a few more than the 
number of connections gives the best performance (e.g. 10 processes for 8 connections).

This code is based on the `downloadCutout.py` and `downloadPsf.py` 
scripts from the [HSC repository](https://hsc-gitlab.mtk.nao.ac.jp/ssp-software/data-access-tools/-/tree/master/pdr3?ref_type=heads) 
which are used internally to download cutouts and PSF models. 
All rights to those scripts are reserved by the original authors.

The script will create an output directory (by default is the same as the input table plus '_query') 
and save the cutouts and PSF models based on their position within the table: 000000_img_r.fits, 000000_psf_r.fits, etc.

```bash
usage: query_hsc [-h] [--output_dir OUTPUT_DIR] [--hsc_release {pdr3_dud_rev,pdr3_dud,pdr3_wide,pdr2_dud,pdr2_wide,pdr1_udeep,pdr1_deep,pdr1_wide,pdr1_ssp_uh_cosmos}] [--num_processes NUM_PROCESSES] [--num_connections NUM_CONNECTIONS] [--timeout TIMEOUT] [--hsc_username HSC_USERNAME]
                 [--hsc_password HSC_PASSWORD] [--restart] [--retry]
                 input_table

positional arguments:
  input_table           Input astropy table .fits file

options:
  -h, --help            show this help message and exit
  --output_dir, -o OUTPUT_DIR
                        Output directory
  --hsc_release {pdr3_dud_rev,pdr3_dud,pdr3_wide,pdr2_dud,pdr2_wide,pdr1_udeep,pdr1_deep,pdr1_wide,pdr1_ssp_uh_cosmos}
                        HSC release to use, note that this defines the depth (wide or deep)
  --num_processes, -np NUM_PROCESSES
                        Number of processes to use
  --num_connections, -nc NUM_CONNECTIONS
                        Number of connections to use for the HSC query
  --timeout, -t TIMEOUT
                        Timeout for the HSC query
  --hsc_username HSC_USERNAME
                        HSC username, otherwise use env variable HSC_SSP_CAS_USERNAME
  --hsc_password HSC_PASSWORD
                        HSC password, otherwise use env variable HSC_SSP_CAS_PASSWORD
  --restart, -r         Restart the query from the last successful query
  --retry, -rr          Restart and retry failed queries
```

## Image degradation
To degrade HSC images to LSST-like images, use either the `query_degrade_hsc` or `read_degrade_hsc` scripts.

### Query and degrade
The `query_degrade_hsc` takes the same input as `query_hsc`, but performs the degradation after querying the HSC cutouts and PSF models.

```bash
usage: query_degrade_hsc [-h] [--output_dir OUTPUT_DIR] [--coadd_years COADD_YEARS] [--hsc_release {pdr3_dud_rev,pdr3_dud,pdr3_wide,pdr2_dud,pdr2_wide,pdr1_udeep,pdr1_deep,pdr1_wide,pdr1_ssp_uh_cosmos}] [--num_processes NUM_PROCESSES] [--num_connections NUM_CONNECTIONS] [--timeout TIMEOUT]
                         [--hsc_username HSC_USERNAME] [--hsc_password HSC_PASSWORD] [--rms_frac_thresh RMS_FRAC_THRESH] [--max_mag_change MAX_MAG_CHANGE] [--restart] [--retry]
                         input_table

positional arguments:
  input_table           Input file

options:
  -h, --help            show this help message and exit
  --output_dir, -o OUTPUT_DIR
                        Output directory
  --coadd_years, -y COADD_YEARS
                        Years of coadd to use, can be a number or 'single_visit'
  --hsc_release {pdr3_dud_rev,pdr3_dud,pdr3_wide,pdr2_dud,pdr2_wide,pdr1_udeep,pdr1_deep,pdr1_wide,pdr1_ssp_uh_cosmos}
                        HSC release to use, note that this defines the depth (wide or deep)
  --num_processes, -np NUM_PROCESSES
                        Number of processes to use
  --num_connections, -nc NUM_CONNECTIONS
                        Number of connections to use for the HSC query
  --timeout, -t TIMEOUT
                        Timeout for the HSC query
  --hsc_username HSC_USERNAME
                        HSC username, otherwise use env variable HSC_SSP_CAS_USERNAME
  --hsc_password HSC_PASSWORD
                        HSC password, otherwise use env variable HSC_SSP_CAS_PASSWORD
  --rms_frac_thresh RMS_FRAC_THRESH
                        Threshold for the RMS_HSC/RMS_LSST for the zero point conversion
  --max_mag_change MAX_MAG_CHANGE
                        Maximum magnitude variation allowed during the zero point conversion
  --restart, -r         Restart the query from the last successful query
  --retry, -rr          Restart and retry failed queries
```

### Read and degrade
The `read_degrade_hsc` script reads HSC cutouts and PSF models from local files and performs the degradation. 
The input is the directory where the cutouts and PSF models are stored. The filenames should be in the output format
of the `query_hsc` script `f"{id:06d}_{img/psf}_{band}.fits"` (e.g. 000000_img_r.fits, 000000_psf_r.fits, etc).

```bash
usage: read_degrade_hsc [-h] [--output_dir OUTPUT_DIR] [--coadd_years COADD_YEARS] [--hsc_release {pdr3_dud_rev,pdr3_dud,pdr3_wide,pdr2_dud,pdr2_wide,pdr1_udeep,pdr1_deep,pdr1_wide,pdr1_ssp_uh_cosmos}] [--num_processes NUM_PROCESSES] [--rms_frac_thresh RMS_FRAC_THRESH] [--max_mag_change MAX_MAG_CHANGE]
                        [--restart] [--retry]
                        input_directory

positional arguments:
  input_directory       Input directory

options:
  -h, --help            show this help message and exit
  --output_dir, -o OUTPUT_DIR
                        Output directory
  --coadd_years, -y COADD_YEARS
                        Years of coadd to use, can be a number or 'single_visit'
  --hsc_release {pdr3_dud_rev,pdr3_dud,pdr3_wide,pdr2_dud,pdr2_wide,pdr1_udeep,pdr1_deep,pdr1_wide,pdr1_ssp_uh_cosmos}
                        HSC depth to use, can be 'wide' or 'deep'
  --num_processes, -np NUM_PROCESSES
                        Number of processes to use
  --rms_frac_thresh RMS_FRAC_THRESH
                        Threshold for the RMS_HSC/RMS_LSST for the zero point conversion
  --max_mag_change MAX_MAG_CHANGE
                        Maximum magnitude variation allowed during the zero point conversion
  --restart, -r         Restart the query from the last successful query
  --retry, -rr          Restart and retry failed queries
```

### Controlling quality / rejection criteria
There are two LSST quality criteria that might not be always met: background RMS and seeing FWHM. 
Both quantities can only be increased during the degradation process. 
If the HSC image quality is too poor compared to LSST, the degradation will not be able to reach the LSST quality.

#### Background RMS
The background RMS of the HSC image should be lower than that of LSST, 
otherwise the noise cannot be increased to match LSST. Even if the HSC RMS is lower than LSST, it has to be lower
enough to allow for a reasonable increase in noise so that the noise correlation produced during 
rebinning and PSF convolution does not dominate the final noise. A strict condition on the RMS ratio would
lead to many rejections, especially for the wide HSC field, hence we provide a more flexible approach.

There are two parameters to control the background RMS quality:
1. `rms_frac_thresh`: the threshold for the ratio RMS_HSC / RMS_LSST. 
If this threshold is met, the image is directly degraded.
If not met, the image is scaled to match the LSST background RMS 
as long as the magnitude difference between HSC and LSST is within `max_mag_change`.
2. `max_mag_change`: the maximum allowed magnitude change during the RMS scaling. You can see
the magnitude change applied to each image in the output log file.

The default value is `rms_frac_thresh = 0.3`, which is generally a good quality cut for HSC deep field. 
For the wide field, you might want to relax this threshold to avoid too many rejections.

#### Seeing FWHM
The seeing FWHM of the HSC image is generally better than LSST, except in the r band. 
Even in the r band, the HSC seeing is often comparable or better than LSST, hence the degradation is still possible
but won't be able to produce the best seeing LSST images. Currently, if the HSC FWHM is larger than LSST,
the PSF convolution step is skipped. This way, the final FWHM will be within the LSST range for all bands, 
but not necessarily matching the LSST FWHM distribution on the r band.

![alt text](https://github.com/furcelay/HSC_to_LSST/blob/main/plots/hsc_to_lsst_g_psf.png?raw=true)
![alt text](https://github.com/furcelay/HSC_to_LSST/blob/main/plots/hsc_to_lsst_r_psf.png?raw=true)
![alt text](https://github.com/furcelay/HSC_to_LSST/blob/main/plots/hsc_to_lsst_i_psf.png?raw=true)

## Example
Here is an example command to degrade HSC images using the `query_degrade_hsc` script. 
The threshold for the background RMS between the HSC and LSST is set to 30%: RMS_HSC < 0.3 * RMS_LSST. 
Which is generally a good quality cut. If not met, the image is scaled to match the LSST background RMS as long 
as the magnitude difference between HSC and LSST is within 0.2 mag.

first get the example input table example_HSC_query.fits (currently random coordinates in the HSC footprint):
```bash
hsc_query_example
```

Then run the query and degradation:
(ensure to store your HSC credentials in the environment variables HSC_SSP_CAS_USERNAME and HSC_SSP_CAS_PASSWORD)
```bash
query_degrade_hsc example_HSC_query.fits --output_dir example_degraded_images \
 --coadd_years 1 --rms_frac_thresh 0.3 --max_mag_change 0.2
```