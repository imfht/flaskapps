# Bento

Thanks for trying Bento.

Please follow these steps prior to the user interview.

- Install Bento: `pip3 install bento-cli`
- Initialize Bento: `bento init` (please provide your email when prompted)
- Run Bento: `bento check`
- Archive preexisting results: `bento archive`
- Disable unwanted rules: `bento disable r2c.eslint arrow-parens`(this example disables the eslint arrow-parens rule)

## Notes

Bento doesn't do any style checking (whitespace, formatting, etc.) and also doesn't send any code off of your machine. You can read more about privacy in the policy [here](https://github.com/returntocorp/bento/blob/master/PRIVACY.md).

More detailed installation instructions can be found [here](https://github.com/returntocorp/bento).

To initialize Bento, choose a Python, Javascript, or TypeScript project that is managed by Git.

During the initialization, when prompted, please enter the same email address you used to sign up for the interview so we can distinguish your session from other users.

Once you run `bento check`, feel free to fix issues, ignore warnings, or disable specific checks (e.g., `bento disable r2c.eslint arrow-parens`). Just use Bento as many times as you'd like. 🤞

We’re curious if you'll like the `bento archive` feature as much as we do. This command adds all current findings to the archive (creating a .bento-whitelist.yml file). It provides a clean slate for your project, so you can keep coding. You can go back and work through the archived findings in your project over time.

## License

<p align="center">
    <img src="https://r2c.dev/r2c-logo-silhouette.png?beta" height="24" alt="r2c logo"/>
</p>
<p align="center">
    Copyright (c) <a href="https://r2c.dev/">r2c</a>.
</p>
