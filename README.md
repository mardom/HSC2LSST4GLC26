# HSC2LSST4GLC26 — HSC-to-LSST Image Degradation Notebooks

Workflow notebooks and vendored `HSC_to_LSST` package for degrading 5-band (*grizy*) Hyper Suprime-Cam (HSC) strong-lensing cutouts (`0.168"/pix`) into Rubin Observatory LSST-like 1-year coadd cutouts (`41x41` pixels at `0.2"/pix`).

## Ordered Notebook Versions

Notebooks are ordered chronologically (`01` → `05`) with cell outputs cleared for clean version control:

| # | Notebook | Original File | Target Dataset | Output Directory | Role |
|---|----------|---------------|----------------|------------------|------|
| 01 | `01_query_and_degrade_hsc.ipynb` | `Reading.ipynb` | `sugohi_lenses_AB_{wide,deep}.fits` | `../data/hsc_query_output/{wide,deep}_degraded` | Query HSC SSP (`pdr3_wide` / `pdr3_dud`) and degrade via `read_degrade_write`. |
| 02 | `02_degrade_final_sample.ipynb` | `Reading2.ipynb` | `../data/final-sample` (Margherita lens sample) | `../data/final-sample-output` | Degrade local 5-band FITS cubes (`imoutf_<coord>.fits`) via `degrade_images`. |
| 03 | `03_degrade_contaminants_50k.ipynb` | `Reading3.ipynb` | `../data/contaminants-sample` (50k contaminants) | `../data/contaminants-sample-output2` | Convert `catalog.csv` to FITS and degrade 50,000 contaminant cubes. |
| 04 | `04_degrade_extra_contaminants.ipynb` | `Reading4.ipynb` | `../data/extra-contaminants` (2k extra contaminants) | `../data/extra-contaminants-output2` | **Latest degradation run.** Degrades extra contaminant cubes; Cell 10 fixes the `extra-contaminants2` path typo to `extra-contaminants`. |
| 05 | `05_display_degraded_images.ipynb` | `Display_Degraded_Images.ipynb` | `../data/final-sample-output` | — | Inspect degraded 5-band FITS cubes, RGB composites, and debug failed galaxies from `degrade.log`. |

## Installation & Reproducibility

> **Important:** Use **Python 3.11** and **`scikit-learn==1.5.2`**. The DP0.2 Gaussian Mixture Model samplers in `HSC_to_LSST/hsc_to_lsst/data/dp0/` are pickled scikit-learn objects that require `scikit-learn==1.5.2` to unpickle cleanly.

### Option A: Conda (recommended)

```bash
conda env create -f environment.yml
conda activate HSC2LSSTLensing
python -m ipykernel install --user --name hsc2lsstlensing --display-name "Python 3 (HSC2LSSTLensing)"
```

### Option B: `venv` + `pip`

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m ipykernel install --user --name hsc2lsstlensing --display-name "Python 3 (HSC2LSSTLensing)"
```

## Expected Data Directory Layout

The notebooks expect a sibling `../data/` directory relative to the repository root:

```text
../data/
├── sugohi_lenses_AB_wide.fits            # Notebook 01
├── sugohi_lenses_AB_deep.fits            # Notebook 01
├── hsc_query_output/                     # Notebook 01 outputs
├── final-sample/                         # Notebook 02 inputs
│   ├── params/*_finalpar.csv
│   └── simct_images/<sample>/imoutf_*.fits
├── final-sample-output/                  # Notebook 02 outputs / Notebook 05 inputs
├── contaminants-sample/                  # Notebook 03 inputs
│   └── contaminants/cont_50k/
├── contaminants-sample-output2/          # Notebook 03 outputs
├── extra-contaminants/                   # Notebook 04 inputs
│   ├── catalog.csv
│   └── cont_*.fits
└── extra-contaminants-output2/           # Notebook 04 outputs
```

## Key Degradation Parameters

All degradation notebooks use the following LSST 1-year coadd configuration:

- `coadd_years = 1` (DP0.2 1-year coadd GMM sampler)
- `hsc_pix_scale = 0.168` arcsec/pix
- `lsst_size_pix = 41` (8.2" × 8.2" at `0.2"`/pix)
- `bands = 'grizy'`
- `zp_rms_frac_thresh = 0.3`
- `zp_max_mag_change = 2.0`

## Attribution & License

This repository vendors `HSC_to_LSST` from `https://github.com/mardom/HSC_to_LSST` (commit `cb71bdf`, forked from `https://github.com/furcelay/HSC_to_LSST`), distributed under the MIT License (see `HSC_to_LSST/LICENSE`).

If you use `HSC_to_LSST` in your research, please cite the LSST SLSC static strong lensing challenge paper:
*(Clecio et al. 2026, in preparation)*
