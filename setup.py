import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lofargeotiff",
    version="0.1",
    author="Tammo Jan Dijkema",
    author_email="dijkema@astron.nl",
    description="Write LOFAR near field images as GeoTIFF",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tammojan/lofargeotiff",
    packages=setuptools.find_packages(),
    install_requires=[
        "lofarantpos",
        "rasterio",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)
