import os
import tempfile
import sqlite3
import pytest
from ..print_repository import should_ignore, build_tree, generate_project_contents, get_github_contents


@pytest.fixture
def temp_directory():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


def test_should_ignore():
    assert should_ignore("test.pyc", [".DS_Store", "*.pyc"])
    assert should_ignore("dir/__pycache__/file.py", ["__pycache__"])
    assert not should_ignore("test.py", [".DS_Store", "*.pyc"])


def test_build_tree(temp_directory):
    os.makedirs(os.path.join(temp_directory, "dir1"))
    os.makedirs(os.path.join(temp_directory, "dir2"))
    open(os.path.join(temp_directory, "file1.txt"), "w").close()
    open(os.path.join(temp_directory, "dir1", "file2.txt"), "w").close()

    tree = build_tree(temp_directory, [])
    assert len(tree) == 4
    assert "dir1/" in tree
    assert "    file2.txt" in tree  # Note the indentation for the nested file
    assert "dir2/" in tree
    assert "file1.txt" in tree


def test_generate_project_contents(temp_directory):
    os.makedirs(os.path.join(temp_directory, "dir1"))
    with open(os.path.join(temp_directory, "file1.txt"), "w") as f:
        f.write("Test content")

    output_file = os.path.join(temp_directory, "output.txt")
    generate_project_contents(temp_directory, output_file, False, [])

    with open(output_file, "r") as f:
        content = f.read()

    assert "Project Structure:" in content
    assert "File Contents:" in content
    assert "Test content" in content


def test_generate_project_contents_with_ignore(temp_directory):
    os.makedirs(os.path.join(temp_directory, "dir1"))
    os.makedirs(os.path.join(temp_directory, "__pycache__"))
    with open(os.path.join(temp_directory, "file1.txt"), "w") as f:
        f.write("Test content")
    with open(os.path.join(temp_directory, "__pycache__", "file2.pyc"), "w") as f:
        f.write("Cached content")

    output_file = os.path.join(temp_directory, "output.txt")
    generate_project_contents(temp_directory, output_file, False, ["__pycache__"])

    with open(output_file, "r") as f:
        content = f.read()

    assert "Project Structure:" in content
    assert "File Contents:" in content
    assert "Test content" in content
    assert "Cached content" not in content


@pytest.mark.parametrize("include_db", [True, False])
def test_generate_project_contents_with_db(temp_directory, include_db):
    db_path = os.path.join(temp_directory, "test.db")

    # Create a valid SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test (name) VALUES (?)", ("Test Data",))
    conn.commit()
    conn.close()

    output_file = os.path.join(temp_directory, "output.txt")
    generate_project_contents(temp_directory, output_file, include_db, [])

    with open(output_file, "r") as f:
        content = f.read()

    if include_db:
        assert "SQLite Database File:" in content
        assert "Table: test" in content
        assert "Columns:" in content
        assert "id (INTEGER)" in content
        assert "name (TEXT)" in content
        assert "Test Data" in content
    else:
        assert "DB File (content not included)" in content


@pytest.mark.skip(reason="Requires GitHub API access")
def test_get_github_contents():
    output_file = "github_output.txt"
    get_github_contents("https://github.com/octocat/Hello-World", output_file, False, [])

    assert os.path.exists(output_file)
    with open(output_file, "r") as f:
        content = f.read()

    assert "Project Structure:" in content
    assert "File Contents:" in content

    os.remove(output_file)


def test_main(temp_directory, monkeypatch):
    monkeypatch.setattr("sys.argv", ["print_repository.py", "--dir", temp_directory, "--output", "test_output.txt"])

    from ..print_repository import main
    main()

    assert os.path.exists("test_output.txt")
    os.remove("test_output.txt")