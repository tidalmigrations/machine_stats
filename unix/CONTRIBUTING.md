# Contributing to _Machine Stats_

Welcome! Happy to see you willing to make the project better.

## We're standing on the shoulders of giants

Under the hood Machine Stats relies on the awesome [Ansible SDK](https://docs.ansible.com/ansible/latest/dev_guide/index.html).

## Technicalities

Development on the latest version of Python is preferred. As of this writing
it's 3.9.  You can use any operating system.

Install all development dependencies using:

```console
pipenv install --dev
```

If you haven't used `pipenv` before but are comfortable with virtualenvs, just
run `pip install pipenv` in the virtualenv you're already using and invoke the
command above from the `unix` directory of the cloned _Machine Stats_ repo. It
will do the correct thing.

Make changes in the source code (e.g in `src/machine_stats/__init__.py`) and
run `pipenv run machine_stats` to run it locally.

Non `pipenv` install works too:

```console
pip install -r requirements.txt
pip install -r dev-requirements.txt
pip install -e .
```

### Tools

We use the following tools:

* `black` for code formatting (`pipenv run black .`)
* `isort` to sort imports (`pipenv run isort .`)
* `flake8` or `pylint` for code linting (`pipenv run flake8
  src/machine_stats/*` or `pipenv run pylint src`)
* `bump2version` for version bumps (`pipenv run bump2version`)

### Release a new Machine Stats version

To deploy a new version of Machine Stats, you will need to create a release. The steps are pretty simple, You can find Github's instruction [here](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository#creating-a-release).

* On the main repo page, click on [Releases](https://github.com/tidalmigrations/machine_stats/releases) (right side bar)
* Create a new release on the `master` branch.
* Choose a tag. The Tag that you create will be used as the new Tidal Tools version. Please follow this convention
  * Minor/Patch release: `v2.5.6` → `v2.5.7`
  * Major release: `v2.5.10` → `v2.6.0`
  * Version release: `v2.6.7` → `v3.0.0`
* Similarly, you can release a `pre-release` version.
  * Make sure to change the target branch to your dev branch and choose the `Set as a pre-release` option.
* **Note:** [virt-stats](https://pypi.org/project/virt-stats/) also have the same version number as Machine Stats.

### Introducing breaking changes?

When you create a PR, the GitHub workflows check for the linting and CodeQL. However, if you think you're introducing breaking changes, then please add the label `ci` with your PR. This will run the Advanced Prechecks workflow that checks Machine Stats' working in the following system environments:

* Ubuntu 20.04 - Python 3.7 to 3.10
* RHEL 8 - Python 3.6, 3.8 to 3.10

## Finally

Thanks again for your interest in improving the project! You're taking action
when most people decide to sit and watch.
