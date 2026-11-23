__author__ = "furcelay"

from hsc_to_lsst.hsc_query import downloadCutout, downloadPsf
from astropy.io import fits
import tarfile
import io
import os


def query_hsc(
        ra,
        dec,
        semaphore,
        username=None,
        password=None,
        timeout=60,  # seconds
        size=20,  # arcsec
        field="pdr3_wide",
        verbose=False
):
    """
    Query HSC cutout and PSF data.

    :param ra: Right Ascension in degrees
    :param dec: Declination in degrees
    :param semaphore: multiprocessing.BoundedSemaphore for limiting concurrent requests
    :param username: HSC SSP CAS username (if None, read from environment variable HSC_SSP_CAS_USERNAME)
    :param password: HSC SSP CAS password (if None, read from environment variable HSC_SSP_CAS_PASSWORD)
    :param timeout: Timeout for the query in seconds
    :param size: Size of the cutout in arcseconds
    :param field: HSC data release field (e.g., "pdr3_wide", "pdr3_dud_rev", etc.)
    :param verbose: If True, print verbose output
    :return: dict
        Dictionary with keys 'g', 'r', 'i', 'z', 'y' containing dictionaries with keys 'image', 'metadata', and 'psf'.
        'image' and 'psf' are 2D numpy arrays representing the image data.
    """
    if username is None:
        username = os.environ.get('HSC_SSP_CAS_USERNAME')
    if password is None:
        password = os.environ.get('HSC_SSP_CAS_PASSWORD')

    rect = downloadCutout.Rect.create(
        ra=str(ra),
        dec=str(dec),
        sw=f"{size/2}arcsec",
        sh=f"{size/2}arcsec",
        filter="all",
        rerun=field
    )
    psf_req = downloadPsf.PsfRequest.create(
        ra=str(ra),
        dec=str(dec),
        filter="all",
        rerun=field,
    )
    image_list = downloadCutout.download(rect, user=username, password=password, semaphore=semaphore, timeout=timeout)
    try:
        psf_list = downloadPsf.download(psf_req, user=username, password=password, semaphore=semaphore, timeout=timeout)
    except (OSError and tarfile.ReadError) as e:
        if verbose:
            print(f"Error querying HSC PSF: {type(e)} {e}")
        psf_list = []

    output_data = {}
    for band in 'grizy':
        band_data = {}
        for metadata, data in image_list:
            if metadata['filter'] == f"HSC-{band.upper()}":
                band_data['image'], band_data['hdr'] = fits.getdata(io.BytesIO(data), header=True)
                band_data['metadata'] = metadata
                break
        for psf_metadata, psf_data in psf_list:
            if psf_metadata['filter'] == f"HSC-{band.upper()}":
                psf = fits.getdata(io.BytesIO(psf_data))
                band_data['psf'] = psf
                break
        output_data[band] = band_data
    return output_data


def query_hsc_binary(
        ra,
        dec,
        semaphore,
        username=None,
        password=None,
        timeout=60,  # seconds
        size=20,  # arcsec
        field="pdr3_wide",
        verbose=False
):
    """
    Query HSC cutout and PSF data as binary files.

    :param ra: Right Ascension in degrees
    :param dec: Declination in degrees
    :param semaphore: multiprocessing.BoundedSemaphore for limiting concurrent requests
    :param username: HSC SSP CAS username (if None, read from environment variable HSC_SSP_CAS_USERNAME)
    :param password: HSC SSP CAS password (if None, read from environment variable HSC_SSP_CAS_PASSWORD)
    :param timeout: Timeout for the query in seconds
    :param size: Size of the cutout in arcseconds
    :param field: HSC data release field (e.g., "pdr3_wide", "pdr3_dud_rev", etc.)
    :param verbose: If True, print verbose output
    :return: dict
        Dictionary with keys 'g', 'r', 'i', 'z', 'y' containing dictionaries with keys 'image', 'metadata', and 'psf'.
        'image' and 'psf' are binary data representing a fits file.
    """
    if username is None:
        username = os.environ.get('HSC_SSP_CAS_USERNAME')
    if password is None:
        password = os.environ.get('HSC_SSP_CAS_PASSWORD')

    rect = downloadCutout.Rect.create(
        ra=str(ra),
        dec=str(dec),
        sw=f"{size / 2}arcsec",
        sh=f"{size / 2}arcsec",
        filter="all",
        rerun=field
    )
    psf_req = downloadPsf.PsfRequest.create(
        ra=str(ra),
        dec=str(dec),
        filter="all",
        rerun=field,
    )
    image_list = downloadCutout.download(rect, user=username, password=password, semaphore=semaphore, timeout=timeout)
    try:
        psf_list = downloadPsf.download(psf_req, user=username, password=password, semaphore=semaphore, timeout=timeout)
    except (OSError and tarfile.ReadError) as e:
        if verbose:
            print(f"Error querying HSC PSF: {type(e)} {e}")
        psf_list = []

    output_data = {}
    for band in 'grizy':
        band_data = {}
        for metadata, data in image_list:
            if metadata['filter'] == f"HSC-{band.upper()}":
                band_data['image'] = data
                band_data['metadata'] = metadata
                break
        for psf_metadata, psf_data in psf_list:
            if psf_metadata['filter'] == f"HSC-{band.upper()}":
                band_data['psf'] = psf_data
                break
        output_data[band] = band_data
    return output_data