import pathlib


# Todo
#  - [ ] process one file (full file path)
#  - [ ] process list of files (full file paths)
#  - [ ] process files that match pattern (file names)
#  - [ ] process files that match pattern within a given scope (full directory path)


def bump_version(
        old_version: str,
        new_version: str,
        file_path: pathlib.Path,
):
    # Read in the file
    with open(file_path, 'r') as fr:
      filedata = fr.read()

    # Replace the target string
    filedata = filedata.replace(
        old_version,
        new_version,
    )

    # Write the file out again
    with open(file_path, 'w') as fw:
      fw.write(filedata)


def batch_bump_version(
        old_version: str,
        new_version: str,
        files: list[pathlib.Path],
):

    for f in files:
        bump_version(
            old_version=old_version,
            new_version=new_version,
            file_path=f,
        )


if __name__ == "__main__":
    pass
