import os
from setuptools import setup, find_packages

VERSION = os.environ.get("PACKAGE_VERSION","0.0.0")

setup(
    name="circleci-trigger",
    version=VERSION,
    packages=find_packages(),
    install_requires=["requests","pyyaml"],
    entry_points={"console_scripts": ["circleci-trigger=circleci_trigger.cli:main"]},
)
