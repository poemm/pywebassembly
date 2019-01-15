*This is nearing completion! It is currently being cleaned-up and is in need of an audit.*


## pywebassembly.py

PyWebAssembly closely follows [WebAssembly Specification, Release 1.0](https://webassembly.github.io/spec/core/_download/WebAssembly.pdf) (pdf). Each section of code references its definition in the Spec document.

`spec_structure.py` closely follows chapter 2.
`spec_validation.py` closely follows chapter 3 and 7.3.
`spec_execution.py`closely follows chapter 4.
`spec_binary_format.py` closely follows chapter 5.
`pywebassembly.py` closely follows chapter 7.1.

Closely following the linked Spec document is useful for the following reasons.
 - The Spec document can be used as a user's manual.
 - PyWebAssembly can be audited alongside the Spec document.
 - When Wasm 1.1 is released, PyWebAssembly can be updated alongside the Spec document.
 - PyWebAssembly does not introduce invariants or design decisions that are not in the Spec document. There are many subtleties in the 150 page Spec document, and invariants may be difficult to maintain, as I have learned. So it may be naive to over-engineer something beyond the spec.
 - Implementing the Spec document has allowed me to find errors and submit fixes to the Spec document, and I have more fixes coming.

Another design goal is for PyWebAssembly to be easily used for prototyping changes to the WebAssembly spec. PyWebAssembly is _NOT_ meant to by "Pythonic" or fast. Instead, it is meant to be easily translated to other languages -- a C++ version is under development.

**API**: It may be possible to limit the API to functions defined in the WebAssembly Spec section 7.1 Embedding. These functions are implemented in pywebassembly.py, but please reference the spec for details. The only awkward part is that `invoke_func` requires specifying `i32.const`, `i64.const`, `f32.const`, or `f64.const` with each argument -- we are considering deviating from the spec and relaxing this requirement.

The following code "spins-up" a VM instance, instantiates a module, and invokes an exported function. See the `examples` directory for more examples.


```
# python3

import pywebassembly as wasm

file_ = open('examples/fibonacci.wasm', 'rb')
bytes_ = memoryview(file_.read())			#can also use bytearray or bytes instead of memoryview
module = wasm.decode_module(bytes_)			#get module as abstract syntax
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
 * Clean-up the code, make it aesthetically pleasing, more maintainable.
 * Refactor floating point values to use ctypes float32 and float64, then pass remaining floating point tests.
 * Support text format as described in chapter 6.


## examples/

Example uses of PyWebAssembly.


## tests/

Testing of PyWebAssembly.


# Notes and Conventions.

Both "PyWebAssembly" and "pywebassembly" can be used to as the name of this project.
