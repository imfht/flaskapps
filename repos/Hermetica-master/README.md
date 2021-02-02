# Hermetica


[![CircleCI](https://circleci.com/gh/yoshiya0503/Hermetica.svg?style=shield&circle-token=4614abf3b106e5f31f9726ebaedfcebc5c7fa859)](https://circleci.com/gh/yoshiya0503/Hermetica)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](CONTRIBUTING.md#pull-requests)
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

---

THIS IS NOT WEB FRAMEWORK TO REPLACE FLASK.

Hermetica is scaffold tools, and wiki to implement better flask applications.

When we try to build web applications by using flask web framework, there are to many patterns and practices.
This diversity make it difficult to implement apps that have simple architecture.
In other words, because of too many manners, options, and patters, to implement more bigger applications is not so easy.
(but, to implement small app by using flask is extreamly easy)

Therefor, we try to implement the scaffold tools head for better architecture applications as mach as possible
based on our many experiences.

* better and common directory structure
* scaffold to create tipycal API, model.
* select powerful packages(like SQLAlchemy Nose)

# Installation

We dare to support only python 3.x, because python 2.x will eventually deprecated almost all systems, and we have to get used to python 3.x quickly.

```
pip install hermetica
```

# Usage

### Overview the usage

hermetica has some subcommands, to create scaffold api, decorator, model.

* api (url and routing method base or class base or flask-restful)
* model (database models, sqlalchemy or mongoengine)
* decorator (you can insert some code before enter the api, like a 'authentication')

```
→ hermetica --help
Usage: hermetica [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  api        create api
  decorator  create decorator
  init       initialize your flask app
  model      create model
```

### initialize your flask project.

```
→ hermetica init --help
Usage: hermetica init [OPTIONS]

  initialize your flask app

Options:
  --api [restful|decorator|class]
                                  Flask-Restful or Flask decorator or
                                  methodview
  --db [sqlalchemy|mongoengine]   SQLAlchemy or Mongoengine or None
  --decorator                     create decorator or None
  --redis                         using Redis or None
  --docker                        using container
  --help                          Show this message and exit.
```

After create project scaffold, you will check `Pipfile` contents, if there are shortages in list of packages, you can
add other packages into `Pipfile`, and lock your package.
(We recommend you to use `pipenv` https://github.com/pypa/pipenv)

Hermetica support docker. you can see `Dockerfile` and `docker-compose.yml` at your root of project.
We recommend you to use docker-compose, it will helpful to separate from other projects.

```
pipenv lock

# if you set docker option, you can up the app container
docker-compose build
docker-compose up
```

### add api to your flask project.

```
→ hermetica api --help
Usage: hermetica api [OPTIONS] NAME

  create api

Options:
  --api [restful|decorator|class]
                                  Flask-Restful or Flask decorator or
                                  methodview
  --version TEXT                  API version
  --help                          Show this message and exit.
```

### add model to your flask project.

```
→ hermetica model --help
Usage: hermetica model [OPTIONS] NAME

  create model

Options:
  --db [sqlalchemy|mongoengine]  SQLAlchemy or Mongoengine or None
  --help                         Show this message and exit.
```

### add decorator to your flask project.

```
→ hermetica decorator --help
Usage: hermetica decorator [OPTIONS] NAME

  create decorator

Options:
  --help  Show this message and exit.
```

# Development

This repos is too young, so we provide few useful features yet.
we will grad if you send PRs...

# See Before Wiki (Flask Best Practices)

Why we apply broken change? Because, before repo source code is slightly trivial,
and we believe this change will not cause any negative impact to others.

To create scaffold tools for flask will cause good affect the world rather than remain trivial code.
But there are no warries. Flask-best-Practices contents (wiki docs) remain here (but only for japanese).

https://github.com/yoshiya0503/Hermetica/wiki
