from setuptools import setup

setup(name='kitefeaturebarcoding',
      version='0.1',
      description='Fast and accurate quantification of single-cell Feature Barcoding experiments. This package prepares mismatch fasta and mismatch t2g files from a Python dictionary of Feature Barcode name and sequence key-value pairs.'
      url='http://github.com/pachterlab/kite',
      author='Eduardo da Veiga Beltrame, Jase Gehring',
      author_email='beltrame@caltech.edu, jgehring@caltech.edu',
      license='BSD-2',
      packages=['kite'],
      zip_safe=False)
