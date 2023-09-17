from setuptools import setup, find_packages
import sys


requires = [
    "requests",
    "openpower",
    "sentry-sdk",
    "sqlalchemy",
    "mariadb",
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
