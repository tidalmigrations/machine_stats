from distutils.core import setup
import re


def read_version():
    """Read the version string from the _version.py file and validate its format.
    The version string must follow semantic versioning (x.y.z).
    Returns:
        str: The version string.
    Raises:
        ValueError: If the version string is not found or is not in the correct format.
    """
    with open("src/machine_stats/_version.py") as handle:
        version_string = handle.read()

        if "=" not in version_string:
            raise ValueError(
                "Version string is not in the correct format in _version.py"
            )

        version = version_string.split("=")[1].strip().strip('"')

        if not version:
            raise ValueError("Version string is empty in _version.py")

        semver_regex = r"^v\d+\.\d+\.\d+$"
        if not re.match(semver_regex, version):
            raise ValueError(
                "Version string is not in semantic versioning format x.y.z in _version.py"
            )
        return version


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="machine_stats",
    version=read_version(),
    author="Tidal SW",
    author_email="support@tidalcloud.com",
    description="A simple and effective way to gather machine statistics (RAM, Storage, CPU, etc.) from server environment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["machine_stats"],
    package_dir={"": "src"},
    package_data={"": ["modules/*", "plugins/*"]},
    exclude_package_data={"": ["tests/*"]},
    url="https://github.com/tidalmigrations/machine_stats",
    install_requires=[
        "ansible-runner==2.4.2",
        "pluginbase==1.0.1",
    ],
    entry_points={
        "console_scripts": [
            "machine_stats=machine_stats:main",
            "machine-stats=machine_stats:main",
        ]
    },
    python_requires=">=3.10,<=3.14",
    classifiers=[
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: System :: Systems Administration",
        "Topic :: System :: Monitoring",
    ],
)
