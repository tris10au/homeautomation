from setuptools import setup, find_packages
import sys


requires = [
    "requests==2.31.0",
    "openpower==0.1.3",
    "sentry-sdk==1.38.0",
    "sqlalchemy==2.0.24",
    "mariadb==1.1.8",
]

setup(
    name="homeautomation",
    version='0.1.0',
    url='https://github.com/tris10au/home-automation',
    license="MIT",
    author="tris10au",
    description="A very basic controller for managing solar usage",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
)
