from setuptools import setup, find_packages


def read_requirements():
    """Read the requirements.txt file and return a list of dependencies."""
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return fh.read().splitlines()


# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="MolNexTR",
    version="1.0",
    description="MolNexTR, a novel graph generation model. The model follows the encoder-decoder architecture, takes three-channel molecular images as input, outputs molecular graph structure prediction, and can be easily converted to SMILES.",
    long_description=long_description,
    license="Apache License 2.0",
    python_requires=">=3.10, <3.12",
    classifiers=[
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    url="",
    packages=find_packages(),
    package_dir={'MolNexTR': 'MolNexTR'},
    install_requires=read_requirements(),
)
