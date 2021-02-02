Contributing
============

## Communication

Don't be shy, ask for help. If you have a question, comment, concern, or
great idea just open up an issue to start the conversation. You can
also email me.

## Commits

* __Rebase__: Whenever you have made commits on your local copy while at 
  the same time commits have been made upstream you should `rebase` instead
  of pull/merge. Rebasing will put the upstream commits before your new
  local commits.
  
  ```sh
  git pull --rebase upstream
  ```

* __References__: When you are addressing a issue you should reference
  that issue in your commits or pull requests. For example, if you just
  addressed issue #11 the first line of your commit message should be
  prefixed with `(gh-11)`. Check out this commit https://github.com/cameronbwhite/Flask-CAS/commit/cfa2cde631e6f4053acc54da4ea21c14c2dde35f 

## Testing

All code summited needs to pass the current test suite. 

### Testing Dependencies

Installation of Flask-CAS does not install the testing dependencies.
You will need to install `Nose` and `Mock`. The dependencies can be
installed with pip.

```sh
pip install Nose Mock
```

### Running Tests

Tests can be ran locally as well as by TravisCI. 

```sh
nosetests
```

## License

This project is under the BSD Clause 3 license. Any and all
future contributions will be licensed the same. If you put statements that
declare your code licensed under anything else they will not be pulled.
