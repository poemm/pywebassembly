*This is nearing completion!*


## pywebassembly.py

PyWebAssembly closely follows [WebAssembly Specification, Release 1.0](https://webassembly.github.io/spec/core/_download/WebAssembly.pdf) (pdf), implementing necessary parts of chapters 2, 3, 4, 5, and 7. Each section of pywebassembly.py references its definition in the Spec document, and follows the same order as the Spec document.

Closely following the linked Spec document is useful for the following reasons.
 - The Spec document can be used as a user's manual.
 - PyWebAssembly can be audited alongside the Spec document.
 - When Wasm 1.1 is released, PyWebAssembly can be updated alongside the Spec document.
 - PyWebAssembly does not introduce invariants or design decisions that are not in the Spec document. There are many subtleties in the 150 page Spec document, and invariants may be difficult to maintain, as I have learned. So it may be naive to over-engineer something beyond the spec.
 - Implementing the Spec document has allowed me to find errors and submit fixes to the Spec document, and I have more fixes coming.

PyWebAssembly is also structured for my personal economy-of-thought as it is being developed and studied for errors. I plan to make it more aesthetically pleasing once it is done.

**API**: It may be possible to limit the API to functions defined in the WebAssembly Spec section 7.1 Embedding. These functions are implemented in section "7.1" of pywebassembly.py, but please reference the spec for details. The only awkward part is that `invoke_func` requires specifying `i32.const`, `i64.const`, `f32.const`, or `f64.const` with each argument -- we are considering deviating from the spec and relaxing this requirement.

The following sample code uses the Spec Embedding API to "spin-up" a VM instance, instantiate a module, and invoke its exported function.


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
 * Support text format as described in chapter 6.
 * Finish validation, namely, validation of instruction sequences from chapter 3 should follow the validation algorithm in the appendix, which includes tricky cases like after `unreachable`. This is mostly implemented in a feature branch, but needs refactoring.
 * Implement remaining testing opcodes, see `tests/README.md`.


## examples/

Example uses of PyWebAssembly.


## tests/

Testing of PyWebAssembly.


# Notes and Conventions.

Both "PyWebAssembly" and "pywebassembly" can be used to as the name of this project.
