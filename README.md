*WARNING: This is an early demo in need of a code review.*
  

**pyWebAssembly.py**: Closely follows "WebAssembly Specification, Release 1.0, Dec 13, 2017". Implements Chapter 5, along with necessary parts of Chapters 2 and 4. The resulting recursive-descent parser takes a .wasm file and builds a syntax tree out of Python tuples, lists, and dicts. This file includes an inverse of a canonical form of each function, allowing mapping a syntax tree back to a .wasm file. Functions from the specification are named `spec_<func>(...)` and their inverses are named `spec_<func>_inv(...)`.


**metering.py**: Injects a function call before each sequence of unbranching instructions. This metering function adds to the current cycle count, and traps when we exceed a limit.

Before metering (see fibonacci.wastfor more):
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


After metering (see fibonacci_metered.wast for more):
```
  (func (;0;) (type 0) (param i32) (result i32)
    (local i32 i32 i32)
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
    get_local 1)
```

**index.html**: Test for metered fibonacci function in fibonacci_metered.py.



**fibonacci...**: Various versions of a fibonacci function.

Notes:

 * Because JavaScript does not support 64-bit integers, we allow passing i64 arguments to WebAssembly as two i32s. Helper code is available in both JavaScript and Web








