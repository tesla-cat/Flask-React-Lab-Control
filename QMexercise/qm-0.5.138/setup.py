import setuptools
import os

with open("VERSION", "r") as f:
    version = f.readline()

if len(version) < 1:
    raise Exception("No version specified")

print("Building version {}".format(version))

setuptools.setup(
    name='qm',
    version=version,
    scripts=[],
    author="Tal Shani",
    author_email="tal@quantum-machines.co",
    description="Control QM controller and machines",
    url="https://quantum-machines.co",
    packages=["qm", "qm.qua", "qm.program", "qm.pb", "qm.results"],
    data_files=["VERSION"],
    install_requires=[
        'grpcio>=1.26.0,<2',
        'protobuf>=3.7.1,<4',
        'marshmallow>=3.0.0,<4',
        'marshmallow-polyfield>=5.7,<6',
        'numpy>=1.17.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
