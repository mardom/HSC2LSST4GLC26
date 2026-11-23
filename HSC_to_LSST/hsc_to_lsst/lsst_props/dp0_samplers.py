import pickle
from pathlib import Path
import warnings
import numpy as np

data_path = Path(__file__).resolve().parents[1]
data_path = data_path.joinpath('data', 'dp0')


class BandSampler:
    """This class samples LSST band properties from a Gaussian Mixture Model (GMM) sampler for a given band.
    The GMM sampler was trained on DP0 data and pickled. Currently, there is a single visit and N-year coadd version.
    The N-year coadd is scaled from the 1-year coadd GMM.
    """

    full_labels = ['median', 'rms', 'seeing', 'exp_time', 'zero_point']

    def __init__(self, gmm_sampler, gmm_labels, constants=None, time_scale=1.0):
        self.gmm_sampler = gmm_sampler
        self.gmm_labels = gmm_labels
        if constants is None:
            constants = {}
        self.constants = constants
        assert set(gmm_labels) | set(constants.keys()) == set(self.full_labels)
        self.time_scale = time_scale

    def sample(self):
        """Sample band properties from the GMM sampler and apply necessary scaling.
        :return: dict of sampled band properties
        """
        samples = self.gmm_sampler.sample()[0][0]
        samples = {label: samples[i] for i, label in enumerate(self.gmm_labels)}
        samples.update({k: v for k, v in self.constants.items() if k not in samples})
        samples['rms'] = np.maximum(samples['rms'], 1e-6)
        # scale properties with time in years
        samples['exp_time'] *= self.time_scale
        samples['rms'] /= np.sqrt(self.time_scale)
        return samples


def dp0_gmm_sampler(dp0_coadd="1"):
    """Load the DP0 GMM samplers for LSST band properties based on the coadd type.

    :param dp0_coadd: str with 'single_visit' or number of years for coadd
    :return: dict of BandSampler objects for each band
    """
    if dp0_coadd == "single_visit":
        # the exp_time is fixed at 30s for single visit, but the zero_point varies
        gmm_labels = ['median', 'rms', 'seeing', 'zero_point']
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            gmm_sampler = pickle.load(open(data_path.joinpath('dp0_gmm_sampler_single_visit.pkl'), 'rb'))
        return {band: BandSampler(gmm_sampler[band], gmm_labels, {'exp_time': 30.0})
                for band in 'grizy'}
    # the dp0_coadd is and int number of years
    elif dp0_coadd.isdigit():
        n_years = int(dp0_coadd)
        # the exp_time scales linearly with number of years, the zero_point is fixed at 27.0 for all coadds
        gmm_labels = ['median', 'rms', 'seeing', 'exp_time']
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            gmm_sampler_1y = pickle.load(open(data_path.joinpath('dp0_gmm_sampler_1yr_coadd.pkl'), 'rb'))
        # zero_point is fixed at 27.0 for all coadds
        return {band: BandSampler(gmm_sampler_1y[band], gmm_labels, {'zero_point': 27.0}, time_scale=n_years)
                for band in 'grizy'}
    else:
        raise ValueError("dp0_coadd must be '1' or 'single_visit'")
