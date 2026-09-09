from sys import argv
import vm

if len(argv) < 2:
    print("error: no input file")
    exit(1)

with open(argv[1], "rb") as file:
    content = file.read()

exit_code = vm.VM().run(content)
print(f"Execution finished with exit code {exit_code}")