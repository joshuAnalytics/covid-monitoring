import os
from setuptools import Command, find_packages, setup


def clean_requirements_list(input_list):
    reqs = [v.split("#")[0].strip() for v in input_list]
    return [v for v in reqs if len(v) > 0 and not v.startswith("-")]


class Cleaner(Command):
    def run(self):
        os.system("rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info")


with open("README.md") as f:
    readme = f.read()

with open("requirements.txt") as f:
    requirements = f.readlines()

requirements = clean_requirements_list(requirements)

setup(
    name="covid_monitoring",
    version="0.0.1",
    description="a library for retrieving and plotting covid data",
    long_description=readme,
    author="joshuAnalytics",
    packages=find_packages(include=["covid_monitoring"]),
    python_requires=">=3.7",
    install_requires=requirements,
    classifiers=[
        "Intended Audience :: mateys",
        "Language :: English",
        "Programming Language :: Python :: 3",
    ],
    cmdclass={"clean": Cleaner},
    entry_points={"console_scripts": ["covid_monitoring=covid_monitoring.cli:cli"]},
)
