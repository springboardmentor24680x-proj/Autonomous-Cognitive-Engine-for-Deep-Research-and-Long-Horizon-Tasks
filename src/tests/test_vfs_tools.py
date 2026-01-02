import pytest
from tools.vfs_tools import (
    ensure_files,
    ls,
    read,
    write,
    edit,
    delete,
    clear,
    rename,
    help_text
)


@pytest.fixture
def state():
    """Fresh state for each test"""
    return {}


def test_ensure_files(state):
    ensure_files(state)
    assert "files" in state
    assert state["files"] == {}


def test_write_and_read_file(state):
    ensure_files(state)

    msg = write(state, "test.txt", "Hello")
    assert msg == "Wrote to test.txt"

    content = read(state, "test.txt")
    assert content == "Hello"


def test_ls_files(state):
    ensure_files(state)

    write(state, "a.txt", "A")
    write(state, "b.txt", "B")

    files = ls(state)
    assert "a.txt" in files
    assert "b.txt" in files
    assert len(files) == 2


def test_edit_append(state):
    ensure_files(state)
    write(state, "file.txt", "Line1")

    msg = edit(state, "file.txt", "Line2")
    assert msg == "Edited file.txt"

    content = read(state, "file.txt")
    assert content == "Line1\nLine2"


def test_edit_overwrite(state):
    ensure_files(state)
    write(state, "file.txt", "Old")

    msg = edit(state, "file.txt", "New", mode="overwrite")
    assert msg == "Edited file.txt"

    content = read(state, "file.txt")
    assert content == "New"


def test_edit_missing_file(state):
    ensure_files(state)

    msg = edit(state, "missing.txt", "data")
    assert msg == "File not found"


def test_delete_file(state):
    ensure_files(state)
    write(state, "temp.txt", "data")

    msg = delete(state, "temp.txt")
    assert msg == "Deleted temp.txt"

    assert "temp.txt" not in state["files"]


def test_clear_file(state):
    ensure_files(state)
    write(state, "clear.txt", "something")

    msg = clear(state, "clear.txt")
    assert msg == "Cleared clear.txt"

    assert read(state, "clear.txt") == ""


def test_rename_file(state):
    ensure_files(state)
    write(state, "old.txt", "content")

    msg = rename(state, "old.txt", "new.txt")
    assert msg == "Renamed old.txt → new.txt"

    assert "new.txt" in state["files"]
    assert "old.txt" not in state["files"]
    assert read(state, "new.txt") == "content"


def test_help_text():
    text = help_text()

    assert "VFS Commands" in text
    assert "ls" in text
    assert "read <file>" in text
    assert "write <file> <text>" in text
    assert "edit <file> <text>" in text
    assert "delete <file>" in text
