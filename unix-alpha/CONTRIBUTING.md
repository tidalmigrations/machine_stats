# Contributing to _Machine Stats_

| :exclamation:  Warning: This is not a stable release! The following documention is a work in progress and might not be accurate |
|-------------------------------------------------------------------------------------------------|

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

### How to bump Machine Stats version

We use tags to release a new version of machine stats alpha. To make a new release, simply create a tag on the `alpha` branch and the `pypi-upload-alpha` GitHub Workflow will take care of the rest.

To build a new image, you will need to create a release. The steps are pretty simple, You can find Github's instruction [here](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository#creating-a-release).

* On the repo page, click on release (right side bar).
* Create new release.
* Choose a tag. You should create a new tag for your build. Make sure that you've selected the `alpha` branch as your target branch.
* Publish the release.

### Introducing breaking changes?

When you create a PR, the GitHub workflows check for the linting and CodeQL. However, if you think you're introducing breaking changes, then please add the label `ci` with your PR. This will run the Advanced Prechecks workflow that checks Machine Stats' working in the following system environments:

* Ubuntu 20.04 - Python 3.7 to 3.10
* RHEL 8 - Python 3.6, 3.8 to 3.10

## Finally

Thanks again for your interest in improving the project! You're taking action
when most people decide to sit and watch.
