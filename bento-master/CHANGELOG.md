# Changelog

This project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [0.11.1](https://pypi.org/project/bento-cli/0.11.1/) - 2020-04-28

### Fixed

- Upgrade notice now prints to stderr, to avoid affecting JSON output
- Tools with file-based configuration (e.g. `sgrep`) will now have
  their caches invalidated when these configuration files change

## [0.11.0](https://pypi.org/project/bento-cli/0.11.0/) - 2020-04-17

### Added

- Added `gosec`, an open-source tool to detect security vulnerabilities in
  Go projects; to use, run `bento enable tool gosec`
- Both r2c check registries and custom check definitions can now be used with
  the `sgrep` tool; to use a r2c check registry, run
  ```
  BENTO_REGISTRY=r/<registry> bento check -t sgrep ...
  ```
  to use a custom sgrep.live share link, run
  ```
  BENTO_REGISTRY=<share code> bento check -t sgrep ...
  ```
  with your three-character share code (these are the last three characters
  of your sgrep.live share link, e.g. `xQn` from `https://sgrep.live/xQn`)
- Bento can now run all tools within an enclosing Docker container; when
  running Bento within a Docker container, use
  ```
  BENTO_REMOTE_DOCKER=1 bento ...
  ```

### Removed

- Removed the experimental `python-taint` tool
- Removed dependency on `r2c-lib`

### Changed

- The `r2c.boto3` checks are now enabled by default; to disable them on
  a project, run `bento disable tool r2c.boto3`

## [0.10.2](https://pypi.org/project/bento-cli/0.10.2/) - 2020-04-06

### Fixed

- Fixed an issue where the `r2c.registry.latest` tool would fail to run
  in a GitHub Action or other environment with a remote Docker daemon,
  as indicated with the `R2C_USE_REMOTE_DOCKER` environment variable.

## [0.10.1](https://pypi.org/project/bento-cli/0.10.1/) - 2020-03-04

### Added

- Add `ci_provider` field to telemetry and update
  [PRIVACY.md](https://github.com/returntocorp/bento/blob/master/PRIVACY.md) accordingly

### Fixed

- Fix a regression (since 0.8.0) where root paths were not properly ignored
- Fix a regression (since 0.10.0) where `init` failed to offer to update the user's
  global git ignore file
- If .bentoignore is missing, render a clear error message to the user

## [0.10.0](https://pypi.org/project/bento-cli/0.10.0/) - 2020-02-26

### Added

- Added `r2c.registry.latest`, an experimental feature that pulls the latest checks from r2c's check registry
- `bento enable ci` to setup the [Bento GitHub Action](https://github.com/marketplace/actions/bento-check) for applicable projects
- `bento init` now prompts to setup the GitHub Action (when applicable)
- Dlint is enabled by default

### Fixed

- Use shebang detection for shell and python files during `bento init`
- jinja tool only installs if it detects python and html/jinja files
- Fix jinja tool hyperlinks
- Exit when a configured tool cannot be found instead of failing silently

## [0.9.1](https://pypi.org/project/bento-cli/0.9.1/) - 2020-02-14

### Fixed

- ShellCheck detect shell files robustly

## [0.9.0](https://pypi.org/project/bento-cli/0.9.0/) - 2020-02-13

### Added

- Python tools now scan files that don't end in `.py` but have python shebang
- Added ReDoS check via Dlint. The check is off by default. Enable the Dlint tool to run this check: `bento enable tool dlint`.
- Jinja checks added and turned on by default

See [https://bento.dev/checks](https://bento.dev/checks) for more information on new checks

### Fixed

- Bento iterates over files in batches if number of files to check exceeds OS argmax limit

## [0.8.2](https://pypi.org/project/bento-cli/0.8.2/) - 2020-02-05

### Fixed

- `bento check` works with repos with no previous commits
- Verify a path is a file before checking if it contains a shell shebang (shellcheck tool)
- Correctly install autorun even if git-hooks subdirectory is non-existent

## [0.8.1](https://pypi.org/project/bento-cli/0.8.1/) - 2020-01-30

### Fixed

- Perfomance improvements when running in large projects
- Additional human readable check_ids for bandit

## [0.8.0](https://pypi.org/project/bento-cli/0.8.0/) - 2020-01-24

This release represents a major shift in Bento's default behavior: It emphasizes an incremental
and personal, rather than team-wide, workflow that makes Bento a smaller commitment to use:

1. Other project contributors won’t see Bento files or have their workflows changed.
2. You no longer need to manually run Bento. After initialization Bento will automatically
   check for issues in your code as you commit, analyzing only the files that have changed.
3. You won’t see a project’s old issues (tech debt) during initialization. To view them,
   run

   ```bash
   bento check --all
   ```

### Migration

Project configurations have changed in version 0.8. In order to migrate a project from
version 0.7 or earlier:

- Ensure Bento has been upgraded using `pip3 install --upgrade bento-cli`. Run `bento --version`
  to validate Bento’s version.
- `rm -r .bento*` (Use `git rm` if you have previously added Bento files to source control).
- Run `bento init` in the project root.

### New requirements

- Docker must be installed, and the docker client running, to use Bento.

### Changed

How you use Bento has changed significantly in 0.8.

#### Usage changes

- `bento check` will now only check staged changes.
  - Use `bento check --all` to check the entire project.
- `bento archive` will archive findings due to staged diff:

  - Use `bento archive --all` to archive all findings in a project.

#### Other changes

- `hadolint` and `shellcheck` are now enabled by default.
- Messages for findings are no longer truncated.
- `bento init` will now install an empty configuration on a project it can not identify;
  tools may then be manually enabled using `bento enable tool TOOL`. Use `bento enable tool --help`
  to list tools.
- Virtual environments for Python tools are now installed in your home directory, instead of in your
  project directories.
- `eslint` is now installed in your project’s `.bento` directory, and will not modify your project’s
  `package.json`.
- Tool and check names have been modified to improve readability.
- `eslint` is disabled by default. To enable it run `bento enable tool eslint`.

### Added

- On init, Bento will prompt you to ask if you want to add ignore patterns to your global Git ignore file.
  If you agree, Bento will alter this file to ignore Bento configuration files in your git projects.
- `bento enable autorun` and `bento disable autorun` will cause Bento to either begin or stop analyzing
  code on every commit.
- Tab completion can now be installed by Bento. To install for your shell, run `bento enable autocomplete`.
  To remove tab completion, run `bento disable autocomplete`.

### Removed

- `bento check --show-all` has been removed. Use `bento check --all` instead. Archived findings can be found at `~/.bento/archive.json`.
- `bento install-hook` has been removed. Use `bento enable autorun` to run Bento on every commit.
- The histogram formatter is no longer used by default. To show findings with a histogram, run
  `bento check -f histo`.

## [0.7.0](https://pypi.org/project/bento-cli/0.7.0/) - 2019-12-11

### Fixed

- Fixed `r2c.hadolint` issue where it failed to detect files with `.dockerfile` suffixes.
- Fixed `r2c.sgrep` to respect file path when running on specific files with `bento check /path/to/file`

### Changed

- Redesigned `bento init`
  - It now runs `bento check` and `bento archive` itself; these were almost always run manually by users immediately after `bento init`
  - Displays histogram of results
- `bento check` supports running a single tool with the `-t` flag: `bento check -t r2c.flask`
- Reworked user registration flow
- Removed [flake8-builtins](https://github.com/gforcada/flake8-builtins) plugin from `r2c.flask` based on user feedback: codebases with SQLAlchemy models (common in Flask apps) regularly shadow the `id` builtin, causing false positives.
- Added eslint arrow-body-style as a default ignore because it is a style issue.
- Added unused variable/import related checks (eslint no-unused-vars and no-var, flake8 F401 and F841)to default ignore. While useful they are very noisy and are often non-issues.

### Added

- Added `r2c.boto3` tool for [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) framework. To use it on a project, run `bento enable tool r2c.boto3`
- Added additional checks for `r2c.flake8`
  - [unescaped-file-extension](https://checks.bento.dev/en/latest/flake8-flask/unescaped-file-extension)
  - [use-jsonify](https://checks.bento.dev/en/latest/flake8-flask/use-jsonify/)

## [0.6.2](https://pypi.org/project/bento-cli/0.6.2/) - 2019-12-05

### Fixed

- Fixed an issue where upgrade notifications were not shown to users.
- Fix an issue where certain `.gitignore` patterns would cause an error or be skipped by Bento
- Properly render multi-line context in the Clippy formatter.

## [0.6.1](https://pypi.org/project/bento-cli/0.6.1/) - 2019-11-26

### Fixed

- Bento no longer completes initialization if it can't identify a project; this prevents
  confusing errors when subsequently running `bento check`.
- Pinned versions of all 3rd-party Python tools, so that remote package upgrades do not break
  Bento.
- Bento no longer crashes if a project path contains a space.

### Changed

- Results of `bento check` are now printed
  using the Clippy and histogram formatters (see "Added" section below) by default.
- The APIs to enable and disable a check are now `bento enable check [check]` and
  `bento disable check [check]`.
- The `r2c.flask` tool is now enabled by default. It finds best-practice and security bugs in
  code using the Python [Flask](https://www.palletsprojects.com/p/flask/) framework.
- Multiple formatters can now be used to display results from `bento check`. For example,
  `bento check -f stylish -f histo` will display results using the Stylish formatter,
  followed by display using a histogram formatter.
- Progress bars are not emitted to stderr if not a tty; this prevents progress-bar output from
  littering CI logs.
- Updated progress bar glyphs for readability on a wider range of terminal themes.
- Disabled `r2c.flake8` check `B001` by default, in favor of the (also included) `E722` check.

### Added

- Added `r2c.requests`, which finds best-practice and security bugs in code using the Python
  [Requests](https://2.python-requests.org/en/master/) framework. It is enabled by default.
- Added `r2c.sgrep`, a syntactically aware code search tool. It is _not_ enabled by default.
  To use it on a project, run `bento enable tool r2c.sgrep`. Note that Docker is required in
  order to use `r2c.sgrep`.
- All findings, including those previously archived, can now be viewed using
  `bento check --show-all`.
- Tools can now be enabled using `bento enable tool [tool_id]`. Available
  tools can be listed by running `bento enable tool --help` or using shell autocompletion.
  Tools can be disabled using `bento disable tool [tool_id]`.

## 0.6.0

Version 0.6.0 was not released.

## [0.5.0](https://pypi.org/project/bento-cli/0.5.0/) - 2019-11-18

### Fixed

- `r2c.eslint` now properly detects TypeScript imports.
- `r2c.eslint` now detects global node environments (e.g., `jest`),
  and properly resolves their global variables.

### Changed

- To better protect users' data, error messages are no longer reported to our backend.
- `.bentoignore` can now be configured to include patterns from other files; by default
  the contents of the project's `.gitignore` are included. For more information, please see the comments at
  the top of the generated `.bentoignore` file.
- Tab completion times reduced by approximately half.
- Disabled a number of `r2c.eslint` checks by default:
  - `arrow-parens`, as it conflicts with Prettier's default behavior.
  - TypeScript semicolon checking, which is stylistic.
  - `import/no-cycle` which takes 50% of tool runtime on moderately large code bases.
- `r2c.flake8 E306` disabled by default, as it is stylistic in nature.
- Runtime of `r2c.eslint` has been reduced by up to 30% for some projects.

### Added

- Added `r2c.shellcheck` tool for shell scripts. To enable, add `r2c.shellcheck` to the
  tools section of your `.bento.yml`. Note that this tool requires `docker` as a dependency.
- Added `r2c.hadolint` tool for Docker files. To enable, add `r2c.hadolint` to the
  tools section of your `.bento.yml`. Note that this tool requires `docker` to be installed in order to run.

## [0.4.1](https://pypi.org/project/bento-cli/0.4.1/) - 2019-11-14

### Fixed

- Fixes a performance regression due to changes in metrics collection.

## [0.4.0](https://pypi.org/project/bento-cli/0.4.0/) - 2019-11-11

### Changed

- We updated our [privacy policy](https://github.com/returntocorp/bento/commits/master/PRIVACY.md).
  - Notably, we collect email addresses to understand usage and communicate with users through product announcements, technical notices, updates, security alerts, and support messages.

### Added

- Added additional `r2c.click` tool for [Click](http://click.palletsprojects.com/) framework:

  - [flake8-click](https://pypi.org/project/flake8-click/) will be disabled by default.

- Added additional `r2c.flask` tool for [Flask](https://flask.palletsprojects.com/) framework:

  - [flake8-flask](https://pypi.org/project/flake8-flask/) will be disabled by default.

## [0.3.1](https://pypi.org/project/bento-cli/0.3.1/) - 2019-11-08

### Fixed

- Fixed an issue where the tool would fail to install if a macOS user
  had installed `gcc` and then upgraded their OS.
- Fixed a compatibility issue for users with a pre-existing version
  of GitPython with version between 2.1.1 and 2.1.13.

## [0.3.0](https://pypi.org/project/bento-cli/0.3.0/) - 2019-11-01

### Changed

- Bento can now be run from any subdirectory within a project.
- Updated the privacy and terms-of-service statement.

### Added

- File ignores are configurable via [git-style ignore patterns](https://git-scm.com/docs/gitignore) (include patterns
  are not supported). Patterns should be added to `.bentoignore`.

- Added additional checks to the `r2c.flake8` tool:

  - All checks from [flake8-bugbear](https://github.com/PyCQA/flake8-bugbear) (except for B009 and B010,
    which are stylistic in nature).
  - All checks from [flake8-builtins](https://github.com/gforcada/flake8-builtins).
  - All checks from [flake8-debugger](https://github.com/jbkahn/flake8-debugger).
  - All checks from [flake8-executable](https://github.com/xuhdev/flake8-executable).

- Clippy output formatting is now supported.
  - To enable, run: `bento check --formatter clippy`
  - Example output:

```
error: r2c.flake8.E113
   --> foo.py:6:5
    |
  6 |   return x
    |
    = note: unexpected indentation
```

- Autocompletion is now supported from both `bash` and `zsh`. To use:
  - In `bash`, run `echo -e '\neval "$(_BENTO_COMPLETE=source bento)"' >> ~/.bashrc`.
  - In `zsh`, run `echo -e '\neval "$(_BENTO_COMPLETE=source_zsh bento)"' >> ~/.zshrc`.

## [0.2.1](https://pypi.org/project/bento-cli/0.2.1/) - 2019-10-29

### Fixed

- Quoted emails in git configuration do not break user registration.
- Removed files properly invalidate results cache.
- Python tools do not crawl `node_modules`.

## [0.2.0](https://pypi.org/project/bento-cli/0.2.0/) - 2019-10-23

### Changed

- Results are cached between runs. This means that an immediate rerun of
  `bento` will be much faster.
- Broadened library compatibility, especially for common packages:
  - attrs from 18.2.0
  - packaging from 14.0
  - pre-commit from 1.0.0
- `r2c.eslint` ignores `.min.js` files. Bento should only report issues in code, not built artifacts.
- Telemetry endpoint uses `bento.r2c.dev`.

### Added

- Bento check will optionally run only on passed paths, using `bento check [path] ...`.
- Add `r2c.pyre` as a configurable tool. To enable, it must be manually configured in `.bento.yml`.
- Formatters can be specified with short names, and these appear in the help text. For example, `bento check --formatter json`.
- `bento` version is passed to telemetry backend.

### Fixed

- Tool does not crash if a git user does not have an email configured.
- Fixed a regression that caused progress bars to hang after first tool completed.
- Made fully compatible with Python 3.6.
- Tool does not mangle `.gitignore` when that file lacks a trailing newline.
