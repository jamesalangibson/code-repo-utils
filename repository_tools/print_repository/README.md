# Print Repository

`print_repository.py` is a Python script that generates a text file containing the structure and contents of a Python project. It's useful for creating a snapshot of your project's code, which can be helpful for documentation, code reviews, or working with large language models.

## Features

- Generates a tree-like structure of your project directory
- Includes the content of all files (except those ignored)
- Can ignore specified files and directories
- Supports local directories and GitHub repositories
- Option to include or exclude database (.db) file contents

## Installation

1. Ensure you have Python 3.11 or higher installed.
2. Clone this repository or download the `print_repository.py` file.
3. Install the required dependencies:

```
poetry install
```

## Usage

### Basic Usage

To generate a text file of your local Python project:

```
python print_repository.py --dir /path/to/your/project --output output.txt
```

### Command-line Arguments

- `--dir`: The directory of the project (default: current directory)
- `--output`: The name of the output file (default: project_contents.txt)
- `--include-db`: Include contents of .db files (default: False)
- `--ignore-patterns`: Patterns of files and directories to ignore (default: .DS_Store .git .idea __pycache__ *.pyc venv tests *.log poetry.lock)
- `--github-url`: URL of the GitHub repository to process (for GitHub repos instead of local directories)

### Examples

1. Process a local directory with custom ignore patterns:

```
python print_repository.py --dir /path/to/project --output project_snapshot.txt --ignore-patterns .DS_Store .git tests **pycache** .idea *.log poetry.lock
```

2. Include database contents:

```
python print_repository.py --dir /path/to/project --output project_with_db.txt --include-db
```

3. Process a GitHub repository:

```
python print_repository.py --github-url https://github.com/username/repo --output github_project.txt
```

## Output

The script generates a text file with two main sections:

1. Project Structure: A tree-like representation of your project's directory structure.
2. File Contents: The content of each file in your project, preceded by the file's path.

## Notes

- The script respects the ignore patterns for both the directory structure and file contents.
- Binary files and ignored files are not included in the output.
- For large projects, the output file can be quite large. Make sure you have sufficient disk space.

## Contributing

Contributions to improve `print_repository` are welcome. Please feel free to submit pull requests or create issues for bugs and feature requests.

## License

This project is open-source and available under the MIT License.