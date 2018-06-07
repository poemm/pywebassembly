*WARNING: This is nearing completion and still being tested.*
  

**pywebassembly.py**: Closely follows *WebAssembly Specification, Release 1.0, April 11, 2018*. Implements the following chapters.

Chapter 2 which defines the abstract syntax.

Chapter 3 which defines validation rules over the abstract syntax. These rules constrain the syntax, but provide properties such as type-safety. An almost-complete implementation is available as a feature-branch, the only thing missing is validation after opcodes such as `unreachable`.

Chapter 4 which defines execution semantics over the abstract syntax. This is implemented and passes all `assert_return` and `assert_trap` tests of the official Wasm tests, except for for tests involving floating-point which is not yet implemented.

Chapter 5 which defines a binary syntax over the abstract syntax. All functions were implemented, creating a recursive-descent parser which takes a `.wasm` file and builds a abstract syntax tree out of nested Python lists and dicts. Also implemented are inverses (up to a canonical form) back to a `.wasm` file -- this is useful to transform the syntax tree and write it back to a `.wasm` file.

Appendix which defines parts of a standard embedding, and an algorithm to validate instruction sequences. We implement most of this.

Note that functions from the specification are named `spec_<funcname>(...)` and, if available, their inverses (of a canonical form) are named `spec_<funcname>_inv(...)`.

**examples/**: Some sample uses of pyWebAssembly, including a metering injector.

**tests/**:  Testing of pywebassembly.



TODO:
 * Floating point canonicalization code injector.
 * Support text format as described in chapter 6.



