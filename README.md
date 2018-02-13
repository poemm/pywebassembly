*WARNING: This is an early demo in need of a code review.*
  

**pyWebAssembly.py**: Closely follows "WebAssembly Specification, Release 1.0, Dec 13, 2017". Implements Chapter 5, along with necessary parts of Chapters 2 and 4. The resulting recursive-descent parser takes a .wasm file and builds a syntax tree out of Python tuples, lists, and dicts. This process is reversible back to a .wasm file. Functions from the specification are named `spec_<func>(...)` and their "inverses" are named `spec_<func>_inv(...)`.


**metering.py**: Injects a function call before each sequence of unbranching instructions, along with the sum of the costs of instructions in the sequence. Also injects helper functions such as the metering function which adds to the current cycle count, and traps when we exceed a limit.

Before metering (see `fibonacci.wast` for more).
```
  (func (;0;) (type 0) (param i32) (result i32)
    (local i32 i32 i32)
    i32.const 1
    set_local 1
    block  ;; label = @1
      get_local 0
      i32.const 1
      i32.lt_s
      br_if 0 (;@1;)
      i32.const 1
      set_local 3
      i32.const 0
      set_local 2
      loop  ;; label = @2
        get_local 2
        get_local 3
        i32.add
        set_local 1
        get_local 3
        set_local 2
        get_local 1
        set_local 3
        get_local 0
        i32.const -1
        i32.add
        tee_local 0
        br_if 0 (;@2;)
      end
    end
    get_local 1)
```


After metering (see `fibonacci_metered.wast` for more). Notice injected `i32.cost n` `call 1` where n is sum of costs of following instructions (each instruction currently costs 1).
```
  (func (;0;) (type 0) (param i32) (result i32)
    (local i32 i32 i32)
    i32.const 3
    call 1
    i32.const 1
    set_local 1
    block  ;; label = @1
      i32.const 4
      call 1
      get_local 0
      i32.const 1
      i32.lt_s
      br_if 0 (;@1;)
      i32.const 5
      call 1
      i32.const 1
      set_local 3
      i32.const 0
      set_local 2
      loop  ;; label = @2
        i32.const 13
        call 1
        get_local 2
        get_local 3
        i32.add
        set_local 1
        get_local 3
        set_local 2
        get_local 1
        set_local 3
        get_local 0
        i32.const -1
        i32.add
        tee_local 0
        br_if 0 (;@2;)
      end
    end
    i32.const 1
    call 1
    get_local 1)
```

**index.html**: Demo running fibonacci_metered.wasm, with arbitrary argument and cycles limit, and a trap if the cycles limit is exceeded. Arbitrary precision integers are stored as a string or as a sequence of i32s, and are imported and exported to and from fibonacci_metered.wasm.

**fibonacci...**: Various versions of our demo fibonacci function.


TODO:

 * Floating point canonicalization code injector.
 * Interpretter as described in chapter 4.
 * Support text format as described in chapter 6.



