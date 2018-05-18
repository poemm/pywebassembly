*WARNING: This is an early demo in need of a code review.*
  

**pyWebAssembly.py**: Closely follows *WebAssembly Specification, Release 1.0, Dec 13, 2017*. Implements Chapter 5 and necessary parts of Chapters 2 and 4. The resulting recursive-descent parser takes a `.wasm` file and builds a syntax tree with nested lists and dicts. This process is invertible back to a `.wasm` file. Functions from the specification are named `spec_<func>(...)` and their inverses (of a canonical form) are named `spec_<func>_inv(...)`. Update: now includes an interpretter as described in chapter 4, but this has only been tested on fibonacci.wasm and may have many bugs.


**examples**: Some sample uses of pyWebAssembly.



TODO:
 * Validation checker as described in chapter 3. (This is almost done, see the feature branch.)
 * Floating point canonicalization code injector.
 * Support text format as described in chapter 6.



