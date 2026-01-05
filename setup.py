from setuptools import setup, find_packages

setup(
    name="tscodescan",
    version="0.2.0",
    description="AI-friendly directory and code scanner with tree-first output",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="toolartS",
    url="https://github.com/toolartS/tscodescan",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "tscodescan=dirscan.cli:main"
        ]
    },
    python_requires=">=3.8",
)
