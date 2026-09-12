# microVM
A virtual machine for my bytecode.

## How to Use
To run the VM on a file:
```
python3 src/main.py <bytecode_file>
```

For example, the test binary supplied in `tests/`:
```
python3 src/main.py tests/test.bin
```

## Changelogs
### v1.1.0:
- Improve instruction handling
- Improve stack display on regular exit

### v1.0.0:
- Release

## Other Things
Assembler: [microASM](https://github.com/the-coder256/microASM)
