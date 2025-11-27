from setuptools import setup, find_packages
setup(
    name="circleci-trigger",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["requests"],
    entry_points={"console_scripts": ["circleci-trigger=circleci_trigger.cli:main"]},
)
