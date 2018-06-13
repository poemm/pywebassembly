*This is nearing completion!*


## pywebassembly.py

PyWebAssembly closely follows *WebAssembly Specification, Release 1.0*, implementing most of chapters 2, 3, 4, 5, and 7. Each piece of code in pywebassembly.py references its definition in the spec, so the spec should be used as a user's manual.

Chapter 2 defines the abstract syntax.

Chapter 3 defines validation rules over the abstract syntax. These rules constrain the syntax, but provide properties such as type-safety. An almost-complete implementation is available as a feature-branch.

Chapter 4 defines execution semantics over the abstract syntax. This implementation passes all `assert_return` and `assert_trap` tests of the official Wasm tests (except for tests involving floating-point numbers, which are not yet implemented).

Chapter 5 defines a binary syntax over the abstract syntax. The implementation is a recursive-descent parser which takes a `.wasm` file and builds an abstract syntax tree out of nested Python lists and dicts. Also implemented are inverses (up to a canonical form) which write an abstract syntax tree back to a `.wasm` file.

Chapter 7 is the Appendix. It defines a standard embedding, and a validation algorithm.


**API**: It may be possible to limit the API to functions defined in the WebAssembly Spec section 7.1 Embedding. These functions are implemented in section "7.1" of pywebassembly.py, but please reference the spec for details. The only awkward part is that `invoke_func` requires specifying `i32.const`, `i64.const`, `f32.const`, or `f64.const` with each argument -- we are considering deviating from the spec and relaxing this requirement.


The following sample code will "spin-up" a VM instance, instantiate a module, and invoke its exported function.


```
# python3

import pywebassembly as wasm

file_ = open('examples/fibonacci.wasm', 'rb')
bytestar = memoryview(file_.read())			#can also use bytearray or bytes instead of memoryview
module = wasm.decode_module(bytestar)			#get module as abstract syntax
store = wasm.init_store()				#do this once for each VM instance
externvalstar = []					#imports, none for fibonacci.wasm
store,moduleinst,ret = wasm.instantiate_module(store,module,externvalstar)
externval = wasm.get_export(moduleinst, "fib")		#we want to call the function "fib"
funcaddr = externval[1]					#the address of the funcinst for "fib"
args = [["i32.const",10]]				#list of arguments, one arg in our case
store,ret = wasm.invoke_func(store,funcaddr,args)	#finally, invoke the function
print(ret)						#list [89] of return values, limitted to one value in Wasm 1.0
```


TODO:
 * Support floating point values and opcodes.
 * Support text format as described in chapter 6.
 * Finish validation, namely, validation of instruction sequences from chapter 3 should follow the validation algorithm in the appendix, which includes tricky cases like after `unreachable`. This is mostly implemented in a feature branch, but needs refactoring.
 * Implement remaining testing opcodes, see `tests/README.md`.


## examples/

Example uses of PyWebAssembly.


## tests/

Testing of PyWebssembly.


# Notes and Conventions.

Both "PyWebassembly" and "pywebassembly" can be used to refer to the project.
