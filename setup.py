from setuptools import setup, find_packages

setup(
    name="dirscan",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "dirscan=dirscan.cli:main"
        ]
    },
)
