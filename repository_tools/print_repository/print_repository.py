import os
import argparse
import sqlite3
import fnmatch
from github import Github
import base64


def should_ignore(path, ignore_patterns):
    path_parts = path.split(os.sep)
    return any(
        any(fnmatch.fnmatch(part, pattern) for pattern in ignore_patterns)
        for part in path_parts
    )

def build_tree(directory, ignore_patterns, prefix=""):
    tree = []
    contents = sorted(os.listdir(directory))
    for item in contents:
        path = os.path.join(directory, item)
        rel_path = os.path.relpath(path, start=directory)
        if should_ignore(rel_path, ignore_patterns):
            continue
        if os.path.isdir(path):
            tree.append(f"{prefix}{item}/")
            tree.extend(build_tree(path, ignore_patterns, prefix + "    "))
        else:
            tree.append(f"{prefix}{item}")
    return tree

def write_file_contents(output_file, file_path, is_db_file=False, content=None):
    if is_db_file:
        write_db_contents(output_file, file_path)
    else:
        try:
            if content:
                file_content = content
            else:
                with open(file_path, 'r', encoding='utf-8') as file:
                    file_content = file.read()
            output_file.write(f"\n\n--- File: {file_path} ---\n\n")
            output_file.write(file_content)
        except UnicodeDecodeError:
            try:
                if not content:
                    with open(file_path, 'r', encoding='iso-8859-1') as file:
                        file_content = file.read()
                output_file.write(f"\n\n--- File: {file_path} (ISO-8859-1 encoding) ---\n\n")
                output_file.write(file_content)
            except Exception as e:
                output_file.write(f"\n\nError reading {file_path}: {str(e)}\n\n")


def write_db_contents(output_file, db_path):
    output_file.write(f"\n\n--- SQLite Database File: {db_path} ---\n\n")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            output_file.write(f"\nTable: {table_name}\n")
            output_file.write("-" * (len(table_name) + 7) + "\n")

            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            output_file.write("Columns:\n")
            for column in columns:
                output_file.write(f"  {column[1]} ({column[2]})\n")

            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            output_file.write(f"\nTotal rows: {row_count}\n")

            output_file.write("\nSample Data (up to 5 rows):\n")
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            rows = cursor.fetchall()
            for row in rows:
                output_file.write(f"  {row}\n")

            output_file.write("\n")

        conn.close()
    except sqlite3.Error as e:
        output_file.write(f"An error occurred: {e}\n")


def generate_project_contents(project_dir, output_file_path, include_db, ignore_patterns):
    if os.path.exists(output_file_path):
        print(f"Warning: The file '{output_file_path}' already exists and will be overwritten.")

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write("Project Structure:\n")
        tree = build_tree(project_dir, ignore_patterns)
        output_file.write("\n".join(tree))
        output_file.write("\n\nFile Contents:\n")

        for root, _, files in os.walk(project_dir):
            rel_path = os.path.relpath(root, project_dir)
            if should_ignore(rel_path, ignore_patterns):
                continue

            for file in files:
                file_path = os.path.join(root, file)
                rel_file_path = os.path.relpath(file_path, project_dir)

                # Check if the file or any of its parent directories should be ignored
                if should_ignore(rel_file_path, ignore_patterns):
                    continue

                is_db_file = file.endswith('.db')

                if is_db_file and not include_db:
                    output_file.write(f"\n\n--- DB File (content not included): {file_path} ---\n\n")
                else:
                    write_file_contents(output_file, file_path, is_db_file)


def get_github_contents(github_url, output_file_path, include_db, ignore_patterns):
    g = Github()
    repo = g.get_repo("/".join(github_url.split("/")[-2:]))

    def build_github_tree(path="", prefix=""):
        tree = []
        contents = repo.get_contents(path)
        for content in contents:
            if should_ignore(content.path, ignore_patterns):
                continue
            if content.type == "dir":
                tree.append(f"{prefix}{content.name}/")
                tree.extend(build_github_tree(content.path, prefix + "    "))
            else:
                tree.append(f"{prefix}{content.name}")
        return tree

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write("Project Structure:\n")
        tree = build_github_tree()
        output_file.write("\n".join(tree))

        output_file.write("\n\nFile Contents:\n")

        def process_github_contents(path=""):
            contents = repo.get_contents(path)
            for content in contents:
                if should_ignore(content.path, ignore_patterns):
                    continue
                if content.type == "dir":
                    process_github_contents(content.path)
                else:
                    is_db_file = content.name.endswith('.db')
                    if is_db_file and not include_db:
                        output_file.write(f"\n\n--- DB File (content not included): {content.path} ---\n\n")
                    else:
                        file_content = base64.b64decode(content.content).decode('utf-8')
                        write_file_contents(output_file, content.path, is_db_file, content=file_content)

        process_github_contents()


def main():
    parser = argparse.ArgumentParser(
        description="Generate a text file containing the structure and contents of a Python project.")
    parser.add_argument('--dir', type=str, default='.',
                        help='The directory of the project (default: current directory)')
    parser.add_argument('--output', type=str, default='project_contents.txt',
                        help='The name of the output file (default: project_contents.txt)')
    parser.add_argument('--include-db', action='store_true', help='Include contents of .db files (default: False)')
    parser.add_argument('--ignore-patterns', type=str, nargs='+',
                        default=['.DS_Store', '.git', '.idea', '__pycache__', '*.pyc', 'venv', 'tests', '*.log',
                                 'poetry.lock'],
                        help='Patterns of files and directories to ignore (default: .DS_Store .git .idea __pycache__ *.pyc venv tests *.log poetry.lock)')
    parser.add_argument('--github-url', type=str, help='URL of the GitHub repository to process')

    args = parser.parse_args()

    output_file = args.output
    include_db = args.include_db
    ignore_patterns = args.ignore_patterns

    if args.github_url:
        get_github_contents(args.github_url, output_file, include_db, ignore_patterns)
    else:
        project_directory = os.path.abspath(args.dir)
        generate_project_contents(project_directory, output_file, include_db, ignore_patterns)

    print(f"Project contents written to {output_file}")


if __name__ == "__main__":
    main()