import pathlib
import subprocess

from os import listdir
from os.path import isfile, join


test_files = [f for f in listdir("tests/") if isfile(join("tests/", f))]

for test_file in test_files:
    with open("tests/" + test_file) as f:
        lines = [line.strip() for line in f.readlines()]

    code = []
    expected_result = []

    reading_code = True
    for line in lines:
        if line == "========":
            reading_code = False
            continue
        if reading_code:
            code.append(line)
        else:
            expected_result.append(line)

    code = "\n".join(code)

    with open("in_code.bal", "w") as f:
        f.write(code)

    subprocess.run(["python3", "compiler/main.py", "in_code.bal", "test_out.bb2"])
    output = subprocess.check_output(["cargo","run", "../test_out.bb2"], cwd="balan2_vm/")

    #TODO: filter out debug logging (but first mark debug logging as such)

    pathlib.Path.unlink("test_out.bb2")
    pathlib.Path.unlink("in_code.bal")

    actual_result = [line.decode("utf-8") for line in output.split(b"\n")]

    assert actual_result == expected_result

