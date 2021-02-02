<h1 align="center">🟡 NOTICE 🟡</h1>

<h1 align="center">👉 Bento development is migrating to <a href="https://github.com/returntocorp/semgrep">Semgrep</a> 👈</h1>

---

<p align="center">
    <img src="https://raw.githubusercontent.com/returntocorp/bento/master/bento-logo.png" height="100" alt="Bento logo"/>
</p>
<h3 align="center">
  Find Python web-app bugs delightfully fast, without changing your workflow
</h3>

<p align="center">
  <a href="#installation">Installation</a>
  <span> · </span>
  <a href="#motivations">Motivations</a>
  <span> · </span>
  <a href="#code-checks">Code Checks</a>
  <span> · </span>
  <a href="#usage">Usage</a>
  <br/>
  <a href="#workflows">Workflows</a>
  <span> · </span>
  <a href="#running-in-cicd">Integrations</a>
  <span> · </span>
  <a href="#help-and-community">Help & Community</a>
</p>

<p align="center">
  <a href="https://pypi.org/project/bento-cli/">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/bento-cli?style=flat-square&color=blue">
  </a>
  <a href="https://pypi.org/project/bento-cli/">
    <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/bento-cli?style=flat-square&color=green">
  </a>
  <a href="https://github.com/returntocorp/bento/issues/new/choose">
    <img src="https://img.shields.io/badge/issues-welcome-green?style=flat-square" alt="Issues welcome!" />
  </a>
  <a href="https://twitter.com/intent/follow?screen_name=r2cdev">
    <img src="https://img.shields.io/twitter/follow/r2cdev?label=Follow%20r2cdev&style=social&color=blue" alt="Follow @r2cdev" />
  </a>
</p>

Inspired by tools like the ESLint plugin for React, Bento was created for Flask and Django. With Bento you’ll:

- **Find bugs that matter.** Checks find security and reliability bugs in your code. They’re vetted across thousands of open source projects and never nit your style.
- **Upgrade your tooling.** You don’t have to fix existing bugs to adopt Bento. It’s diff-centric, finding new bugs introduced by your changes. And there’s zero config.
- **Go delightfully fast.** Run Bento automatically locally or in CI. Either way, it runs offline and never sends your code anywhere.

<p align="center">
    <img src="https://web-assets.r2c.dev/bento-demo.gif" width="100%" alt="Demonstrating Bento running in a terminal"/>
</p>

## Installation

Bento is free and requires [Python 3.6+](https://www.python.org/downloads/) and [Docker 19.03+](https://docs.docker.com/get-docker/). It runs on macOS and Linux.

In a Git project directory:

```bash
$ pip3 install bento-cli && bento init
```

Go forth and write great code!

## Motivations

> See our [Bento introductory blog post](https://bento.dev/blog/2019/our-quest-to-make-world-class-security-and-bugfinding-available-to-all-developers/) to learn the full story.

Bento is part of a quest to make world-class security and bugfinding available to all developers, for free. We’ve learned that most developers have never heard of—let alone tried—tools that find deep flaws in code: like Codenomicon, which found [Heartbleed](http://heartbleed.com/), or Zoncolan at Facebook, which finds more [top-severity security issues](https://cacm.acm.org/magazines/2019/8/238344-scaling-static-analyses-at-facebook/fulltext) than any human effort. These tools find severe issues and also save tons of time, identifying [hundreds of thousands of issues](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/43322.pdf) before humans can. Bento is a step towards universal access to tools like these.

We’re also big proponents of opinionated tools like [Black](https://github.com/psf/black) and [Prettier](https://github.com/prettier/prettier). This has two implications: Bento ignores style-related issues and the bikeshedding that comes with them, and it ships with a curated set of checks that we believe are high signal and bug-worthy. See [Three things your linter shouldn’t tell you](https://bento.dev/blog/2019/three-things-your-linter-shouldnt-tell-you/) for more about our decision making process.

## Code Checks

Bento’s check focus on security and reliability bugs in Flask and Django projects.

|                              |                                      |                                                      |
| ---------------------------- | ------------------------------------ | ---------------------------------------------------- |
| **Flask**                    | **Jinja**                            | **Django**                                           |
| missing JWT token            | href template variable               | _coming soon_                                        |
| secure set cookie            | missing noopener                     |                                                      |
| send file open               | missing noreferrer                   | **Docker**                                           |
| unescaped file extension     | missing csrf protection              | [Hadolint](https://github.com/hadolint/hadolint)     |
| use blueprint for modularity | missing doctype                      |                                                      |
| use jsonify                  | meta charset                         | **Shell**                                            |
| avoid hardcoded config       | meta content-type                    | [ShellCheck](https://github.com/koalaman/shellcheck) |
|                              | unquoted attribute template variable |
| **Requests**                 |                                      |
| no auth over http            | **SQLAlchemy**                       |                                                      |
| use scheme                   | _coming soon_                        |                                                      |
| use timeout                  |                                      |

See the full list of [Bento’s specialty checks](https://bento.dev/checks/).

## Usage

Out-of-the-box, Bento is configured for your personal use. See [Team Use](#team-use) to setup Bento for all contributors.

### Upgrading

```bash
$ pip3 install --upgrade bento-cli
```

### Command Line Options

```
$ bento --help
Usage: bento [OPTIONS] COMMAND [ARGS]...

Options:
  -h, --help    Show this message and exit.
  --version     Show the version and exit.
  --agree       Automatically agree to terms of service.
  --email TEXT  Email address to use while running this command without global
                configs e.g. in CI

Commands:
  archive  Suppress current findings.
  check    Checks for new findings.
  disable  Turn OFF a Bento feature for this project.
  enable   Turn ON a Bento feature for this project.
  init     Autodetects and installs tools.

  To get help for a specific command, run `bento COMMAND --help`
```

### Exit Codes

`bento check` may exit with the following exit codes:

- `0`: Bento ran successfully and found no errors
- `2`: Bento ran successfully and found issues in your code
- `3`: Bento or one of its underlying tools failed to run

## Workflows

### Individual Use

Bento understands the importance of getting out of the way so you can write your code. It runs at commit-time on your diffs and only affects you; it won’t change anything for other project contributors or modify Git state.

Initialization enables `autorun` behind the scenes. By default `autorun` blocks the commit if Bento returns findings. To make it non-blocking:

```bash
$ bento enable autorun --no-block
```

You can always manually run Bento on staged files or directories via:

```bash
$ bento check [PATHS]
```

This will show only new findings introduced by these files AND that are not in the archive (`.bento/archive.json`). Use `--all` to check all Git tracked files, not just those that are staged:

```bash
$ bento check --all [PATHS]
```

This feature makes use of Git hooks. If the Bento hook incorrectly blocks your commit, you can skip it by passing the `--no-verify` flag to Git at commit-time (please use this sparingly since all hooks will be skipped):

```bash
$ git commit --no-verify
```

### Team Use

#### Running Locally

To setup Bento for all project contributors, add Bento’s configuration to Git (it’s ignored by default):

```bash
$ cd <PROJECT DIRECTORY>
# Add Bento's cache to the project's .gitignore
$ echo ".bento/cache" >> .gitignore
# Commit Bento's config to your project
$ git add --force .bento .bentoignore
```

Contributors can run Bento for themselves using the project’s configuration via:

```bash
$ bento init
```

#### Running in CI/CD

Bento has first-class support for checking pull requests with GitHub Actions.
Such checks will report only on the bugs introduced by the changes in the pull request.

To get started, just run `bento enable ci` in your project directory.
This will add a CI configuration file to your repository.

#### Advanced CI/CD configuration

You can also configure Bento in CI to analyze your entire project,
instead of only the changes from a pull request.
So that you don’t have to fix all existing issues before making Bento blocking,
its `archive` feature allows historical issues to be tracked and ignored during CI.

To use the `archive` feature so Bento returns a non-zero exit code only for new issues, rather than all existing issues, first create the archive:

```bash
$ cd <PROJECT DIRECTORY>
$ bento archive .
```

Commit Bento’s configuration to the project:

```bash
# Add Bento's cache to the project's .gitignore
$ echo ".bento/cache" >> .gitignore
# Commit Bento's config to your project
$ git add --force .bento .bentoignore
```

You can then add Bento to your CI scripts:

```bash
$ pip3 install bento-cli && bento --version
$ bento --agree --email=<YOUR_EMAIL> check --all 2>&1 | cat
```

We pipe through `cat` to disable Bento's interactive tty features (e.g. progress bars, using a pager for many findings).

If you use CircleCI, the above commands become:

```yaml
version: 2.1

jobs:
  bentoCheck:
  executor: circleci/python:3.7.4-stretch-node
  steps:
    - checkout
    - run:
        name: "Install Bento"
        command: pip3 install bento-cli && bento --version
    - run:
        name: "Run Bento check"
        command: bento --agree --email=<YOUR_EMAIL> check --all 2>&1 | cat
```

`bento check` will exit with a non-zero exit code if it finds issues in your code (see [Exit Codes](#exit-codes)).

If you need help setting up Bento with another CI provider please [open an issue](https://github.com/returntocorp/bento/issues/new?template=feature_request.md). Documentation PRs welcome if you set up Bento with a CI provider that isn’t documented here!

## Help and Community

Need help or want to share feedback? We’d love to hear from you!

- Email us at [support@r2c.dev](mailto:support@r2c.dev)
- Join #bento in our [community Slack](https://join.slack.com/t/r2c-community/shared_invite/enQtNjU0NDYzMjAwODY4LWE3NTg1MGNhYTAwMzk5ZGRhMjQ2MzVhNGJiZjI1ZWQ0NjQ2YWI4ZGY3OGViMGJjNzA4ODQ3MjEzOWExNjZlNTA)
- [File an issue](https://github.com/returntocorp/bento/issues/new?assignees=&labels=bug&template=bug_report.md&title=) or [submit a feature request](https://github.com/returntocorp/bento/issues/new?assignees=&labels=feature-request&template=feature_request.md&title=) directly on GitHub &mdash; we welcome them all!

We’re constantly shipping new features and improvements.

- [Sign up for the Bento newsletter](http://eepurl.com/gDeFvL) &mdash; we promise not to spam and you can unsubscribe at any time
- See past announcements, releases, and issues [here](https://us18.campaign-archive.com/home/?u=ee2dc8f77e27d3739cf4df9ef&id=d13f5e938e)

We’re fortunate to benefit from the contributions of the open source community and great projects such as [Bandit](https://pypi.org/project/bandit/), [ESLint](https://eslint.org/), [Flake8](https://pypi.org/project/flake8/), and their plugins. 🙏

## License and Legal

Please refer to the [terms and privacy document](https://github.com/returntocorp/bento/blob/master/PRIVACY.md).

</br>
</br>
<p align="center">
    <img src="https://web-assets.r2c.dev/r2c-logo-silhouette.png?gh" height="24" alt="r2c logo"/>
</p>
<p align="center">
    Copyright (c) <a href="https://r2c.dev">r2c</a>.
</p>
