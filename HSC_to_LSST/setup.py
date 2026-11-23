from setuptools import setup, find_packages


setup(
    name='hsc_to_lsst',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'astropy',
        'photutils',
        'reproject',
        'lenstronomy',
        'scipy',
        'scikit-learn==1.5.2',
        'tqdm'
    ],
    scripts=[
        'bin/query_degrade_hsc',
        'bin/query_hsc',
        'bin/read_degrade_hsc',
        'bin/hsc_query_example'
    ],
    include_package_data=True,
    author='Felipe Urcelay, LSST Strong Lensing Science Collaboration',
)
