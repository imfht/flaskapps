# Bento Privacy Policy

Bento collects usage data to help us improve the product. This document describes:

- the principles that guide our data-collection decisions
- the breakdown of the data that are and are not collected
- how we use the data we collect to make Bento better

## Principles

These principles inform our decisions around data collection:

1. **Transparency**: Collect and use data in a way that is clearly explained to the user and benefits them
2. **User control**: Put users in control of their data at all times
3. **Limited data**: Collect what is needed, de-identify where possible, and delete when no longer necessary

## Collected Data

Bento collects data to help improve its underlying tools and user experience. Two types of data are collected:

### Usage Data

As the name suggests, usage data tell us what commands you ran, what options and flags you ran them with, as well as information that helps us debug any issues users may be facing, e.g.

- The name of the command you ran,
- Arguments or options,
- How long the command took to run,
- If the command ran in a CI environment,
- The version of Bento you're using,
- What OS and shell you're running in, etc.

See Description of Fields for a full list.

While using Bento in Beta, we associate these data with your email address to facilitate our outreach efforts.

### Results Data

Results data contain information about the code check rules that fired when you ran Bento, and help us make our rules better. These include:

- The number of times rules fired across your repo,
- Rules you disabled,
- The number of results that were fixed or archived since the last run, and
- Hashes of the repository and commit for which Bento produced these results,

We consider this information more sensitive and do NOT associate it with user-identifiable information.

### Data NOT collected

We strive to balance our desire to collect data for improving Bento and its underlying tools with our users' need for privacy.

The following items don't leave your computer and are not sent or shared with anyone.

- Source code
- Raw repository names, filenames, or commit hashes,
- User-identifiable data about Bento's findings in your code

### Examples

This is a sample blob of usage data collected by Bento and sent to r2c:

```json
{
  "X-R2C-Bento-Cli-Version": "0.3.1b2",
  "X-R2C-Bento-User-Platform": "Linux-4.10.0-35-generic-x86_64-with-debian-9.11",
  "X-R2C-Bento-User-Shell": "zsh",
  "client_ip": "35.221.28.0",
  "command": "check",
  "command_kwargs": {
    "formatter": null,
    "pager": true,
    "paths": [],
    "staged_only": true
  },
  "duration": 1.251570224761963,
  "email": "test@returntocorp.com",
  "exit_code": 2,
  "hash_of_commit": "641c9d42ecc5a442009d241f6528ab982f3d47ab2c61f2dc330ded3da4538aa6",
  "is_ci": true,
  "ci_provider": "gitlab-ci",
  "repository": "4a74fa9309d6f79a91442d95f35e68fc8838796448b4398527faabad7aa21a24",
  "timestamp": "2019-11-08T17:55:16.432Z",
  "ua": "python-requests/2.22.0"
}
```

The following is a sample of the results data we collect:

```json
{
    "X-R2C-Bento-Cli-Version": "0.3.1b2",
    "X-R2C-Bento-User-Platform": "Linux-4.10.0-35-generic-x86_64-with-debian-9.11",
    "X-R2C-Bento-User-Shell": "",
    "check_id": "E999",
    "client_ip": "35.231.49.0",
    "hash_of_commit": "a6847d624cad44f9bb3ab40963842289e2fc5c6f",
    "count": 1,
    "filtered_count": 0,
    "ignored_rules": [
        "B009",
        "B010",
        "E101",
        "E111",
        "E114",
        "E115",
        "E116",
        ...
    ],
    "path_hash": "c2d20e995af6b538c471ccfe0130a32ed950abcdcd4cd0c27e38160fab97c07f",
    "repository_hash": "79d7408f2c194d95bc502660d46a7be8b838cab9ad24a09e32e29846f7a7d649",
    "timestamp": "2019-11-08T23:56:59.251Z",
    "tool": "r2c.flake8",
    "ua": "python-requests/2.22.0"
}
```

### Description of fields

| Field                     | Description                                                                           | Use case                                                                                                                    |
| :------------------------ | :------------------------------------------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------- |
| X-R2C-Bento-Cli-Version   | The version of Bento being used                                                       | Understanding average upgrade patterns and debugging specific errors                                                        |
| X-R2C-Bento-User-Platform | OS description                                                                        | Reproduce and debug issues with specific platforms                                                                          |
| X-R2C-Bento-User-Shell    | shell description                                                                     | Reproduce and debug issues with specific shells                                                                             |
| duration                  | How long the command took to run                                                      | Understanding performance issues                                                                                            |
| is_ci                     | A boolean determining whether Bento was running in CI                                 | Understanding if Bento is adopted in CI pipeline or is used locally                                                         |
| ci_provider               | Name of the CI provider running Bento                                                 | Understanding CI adoption patterns                                                                                          |
| ua                        | user agent                                                                            | Reserved for future Bento variants                                                                                          |
| client_ip                 | IP address                                                                            | Provide timely support based on timezones and understand geographic difference in use                                       |
| tool                      | The underlying tool whose results a telemetry event contains [r2c.eslint, r2c.flake8] | Improving underlying OSS tools and excluding unwanted checks                                                                |
| timestamp                 | Time when the event fired                                                             | Understanding tool usage over time                                                                                          |
| repository                | SHA256 hash of the repository name                                                    | Understanding if results we're receiving are associated with the same codebase                                              |
| commit                    | Git commit hash                                                                       | Understanding if results we're receiving are associated with the same codebase                                              |
| email                     | email address that users enter upon installation                                      | User reach-out during out Beta period                                                                                       |
| ignored_rules             | Rules that are explicitly ignored by Bento (by using `bento disable`)                 | Understanding which checks are useful to users and which are not                                                            |
| path_hash                 | SHA256 hash of the relative file path which is relevant to the event                  | Understanding the fix rate of Bento results; in conjunction with check_id and result counts, infer if results are addressed |
| check_id                  | SHA256 hash of the check_id which caused the event                                    | Measure check adoption and fixes; in conjuction with path_hash and count, infer if checks get addressed                     |
| count                     | Number of times a check fires for this path                                           | Number of times a check fires for a path; in conjunction with path_hash and rule_id_hash, infer if checks get addressed     |
| filtered_count            | Number of times a check fires, not including archived checks.                         | Measure check adoption and fixes                                                                                            |
| exit_code                 | Bento's exit code, which helps us understand if Bento failed with an error            | Debug commonly occurring issues                                                                                             |

## Data Usage

We use this information for the following purposes:

- to support, and improve Bento and the underlying OSS tools it wraps
- to communicate with users, if users supply their email address, including by sending product announcements, technical notices, updates, security alerts, and support messages
- to better understand user needs and interests, and to solicit user feedback about Bento

## Data Sharing

We use some third party companies and services to help administer and provide Bento, for example for hosting, customer support, product usage analytics, email delivery, and database management. These third parties are permitted to handle user information only to perform these tasks in a manner consistent with this document and are obligated not to disclose or use it for any other purpose.

We do not share or sell the information that users provide to us with other organizations without explicit consent, except as described in this document.
