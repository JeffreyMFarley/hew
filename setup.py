from setuptools import setup

setup(name='hew',
      version='0.1',
      description='Data mining tools',
      url='https://github.com/JeffreyMFarley/hew',
      author='Jeffrey M Farley',
      author_email='JeffreyMFarley@users.noreply.github.com',
      packages=['hew'],
      install_requires=[
          'distance', 'pymonad'
      ],
      test_suite='tests',
      zip_safe=False)
