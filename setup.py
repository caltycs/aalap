#!/usr/bin/env python3
from setuptools import setup, find_packages
from aalap.version import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="aalap-cli",
    version=__version__,
    author="Parijat Bose",
    author_email="info.caltycs@gmail.com",
    description="Interactive CLI for Claude AI with MCP server support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/caltycs/aalap",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "aalap=aalap.__main__:main",
        ],
    },
    include_package_data=True,
)