from tools.vfs_tools import write_file, read_file, list_files


def test_vfs_operations():
    vfs = {"files": {}}

    # Write file
    write_file.invoke({
        "filename": "a.txt",
        "content": "hello",
        "vfs": vfs
    })

    # List files
    result = list_files.invoke({
        "vfs": vfs
    })

    assert "a.txt" in result

    # Read file
    content = read_file.invoke({
        "filename": "a.txt",
        "vfs": vfs
    })

    assert content == "hello"