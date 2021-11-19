from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="virt_stats",
    version="2.1.0",
    author="Petr Razumov",
    author_email="petr.razumov@tidalmigrations.com",
    description="A simple and effective way to gather machine statistics (RAM, Storage, CPU, etc.) from virtual environment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["virt_stats"],
    package_dir={"": "src"},
    url="https://github.com/tidalmigrations/machine_stats",
    install_requires=[
        "libvirt-python==7.3.0",
    ],
    entry_points={
        "console_scripts": [
            "virt_stats=virt_stats:main",
            "virt-stats=virt_stats:main",
        ]
    },
)
