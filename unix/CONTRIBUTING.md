# Contributing to _Machine Stats_

Welcome! Happy to see you willing to make the project better.

## We're standing on the shoulders of giants

Under the hood Machine Stats relies on the awesome [Ansible SDK](https://docs.ansible.com/ansible/latest/dev_guide/index.html).

## Technicalities

Development on the latest version of Python is preferred. As of this
writing it's 3.14.  You can use any operating system. We use the
wonder [uv tool](https://docs.astral.sh/uv/) for a modern take on
python package management. If you don't have it installed follow the
appropriate instructions for your OS/package manager of choice.

Install all development dependencies using:

```console
uv sync
```

### Tools

We use the following tools:

* uv for modern python project management
* `black` for code formatting (`uv run black .`)
* `isort` to sort imports (`uv run isort .`)
* `flake8` or `pylint` for code linting (`uv run flake8
  src/machine_stats/*` or `uv run pylint src`)

### Testing

We use `pytest` for testing. Test files are located in the `tests/` directory and should be named with a `test_` prefix (e.g., `test_my_feature.py`).

To run the tests, use the following command:

```console
pytest
```

or

```console
uv run pytest
```

### How to release a new Machine Stats version

To deploy a new version of Machine Stats, you will need to create a release. The steps are pretty simple, You can find Github's instruction [here](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository#creating-a-release).

* On the main repo page, click on [Releases](https://github.com/tidalmigrations/machine_stats/releases) (right side bar)
* Create a new release on the `master` branch.
* Choose a tag. The Tag that you create will be used as the new Tidal Tools version. Please follow this convention
  * Minor/Patch release: `v2.5.6` → `v2.5.7`
  * Major release: `v2.5.10` → `v2.6.0`
  * Version release: `v2.6.7` → `v3.0.0`
* **Note:** [virt-stats](https://pypi.org/project/virt-stats/) also have the same version number as Machine Stats.

### Introducing breaking changes?

When you create a PR, the GitHub workflows check for the linting and CodeQL. However, if you think you're introducing breaking changes, then please add the label `ci` with your PR. This will run the Advanced Prechecks workflow that checks Machine Stats' working in the following system environments:

* Ubuntu 24.04 - Python 3.7 to 3.10
* RHEL 8 - Python 3.6, 3.8 to 3.10

## Finally

Thanks again for your interest in improving the project! You're taking action
when most people decide to sit and watch.
