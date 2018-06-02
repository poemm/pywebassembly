*WARNING: This is nearing completion and still being tested.*
  

**pyWebAssembly.py**: Closely follows *WebAssembly Specification, Release 1.0, April 11, 2018*. Implements the following chapters.

Chapter 2 which defines the abstract syntax.

Chapter 3 which defines validation rules over the abstract syntax. These rules constrain the syntax, but provide properties such as type-safety. An almost-complete implementation is available as a feature-branch, the only thing missing is validation after opcodes such as `unreachable`.

Chapter 4 which defines execution semantics over the abstract syntax. This is implemented and currently passes all `assert_return` tests in the official Wasm test suite, except for those involving floating-point operations which are yet implemented.

Chapter 5 which defines a binary syntax over the abstract syntax. The spec defines a recursive-descent parser which takes a `.wasm` file and builds a abstract syntax tree out of nested Python lists and dicts. Also implemented are inverses (up to a canonical form) back to a `.wasm` file -- this is useful to transform the syntax tree and write it back to a `.wasm` file.

Appendix which defines parts of a standard embedding, API, and an algorithm to validate instruction sequences. We implement most of this.

Note that functions from the specification are named `spec_<funcname>(...)` and, if available, their inverses (of a canonical form) are named `spec_<funcname>_inv(...)`. (Or some variation of this.)

**examples**: Some sample uses of pyWebAssembly, including a metering injector.



TODO:
 * Floating point canonicalization code injector.
 * Support text format as described in chapter 6.



