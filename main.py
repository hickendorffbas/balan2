import sys


with open(sys.argv[1], "r") as code_file:
    code_text = code_file.read()

print(code_text)

