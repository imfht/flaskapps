# Custom Checks

## Grep

Bento supports user-defined checks written using standard grep syntax. To define your own checks add `.bento-grep.yml` alongside your normal `.bento.yml` file and add `r2c.bandit:` to the `tools` section of the `.bento.yml` file.

When a valid `.bento-grep.yml` and the check is enabled, Bento will run all regex paterns recursively over all your files not in the `.bentoignore` file and report the findings under the `r2c.grep` tool. You can archive, ignore, take any action just like a normal check.

### .bento-grep.yml Syntax

**`patterns:`** _(required)_ - `List[Pattern]` - a list of pattern objects

Each **pattern** is an object with these properties:

**`id`** _(required)_ - `str` - user displayed string that identifies each pattern

**`regex`** _(required)_ - `str` - valid grep regex

**`message`** _(optional)_ - `str` - message to display user. If not provided, the raw line that matched the regex will be used as the message

**`file_extentions`** - _(optional)_ - `List[str]` - list of glob strings. Passed directly to `--include` in `grep`

**`exclude_dirs`** - _(optional)_ - `List[str]` - list of source folders to exclude. Passed directly to `--exclude-dir` in `grep`. You should prefer using `.bentoignore` but if you need to ignore a specific folder for one Pattern this useful

#### Formal Definition

```typescript
interface GrepConfig {
  patterns: Pattern[];
}

interface Pattern {
  id: string;
  regex: string;
  message?: string;
  file_extentions?: string[];
  exclude_dirs?: string[];
}
```

### Example .bento-grep.yml Config

```yaml
patterns:
- id: "no-shell"
    regex: "shell=True"
    message: "shell=True is scary and needs extra review"
    file_extentions:
    - "*.py"
- id: "no-md5"
    regex: import md5
    exclude_dirs:
    - "src/web"
```
