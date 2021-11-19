from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="machine_stats",
    version="2.1.0",
    author="Petr Razumov",
    author_email="petr.razumov@tidalmigrations.com",
    description="A simple and effective way to gather machine statistics (RAM, Storage, CPU, etc.) from server environment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["machine_stats"],
    package_dir={"": "src"},
    package_data={"": ["modules/*", "plugins/*"]},
    url="https://github.com/tidalmigrations/machine_stats",
    install_requires=[
        "ansible<2.10",
        "pluginbase==1.0.1",
    ],
    entry_points={
        "console_scripts": [
            "machine_stats=machine_stats:main",
            "machine-stats=machine_stats:main",
        ]
    },
)
