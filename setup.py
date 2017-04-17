import sys
from setuptools import setup

install_requires = [
    'distance', 'pymonad'
]

if sys.version < '3.0':
    install_requires.append('mock')

setup(name='hew',
      version='0.1',
      description='Data mining tools',
      url='https://github.com/JeffreyMFarley/hew',
      author='Jeffrey M Farley',
      author_email='JeffreyMFarley@users.noreply.github.com',
      packages=['hew', 'hew.classifiers', 'hew.clusters', 'hew.structures'],
      include_package_data=True,
      install_requires=install_requires,
      test_suite='tests',
      zip_safe=False)
