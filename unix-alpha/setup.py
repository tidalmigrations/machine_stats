from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="machine_stats_alpha",
    version="1.0.0",
    author="Tidal Migrations",
    author_email="support@tidalmigrations.com",
    description="A simple and effective way to gather machine statistics (RAM, Storage, CPU, etc.) from server environment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["machine_stats"],
    package_dir={"": "src"},
    package_data={"": ["modules/*", "plugins/*"]},
    url="https://github.com/tidalmigrations/machine_stats",
    install_requires=[
        "ansible==5.5.0",
        "pluginbase==1.0.1",
    ],
    entry_points={
        "console_scripts": [
            "machine_stats_alpha=machine_stats:main",
            "machine-stats-alpha=machine_stats:main",
        ]
    },
)
