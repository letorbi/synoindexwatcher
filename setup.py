
import setuptools
import sys

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="synoindexwatcher",
    version="0.11.4",
    author="Torben Haase",
    author_email="git@letorbi.com",
    description="An automated media-index updater for Synology DiskStations based on inotify and synoindex.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/letorbi/synoindexwatcher",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
        "inotifyrecursive>=0.3.5",
        "configparser; python_version < '3.5'"
    ],
    python_requires=">=2.7, !=3.0.*, !=3.1.*"
)
