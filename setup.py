from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

INSTALL_REQUIRES = [
      'google-api-core>=1.26.3',
      'google-cloud-storage>=1.37.1',
      'google-cloud-automl>=2.3.0',
      'google-cloud-bigquery>=2.14.0'
]

setup(
    name='txpy-gchelper',
    version='0.0.12',
    description='A wrapper around the Google Cloud SDK for Python',
    long_description=readme,
    long_description_content_type='text/x-rst',
    author='Philippe Huet',
    author_email='philhu@tyxio.com',
    url='https://github.com/tyxio/txpy-gchelper',
    license='MIT License',
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(exclude=('tests', 'docs')),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independant"
        ]
)