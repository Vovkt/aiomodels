#!/usr/bin/env python3
from setuptools import find_packages, setup


NAME = "aiomodels"

DEPENDENCIES = [
    "motor==2.5.1",
]

EXTRAS_PYDANTIC = ["pydantic==1.8.2"]

EXTRAS_DEV = [
    "black==21.10b0",
    "mypy==0.910",
    "coverage",
]


setup(
    name=NAME,
    version="0.0.1a",
    url="https://github.com/Vovkt/aiomodels",
    description="Mongo async models",
    maintainer="Vladimir Doroshenko",
    maintainer_email="vovktt@gmail.com",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    zip_safe=True,
    install_requires=DEPENDENCIES,
    extras_require={
        "pydantic": EXTRAS_PYDANTIC,
        "dev": (EXTRAS_PYDANTIC + EXTRAS_DEV),
    },
    classifiers=[
        "Programming Language :: Python :: 3.8",
    ],
)
