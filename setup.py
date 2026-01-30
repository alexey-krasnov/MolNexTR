import setuptools

def read_requirements():
    """Read the requirements.txt file and return a list of dependencies."""
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return fh.read().splitlines()

setuptools.setup(
    name="molnextr",
    version="1.0.2",
    description="molnextr, a novel graph generation model",
    entry_points={
        "console_scripts": ["molnextr = molnextr.molnextr:main"],
    },
    url="https://github.com/CYF2000127/MolNexTR",
    packages=setuptools.find_packages(),
    license="Apache License 2.0",
    install_requires=read_requirements(),
    package_data={"molnextr": ["decoding/*.*", "indigo/*.*", "models/*.*","vocab/*.*"]},
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: Apache License 2.0",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)