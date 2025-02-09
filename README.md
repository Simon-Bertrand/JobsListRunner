# JobsListRunner

JobsListRunner (jlr) is a simple command-line interface (CLI) tool to manage job lists. It supports generating, executing, and clearing job lists.

## Installation

The lib requires pydantic and pyyaml libraries.
Install it with :

```sh
pip install git+https://github.com/Simon-Bertrand/JobsListRunner.git
```

The CLI will be available in your current environment using `python -m jlr` or directly `jlr`

## Usage

```sh
jlr [-h] {generate,execute,clear} ...
```

## Commands

- `generate`: Generates a new job list from a script folder
- `execute`: Executes the jobs in the generated list.
- `clear`: Clears dates in the specified job list.

## Examples

### Generate a Job List

```sh
jlr generate /path/to/script/folder -o ./jobs_list.yaml
```

### Execute the Job List

```sh
jlr execute ./jobs_list.yaml -n 4
```

### Clear the Job List

```sh
jlr clear ./jobs_list.yaml
```

## Help

For more information on a specific command, use the `-h` flag:

```sh
jlr -h
```
