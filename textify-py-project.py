import os
import argparse
import sqlite3

def generate_tree(startpath):
    tree = []
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        tree.append(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            tree.append(f"{subindent}{f}")
    return '\n'.join(tree)

def write_file_contents(output_file, file_path, is_db_file=False):
    if is_db_file:
        write_db_contents(output_file, file_path)
    else:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                output_file.write(f"\n\n--- File: {file_path} ---\n\n")
                output_file.write(file.read())
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='iso-8859-1') as file:
                    output_file.write(f"\n\n--- File: {file_path} (ISO-8859-1 encoding) ---\n\n")
                    output_file.write(file.read())
            except Exception as e:
                output_file.write(f"\n\nError reading {file_path}: {str(e)}\n\n")

def write_db_contents(output_file, db_path):
    output_file.write(f"\n\n--- SQLite Database File: {db_path} ---\n\n")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            output_file.write(f"\nTable: {table_name}\n")
            output_file.write("-" * (len(table_name) + 7) + "\n")

            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            output_file.write("Columns:\n")
            for column in columns:
                output_file.write(f"  {column[1]} ({column[2]})\n")

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            output_file.write(f"\nTotal rows: {row_count}\n")

            # Sample data (first 5 rows)
            output_file.write("\nSample Data (up to 5 rows):\n")
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            rows = cursor.fetchall()
            for row in rows:
                output_file.write(f"  {row}\n")

            output_file.write("\n")

        conn.close()
    except sqlite3.Error as e:
        output_file.write(f"An error occurred: {e}\n")

def generate_project_contents(project_dir, output_file_path, include_db):
    if os.path.exists(output_file_path):
        print(f"Warning: The file '{output_file_path}' already exists and will be overwritten.")

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        # Write the tree structure
        output_file.write("Project Structure:\n")
        output_file.write(generate_tree(project_dir))
        output_file.write("\n\nFile Contents:\n")

        for root, dirs, files in os.walk(project_dir):
            # Exclude some directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'venv', '__pycache__', '.idea']]
            
            for file in files:
                file_path = os.path.join(root, file)
                is_db_file = file.endswith('.db')
                
                if is_db_file and not include_db:
                    output_file.write(f"\n\n--- DB File (content not included): {file_path} ---\n\n")
                elif file.endswith(('.py', '.txt', '.md', '.yaml', '.yml', 'Dockerfile', 'docker-compose.yml', 'poetry.toml', '.db')) or file in ['Dockerfile', 'docker-compose.yml', 'poetry.toml']:
                    write_file_contents(output_file, file_path, is_db_file)

def main():
    parser = argparse.ArgumentParser(description="Generate a text file containing the structure and contents of a Python project.")
    parser.add_argument('--dir', type=str, default='.', help='The directory of the project (default: current directory)')
    parser.add_argument('--output', type=str, default='project_contents.txt', help='The name of the output file (default: project_contents.txt)')
    parser.add_argument('--include-db', action='store_true', help='Include contents of .db files (default: False)')
    
    args = parser.parse_args()

    project_directory = os.path.abspath(args.dir)
    output_file = args.output
    include_db = args.include_db

    generate_project_contents(project_directory, output_file, include_db)
    print(f"Project contents written to {output_file}")

if __name__ == "__main__":
    main()