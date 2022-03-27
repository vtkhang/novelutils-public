#!/usr/bin/env python
"""The setup and build script for getnovel."""
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    setup(
        name="novelutils",
        version="1.2.1",
        author="Vũ Thừa Khang",
        author_email="vuthuakhangit@gmail.com",
        description="Tool based on Scrapy framework to get novel from web site.",
        long_description=fh.read(),
        long_description_content_type="text/markdown",
        url="https://github.com/vtkhang/novelutils",
        project_urls={
            "Bug Tracker": "https://github.com/vtkhang/novelutils/issues",
        },
        license="BSD",
        packages=["novelutils"],
        classifiers=[
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "License :: OSI Approved :: BSD License",
            "Operating System :: OS Independent",
        ],
        include_package_data=True,
        python_requires=">=3.7",
        install_requires=[
            "scrapy == 2.5.1",
            "beautifulsoup4 >= 4.10.0",
            "pillow >= 9.0.1",
            "importlib-resources >= 5.4.0",
            "importlib-metadata >= 4.11.3",
            "tldextract >= 3.2.0",
            "validators >= 0.18.2"
        ],
        extras_require={
            "dev": [
                "black >= 22.1.0",
                "ipython >= 7.32.0",
                "pylint >= 2.12.2"
            ],
            "build": ["build >= 0.7.0"],
        },
        entry_points={
            "console_scripts": ["novelutils = novelutils:run_main"],
        },
    )
