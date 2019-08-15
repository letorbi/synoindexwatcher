
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="synoindexwatcher",
    version="0.3.0",
    author="Torben Haase",
    author_email="torben@pixelsvsbytes.com",
    description="A media index watcher for Synology DiskStations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/letorbi/synoindexwatcher",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
    ],
)
