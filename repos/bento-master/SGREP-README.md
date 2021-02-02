# sgrep README

The goal of `sgrep` is to allow programmers to express complex code _patterns_ with a familiar syntax. The idea is to mix the convenience of grep with the correctness and precision of a compiler frontend. Using sgrep via [Bento](http://bento.dev/) to allow developers and security engineers to easily develop and run custom checks on every commit.

Sgrep was recently presented at a meetup hosted at r2c: [the slides from the meetup are the best way to get a quick introduction](https://r2c.dev/sgrep-public.pdf).

## Principles

sgrep’s design follows 3 principles:

1. **Precision:** `sgrep` works at the **abstract syntax tree level**, not character or line-level. sgrep does not care about differences in spacing, indentation, or comments
2. **Grep-like syntax:** `sgrep` queries look very similar to the original language and use familiar grep-like syntax
3. **Support pattern matching:** `sgrep` provides operators like metavariables (for generic matching) and ellipses (for sequence expansion).

## Installation

`sgrep` has good support for Python and JavaScript, with some support for Java and C, and more languages on the way!

System requirements:

- Python 3.6+
- Docker

On macOS and Ubuntu:

```
$ pip3 install bento-cli
# now change directory to a project of interest
$ bento init
```

## Usage in Bento

[Bento](http://bento.dev/) has a suite of tools and checks it runs by default: **sgrep is not currently enabled by default**. To enable it to run alongside of Bento’s default tools:

```
$ bento enable tool sgrep
```

You can run sgrep independently with the following command:

```
$ bento check -t sgrep --comparison=archive .
```

## Writing Bento Checks

Custom checks in Bento are defined in `.bento/sgrep.yml`. Note that the order of the rules in this file is important! The first rule that matches a code pattern will trigger. This allows you to define patterns with greater specificity first, and fallback to more general patterns later in the file.

`.bento/sgrep.yml` contains a list of `rules` similar to the following:

```
rules:
  - id: is_equal_to_self
    pattern: $X == $X
    message: "This may be a comparator typo (e.g., `>=`, `!=`). X == X will always be true, unless X is NaN."
    languages: [python, javascript]
    severity: WARNING
```

Each rule object has these fields:

| Field     | Type          | Description                                                                                                        | Required |
| --------- | ------------- | ------------------------------------------------------------------------------------------------------------------ | -------- |
| id        | string        | None unique check-id that should be descriptive and understandable in isolation by the user. e.g. `no-unused-var`. | Y        |
| pattern   | string        | See Example Patterns below.                                                                                        | Y        |
| message   | string        | Description of the rule that will be output when a match is found.                                                 | Y        |
| languages | array<string> | Languages the check is relevant for. Can be python or javascript.                                                  | Y        |
| severity  | string        | Case sensitive string equal to WARNING, ERROR, OK                                                                  | Y        |

## Get in Touch!

Have suggestions, feature requests, or bug reports? Send us a note at [support@r2c.dev](mailto:support@r2c.dev). You can also [file an issue](https://github.com/returntocorp/bento/issues/new?assignees=&labels=bug&template=bug_report.md&title=), [submit a feature request](https://github.com/returntocorp/bento/issues/new?assignees=&labels=feature-request&template=feature_request.md&title=), or [join our community Slack](https://join.slack.com/t/r2c-community/shared_invite/enQtNjU0NDYzMjAwODY4LWE3NTg1MGNhYTAwMzk5ZGRhMjQ2MzVhNGJiZjI1ZWQ0NjQ2YWI4ZGY3OGViMGJjNzA4ODQ3MjEzOWExNjZlNTA).

sgrep’s primary author started development of the tool at Facebook. For information about the old version of sgrep, see the archive at https://github.com/facebookarchive/pfff/wiki/Sgrep.

## Example Patterns

### expression Matching

```
pattern: 1 + foo(42)

# CODE EXAMPLES

foobar(1 + foo(42)) + whatever()
```

### metavariables

```
pattern: $X + $Y

# CODE EXAMPLES

foo() + bar()
```

**Matching Identifiers**

```
pattern: import $X

# CODE EXAMPLES

import random
```

**Reusing Metavariables**

```
pattern: ￼$X == $X

# CODE EXAMPLES

1+2 == 1+2
```

### Function Calls

```
pattern: foo(...)

# CODE EXAMPLES

foo(1,2)
```

The above will not match patterns like `obj.foo(1,2)` because the AST for a function differs from a method call internally.

**With Arguments After a Match**

```
pattern: foo(1, ...)

# CODE EXAMPLES

foo(1, "extra stuff", False)
foo(1) # matches no arguments as well
```

**With Arguments Before a Match**

```
pattern: foo(..., 1, ...)

# CODE EXAMPLES

foo(1, 2)
foo(2, 1)
foo(2, 3, 1)
```

**Object with Method Call**

```
pattern: $X.get(..., None)

# CODE EXAMPLES

json_data.get('success', None)
```

**Keyword Arguments in Any Order **

```
pattern: foo(kwd1=$X, err=$Y)

# CODE EXAMPLES (keyword arguments in arbitrary order)

foo(err=False, kwd1=True)

```

### String Matching

**Using the ‘...’ Operator**

```
pattern: foo("...")

# CODE EXAMPLES

foo("this is a specific string")

```

**Using [OCaml regular expression](https://caml.inria.fr/pub/docs/manual-ocaml/libref/Str.html) Patterns**

```
pattern: foo("=~/.*a.*/")

# CODE EXAMPLES

foo("this has an a")
```

### conditionals

```
pattern: if $X:
           $Y

# CODE EXAMPLES

if __name__ == "__main__":
    print('hello world')
```

```
pattern: if $X:
           ...

# CODE EXAMPLES

if __name__ == "__main__":
    print('hello world')
    foo()
    bar()
```

Note you can’t match a half statement; both of the examples above must specify the contents of the condition’s body (e.g. `$Y` and `...`), otherwise they are not valid AST elements.

### In a statement context, a Metavariable can also match any statement

```
pattern: if $X:
           $Y

# CODE EXAMPLES
if 1:
  foo()

if 2:
  return 1

if 3:     # matches a “block” (a single statement containing multiple statements)
  foo()
  bar()
```

Because in Python there is usually no terminator (e.g., `;`), there is an ambiguity about `$Y` in the above, which could match a statement and also an expression that is then matched later.

### Match on import types

```
subprocess.Popen(...)

# CODE EXAMPLES

import subprocess as s
s.Popen()
```

## Limitations

### sgrep is not grep

```
'foo'
which is parsed as an expression pattern, will match code like
foo()
bar+foo
foo(1,2)

but will not match code like
import foo

because in the above, foo is not an expression, but rather a name part of an import statement.
```

### You can not use a half expression or half statement pattern

```
'1+'  or 'if $X:' are not valid patterns because they are not full AST elements.
```
