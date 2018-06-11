*This is nearing completion!*
  

**pywebassembly.py**: Closely follows *WebAssembly Specification, Release 1.0, April 11, 2018*. Implements the following chapters.

Chapter 2 which defines the abstract syntax.

Chapter 3 which defines validation rules over the abstract syntax. These rules constrain the syntax, but provide properties such as type-safety. An almost-complete implementation is available as a feature-branch, the only thing missing is validation after opcodes such as `unreachable`.

Chapter 4 which defines execution semantics over the abstract syntax. This is implemented and passes all `assert_return` and `assert_trap` tests of the official Wasm tests, except for for tests involving floating-point which is not yet implemented.

Chapter 5 which defines a binary syntax over the abstract syntax. All functions were implemented, creating a recursive-descent parser which takes a `.wasm` file and builds a abstract syntax tree out of nested Python lists and dicts. Also implemented are inverses (up to a canonical form) back to a `.wasm` file -- this is useful to transform the syntax tree and write it back to a `.wasm` file.

Appendix which defines parts of a standard embedding which is implemented. We also implemented the algorithm to validate instruction sequences, this is untested in a feature branch.


API: It may be possible to use only functions defined in the WebAssembly Spec section 7.1 Embedding. These functions are in pywebassembly.py and labelled "7.1", but please reference the spec for details.


The following sample code will "spin-up" a VM instance, instantiate a module, and invoke its exported function.


```
import pywebassembly as wasm

file_ = open('examples/fibonacci.wasm', 'rb')
bytestar = memoryview(file_.read())			#can also use bytearray, but memoryview does not copy
module = wasm.decode_module(bytestar)			#get module as abstract syntax
store = wasm.init_store()				#do this once for each VM instance
externvalstar = []					#imports, none for fibonacci.wasm
store,moduleinst,ret = wasm.instantiate_module(store,module,externvalstar)
externval = wasm.get_export(moduleinst, "fib")		#we want to call the function "fib"
funcaddr = externval[1]					#the address of the funcinst for "fib"
args = [["i32.const",10]]				#list of arguments, one arg in our case
store,ret = wasm.invoke_func(store,funcaddr,args)	#finally, invoke the function
print(ret)						#should return [89]. note: returns a list with one value
```

The following sample will "spin-up" a new VM, instantiate several modules with imports/exports, and invoke some exported functions.

```
coming soon
```

**examples/**: Some sample uses of pywebassembly, including a metering injector.

**tests/**:  Testing of pywebassembly.



TODO:
 * Support floating point values and opcodes.
 * Support text format as described in chapter 6.
 * Finish validation, namely,`spec_validate_instrstar()` from chapter 3 should follow the validation algorithm in the appendix.
 * Implement remaining testing opcodes, see `tests/README.md`. This includes updating the parser to return errors for `assert_malformed` test. For example, should include error checks  `idx>len(raw) or idx<0` which give "index out of range" error.


