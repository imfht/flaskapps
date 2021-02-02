# athena

<img align="left" src="/static/athena.png">

**athena** is an elegant, minimalist, simple static blog generator
written in Python. It is based on Flask, Pandoc, and Tufte CSS.

You can browse the [live demo here][demo].

## Quick install and run

To install athena:

1. `git clone https://github.com/apas/athena.git`
1. `python3 install.py`

To run athena:

1. `source env/bin/activate`
1. `python athena.py`

athena will start a Flask server at `127.0.0.1:5000`.

To build static HTML:

1. `python athena.py build`

athena will create a new `build/` directory (it's automatically ignored by git.)

## Documentation

You can browse the full athena documentation and read about its philosophy in
[the repository's wiki][wiki].

## License

MIT

[demo]: https://apas.github.io/athena/
[wiki]: https://github.com/apas/athena/wiki
