*WARNING: This is nearing completion and still being tested.*
  

**pyWebAssembly.py**: Closely follows *WebAssembly Specification, Release 1.0, April 11, 2018*. Implements Chapter 2 (Abstract Syntax), Chapter 3 (Validation), Chapter 4 (Execution), Chapter 5 (Binary Format), and parts of the Appendix. Functions from the specification are named `spec_<func>(...)` and, if available, their inverses (of a canonical form) are named `spec_<func>_inv(...)`.

Chapter 2 defines the abstract syntax.

Chapter 3 defines validation rules over the abstract syntax. These rules are used in type-checking. An almost-complete implementation is available as a feature-branch, the only thing missing is validation after the `unreachable` opcode.

Chapter 4 defines execution semantics over the abstract syntax. This is implemented and currently being tested. It successfully executes fibonacci.wasm and many tests in the official Wasm test suite. Also, floating-point operations are not yet supported.

Chapter 5 defines a binary syntax over the abstract syntax. All functions were implemented, creating a recursive-descent parser which takes a `.wasm` file and builds a abstract syntax tree out of nested Python lists and dicts. Also implemented are inverses (up to a canonical form) back to a `.wasm` file.

Appendix defines parts of a standard embedding, and an algorithm to validate instruction sequences.


**examples**: Some sample uses of pyWebAssembly, including a metering injector.



TODO:
 * Floating point canonicalization code injector.
 * Support text format as described in chapter 6.



