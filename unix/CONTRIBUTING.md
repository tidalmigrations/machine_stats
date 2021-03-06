# Contributing to _Machine Stats_

Welcome! Happy to see you willing to make the project better.

## We're standing on the shoulders of giants

Under the hood Machine Stats relies on the awesome [Ansible
SDK](https://docs.ansible.com/ansible/latest/dev_guide/index.html).

## Technicalities

Development on the latest version of Python is preferred. As of this writing
it's 3.9.  You can use any operating system.

Install all development dependencies using:

```console
$ pipenv install --dev
```

If you haven't used `pipenv` before but are comfortable with virtualenvs, just
run `pip install pipenv` in the virtualenv you're already using and invoke the
command above from the `unix` directory of the cloned _Machine Stats_ repo. It
will do the correct thing.

Non `pipenv` install works too:

```console
$ pip install -r requirements.txt
$ pip install -r dev-requirements.txt
$ pip install -e .
```

### Tools

We use the following tools:

* `black` for code formatting (`pipenv run black .`)
* `isort` to sort imports (`pipenv run isort .`)
* `flake8` or `pylint` for code linting (`pipenv run flake8
  src/machine_stats/*` or `pipenv run pylint src`)
* `bump2version` for version bumps (`pipenv run bump2version`)

## Finally

Thanks again for your interest in improving the project! You're taking action
when most people decide to sit and watch.
