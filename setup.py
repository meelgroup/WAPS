from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
  name = 'waps',
  packages = ['waps'],
  version = 'v1.0.2',
  license='MIT',
  description = 'This library can be used to sample satisfying assignments for a CNF/DNF obeying a given literal-weighted weight function and projected upon a given sampling set.',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author = 'Rahul Gupta',
  author_email = 'rahujupiter@gmail.com',
  url = 'https://github.com/meelgroup/waps/',
  download_url = 'https://github.com/meelgroup/waps/archive/v1.0.2.tar.gz',
  keywords = ['sampling', 'cnf', 'weighted sampling', 'projected sampling', 'dDNNF'],   # Keywords that define your package best
  install_requires=[
          'numpy',
          'pydot',
          'gmpy2',
          'pyparsing'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7'
  ],
)
