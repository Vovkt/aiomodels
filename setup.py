#!/usr/bin/env python3
from setuptools import find_packages, setup


NAME = "aiomodel"

DEPENDENCIES = [
    "motor==2.5.1",
]

EXTRAS_DEV = [
    "black==21.10b0",
    "mypy==0.910",
]


setup(
    name=NAME,
    version="0.0.1",
    url="https://github.com/Vovkt/aiomodel",
    description="Mongo async models",
    maintainer="Vladimir Doroshenko",
    maintainer_email="vovktt@gmail.com",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    zip_safe=True,
    install_requires=DEPENDENCIES,
    extras_require={
        "dev": EXTRAS_DEV,
    },
    classifiers=[
        "Programming Language :: Python :: 3.8",
    ],
)