#!/usr/bin/env python
"""
    PyWebAssembly - Implmentation of WebAssembly, and some tools.
    Copyright (C) 2018-2019  Paul Dworzanski

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


import sys
sys.path.append('..')

import pywebassembly as wasm


"""
0000000 6100 6d73 0001 0000 1801 6005 7f01 7f01
0000010 0160 007f 0160 017f 607f 7f02 007f 0060
0000020 7f01 0603 0005 0201 0403 0404 7001 0000
0000030 0305 0001 0601 0415 017f 0041 7f0b 4101
0000040 0b00 017f 0041 7f0b 4101 0b00 4e07 0605
0000050 656d 6f6d 7972 0002 6603 6269 0000 670e
0000060 7465 6d5f 7861 635f 6379 656c 0073 0e02
0000070 6573 5f74 616d 5f78 7963 6c63 7365 0300
0000080 6719 7465 6e5f 6d75 6d5f 7861 635f 6379
0000090 656c 5f73 6863 6e75 736b 0400 f90a 0501

00000a0 0153 7f03 0341 0110 0141 0121 4002 0441
00000b0 0110 0020 0141 0d48 4100 1005 4101 2101
00000c0 4103 2100 0302 4140 100d 2001 2002 6a03
00000d0 0121 0320 0221 0120 0321 0020 7f41 226a
00000e0 0d00 4100 1001 0b01 0141 0110 410b 1002
00000f0 2001 0b01 014d 7f01 0023 0121 0023 0020
0000100 246b 2300 2000 4b01 2304 2101 2301 4101
0000110 6b01 0124 0123 0120 044b 0223 0121 0223
0000120 0141 246b 2302 2002 4b01 2304 2103 2301
0000130 4103 6b01 0324 0323 0120 044b 0b00 0b0b
0000140 0b0b 0025 0020 0041 0446 237f 0500 0020
0000150 0141 0446 237f 0501 0020 0241 0446 237f
0000160 0502 0323 0b0b 0b0b 002a 0020 0041 0446
0000170 0120 0024 2005 4100 4601 2004 2401 0501
0000180 0020 0241 0446 0120 0224 2005 2401 0b03
0000190 0b0b 040b 4100 0b04                    
0000198
user@user:~/mnt/ethereum/repos/pywebassembly/poemm-pywebassembly/examples$ 
user@user:~/mnt/ethereum/repos/pywebassembly/poemm-pywebassembly/examples$ 
user@user:~/mnt/ethereum/repos/pywebassembly/poemm-pywebassembly/examples$ 
user@user:~/mnt/ethereum/repos/pywebassembly/poemm-pywebassembly/examples$ hexdump fibonacci_metered.wasm_orig 
0000000 6100 6d73 0001 0000 1801 6005 7f01 7f01
0000010 0160 007f 0160 017f 607f 7f02 007f 0060
0000020 7f01 0603 0005 0201 0403 0404 7001 0000
0000030 0305 0001 0601 0415 017f 0041 7f0b 4101
0000040 0b00 017f 0041 7f0b 4101 0b00 4e07 0605
0000050 656d 6f6d 7972 0002 6603 6269 0000 670e
0000060 7465 6d5f 7861 635f 6379 656c 0073 0e02
0000070 6573 5f74 616d 5f78 7963 6c63 7365 0300
0000080 6719 7465 6e5f 6d75 6d5f 7861 635f 6379
0000090 656c 5f73 6863 6e75 736b 0400 800a 0502

00000a0 0153 7f03 0341 0110 0141 0121 4002 0441
00000b0 0110 0020 0141 0d48 4100 1005 4101 2101
00000c0 4103 2100 0302 4140 100d 2001 2002 6a03
00000d0 0121 0320 0221 0120 0321 0020 7f41 226a
00000e0 0d00 4100 1001 0b01 0141 0110 410b 1002
00000f0 2001 0b01 0151 7f01 0023 0121 0023 0020
0000100 246b 2300 2000 4b01 4004 0123 0121 0123
0000110 0141 246b 2301 2001 4b01 4004 0223 0121
0000120 0223 0141 246b 2302 2002 4b01 4004 0323
0000130 0121 0323 0141 246b 2303 2003 4b01 4004
0000140 0b00 0b0b 0b0b 0025 0020 0041 0446 237f
0000150 0500 0020 0141 0446 237f 0501 0020 0241
0000160 0446 237f 0502 0323 0b0b 0b0b 002d 0020
0000170 0041 0446 2040 2401 0500 0020 0141 0446
0000180 2040 2401 0501 0020 0241 0446 2040 2401
0000190 0502 0120 0324 0b0b 0b0b 0004 0441 000b
000019f






0000090 656c 5f73 6863 6e75 736b 0400 f90a 0501
0000090 656c 5f73 6863 6e75 736b 0400 800a 0502

00000a0 0153 7f03 0341 0110 0141 0121 4002 0441
00000a0 0153 7f03 0341 0110 0141 0121 4002 0441

00000b0 0110 0020 0141 0d48 4100 1005 4101 2101
00000b0 0110 0020 0141 0d48 4100 1005 4101 2101

00000c0 4103 2100 0302 4140 100d 2001 2002 6a03
00000c0 4103 2100 0302 4140 100d 2001 2002 6a03

00000d0 0121 0320 0221 0120 0321 0020 7f41 226a
00000d0 0121 0320 0221 0120 0321 0020 7f41 226a

00000e0 0d00 4100 1001 0b01 0141 0110 410b 1002
00000e0 0d00 4100 1001 0b01 0141 0110 410b 1002

00000f0 2001 0b01 014d 7f01 0023 0121 0023 0020
00000f0 2001 0b01 0151 7f01 0023 0121 0023 0020

                       ____
0000100 246b 2300 2000 4b01 2304 2101 2301 4101
0000100 246b 2300 2000 4b01 4004 0123 0121 0123

0000110 6b01 0124 0123 0120 044b 0223 0121 0223
0000110 0141 246b 2301 2001 4b01 4004 0223 0121

0000120 0141 246b 2302 2002 4b01 2304 2103 2301
0000120 0223 0141 246b 2302 2002 4b01 4004 0323

0000130 4103 6b01 0324 0323 0120 044b 0b00 0b0b
0000130 0121 0323 0141 246b 2303 2003 4b01 4004

0000140 0b0b 0025 0020 0041 0446 237f 0500 0020
0000140 0b00 0b0b 0b0b 0025 0020 0041 0446 237f

0000150 0141 0446 237f 0501 0020 0241 0446 237f
0000150 0500 0020 0141 0446 237f 0501 0020 0241

0000160 0502 0323 0b0b 0b0b 002a 0020 0041 0446
0000160 0446 237f 0502 0323 0b0b 0b0b 002d 0020

0000170 0120 0024 2005 4100 4601 2004 2401 0501
0000170 0041 0446 2040 2401 0500 0020 0141 0446

0000180 0020 0241 0446 0120 0224 2005 2401 0b03
0000180 2040 2401 0501 0020 0241 0446 2040 2401

0000190 0b0b 040b 4100 0b04                    
0000190 0502 0120 0324 0b0b 0b0b 0004 0441 000b

user@user:~/mnt/ethereum/repos/pywebassembly/poemm-pywebassembly/examples$ hexdump fibonacci_metered.wasm_orig 
"""





#cost of each intstruction
instr_cost = {
'unreachable':1,'nop':1,
'block':1, 'loop':1, 'if':1, 'else':1, 'end':1,
'br':1, 'br_if':1, 'br_table':1,
'return':1, 'call':1, 'call_indirect':1,

'drop':1,'select':1,

'get_local':1, 'set_local':1, 'tee_local':1, 'get_global':1, 'set_global':1,

'i32.load':1, 'i64.load':1, 'f32.load':1, 'f64.load':1, 'i32.load8_s':1, 'i32.load8_u':1, 'i32.load16_s':1, 'i32.load16_u':1, 'i64.load8_s':1, 'i64.load8_u':1, 'i64.load16_s':1, 'i64.load16_u':1, 'i64.load32_s':1, 'i64.load32_u':1, 'i32.store':1, 'i64.store':1, 'f32.store':1, 'f64.store':1, 'i32.store8':1, 'i32.store16':1, 'i64.store8':1, 'i64.store16':1, 'i64.store32':1,
'current_memory':1,'grow_memory':1,

'i32.const':1, 'i64.const':1, 'f32.const':1, 'f64.const':1,

'i32.eqz':1, 'i32.eq':1, 'i32.ne':1, 'i32.lt_s':1, 'i32.lt_u':1, 'i32.gt_s':1, 'i32.gt_u':1, 'i32.le_s':1, 'i32.le_u':1, 'i32.ge_s':1, 'i32.ge_u':1,

'i64.eqz':1, 'i64.eq':1, 'i64.ne':1, 'i64.lt_s':1, 'i64.lt_u':1, 'i64.gt_s':1, 'i64.gt_u':1, 'i64.le_s':1, 'i64.le_u':1, 'i64.ge_s':1, 'i64.ge_u':1,

'f32.eq':1, 'f32.ne':1, 'f32.lt':1, 'f32.gt':1, 'f32.le':1, 'f32.ge':1,

'f64.eq':1, 'f64.ne':1, 'f64.lt':1, 'f64.gt':1, 'f64.le':1, 'f64.ge':1,

'i32.clz':1, 'i32.ctz':1, 'i32.popcnt':1, 'i32.add':1, 'i32.sub':1, 'i32.mul':1, 'i32.div_s':1, 'i32.div_u':1, 'i32.rem_s':1, 'i32.rem_u':1, 'i32.and':1, 'i32.or':1, 'i32.xor':1, 'i32.shl':1, 'i32.shr_s':1, 'i32.shr_u':1, 'i32.rotl':1, 'i32.rotr':1,

'i64.clz':1, 'i64.ctz':1, 'i64.popcnt':1, 'i64.add':1, 'i64.sub':1, 'i64.mul':1, 'i64.div_s':1, 'i64.div_u':1, 'i64.rem_s':1, 'i64.rem_u':1, 'i64.and':1, 'i64.or':1, 'i64.xor':1, 'i64.shl':1, 'i64.shr_s':1, 'i64.shr_u':1, 'i64.rotl':1, 'i64.rotr':1,

'f32.abs':1, 'f32.neg':1, 'f32.ceil':1, 'f32.floor':1, 'f32.trunc':1, 'f32.nearest':1, 'f32.sqrt':1, 'f32.add':1, 'f32.sub':1, 'f32.mul':1, 'f32.div':1, 'f32.min':1, 'f32.max':1, 'f32.copysign':1, 'f64.abs':1,

'f64.neg':1, 'f32.min':1, 'f32.max':1, 'f32.copysign':1, 'f64.abs':1, 'f64.neg':1, 'f64.ceil':1, 'f64.floor':1, 'f64.trunc':1, 'f64.nearest':1, 'f64.sqrt':1, 'f64.add':1, 'f64.sub':1, 'f64.mul':1, 'f64.div':1, 'f64.min':1, 'f64.max':1, 'f64.copysign':1,

'i32.wrap/i64':1, 'i32.trunc_s/f32':1, 'i32.trunc_u/f32':1, 'i32.trunc_s/f64':1, 'i32.trunc_u/f64':1, 'i64.extend_s/i32':1, 'i64.extend_u/i32':1, 'i64.trunc_s/f32':1, 'i64.trunc_u/f32':1, 'i64.trunc_s/f64':1, 'i64.trunc_u/f64':1, 'f32.convert_s/i32':1, 'f32.convert_u/i32':1, 'f32.convert_s/i64':1, 'f32.convert_u/i64':1, 'f32.demote/f64':1, 'f64.convert_s/i32':1, 'f64.convert_u/i32':1, 'f64.convert_s/i64':1, 'f64.convert_u/i64':1, 'f64.promote/f32':1, 'i32.reinterpret/f32':1, 'i64.reinterpret/f64':1, 'f32.reinterpret/i32':1, 'f64.reinterpret/i64':1
}




def inject_metering_calls_to_each_function(mod):
  for f in mod["funcs"]:
    #for e in f["body"]:
    f["body"]=inject_metering_expr(f["body"],len(mod["funcs"])) #len(mod["funcs"]) is idx of metering func in wasm



#THIS IS THE IMPORTANT FUNCTION; RECURSIVELY INJECTS METERING CALLS
def inject_metering_expr(expr,meteringFuncIdx):
  #inject to beginning of list
  #expr=[("i32.const",0),("call",meteringFuncIdx)]+expr
  cost=0
  #cost_instr=expr[0]
  idx_to_inject=0
  i=0
  #print(expr)
  while i<len(expr):
    #print(i,expr[i][0],expr[i])
    cost+=instr_cost[expr[i][0]]
    if expr[i][0] in {"block","if","loop","br","br_if","br_table"}:
      #cost_instr[1]=cost
      #inject
      if cost !=0:
        #print("injecting  i:",i,"idx_to_inject",idx_to_inject)
        expr=expr[:idx_to_inject]+[["i32.const",cost],["call",meteringFuncIdx]]+expr[idx_to_inject:]
        idx_to_inject=i+3
        cost=0
        i+=2
      #recurse on nested exprs
      if expr[i][0] in {"block","if","loop"}:
        expr[i][2][:]=inject_metering_expr(expr[i][2],meteringFuncIdx)
      #if not end, inject another
      #if i<len(expr)-1:
      #  cost=0
      #  expr=expr[:i+1]+[("i32.const",0),("call",meteringFuncIdx)]+expr[i+1:]
      #  cost_instr=expr[i]
    i+=1
  if cost !=0:
    expr=expr[:idx_to_inject]+[["i32.const",cost],["call",meteringFuncIdx]]+expr[idx_to_inject:]
  return expr



def inject_helper_functions(mod):
  #inject globals for cycles_remaining
  global_idx_cycles = len(mod["globals"])
  mod["globals"]+=[{'type': ['var', 'i32'], 'init': [['i32.const', 0],["end"]]},
                   {'type': ['var', 'i32'], 'init': [['i32.const', 0],["end"]]},
                   {'type': ['var', 'i32'], 'init': [['i32.const', 0],["end"]]},
                   {'type': ['var', 'i32'], 'init': [['i32.const', 0],["end"]]}]
  #inject function to perform metering
  mod["types"]+=[[['i32'],[]]]
  mod["funcs"]+=[{'type': len(mod["types"])-1, 'locals': ['i32'],
      'body': [['get_global', 0+global_idx_cycles],
               ['set_local', 1],
               ['get_global', 0+global_idx_cycles],
               ['get_local', 0],
               ['i32.sub'],
               ['set_global', 0+global_idx_cycles],
               ['get_global', 0+global_idx_cycles],
               ['get_local', 1],
               ['i32.gt_u'],
               ['if', [],
                [
                 ['get_global', 1+global_idx_cycles],
                 ['set_local', 1],
                 ['get_global', 1+global_idx_cycles],
                 ['i32.const', 1],
                 ['i32.sub'],
                 ['set_global', 1+global_idx_cycles],
                 ['get_global', 1+global_idx_cycles],
                 ['get_local', 1],
                 ['i32.gt_u'],
                 ['if', [],
                  [
                   ['get_global', 2+global_idx_cycles],
                   ['set_local', 1],
                   ['get_global', 2+global_idx_cycles],
                   ['i32.const', 1],
                   ['i32.sub'],
                   ['set_global', 2+global_idx_cycles],
                   ['get_global', 2+global_idx_cycles],
                   ['get_local', 1],
                   ['i32.gt_u'],
                   ['if', [],
                    [
                     ['get_global', 3+global_idx_cycles],
                     ['set_local', 1],
                     ['get_global', 3+global_idx_cycles],
                     ['i32.const', 1],
                     ['i32.sub'],
                     ['set_global', 3+global_idx_cycles],
                     ['get_global', 3+global_idx_cycles],
                     ['get_local', 1],
                     ['i32.gt_u'],
                     ['if', [],
                      [
                       ['unreachable'],
                       ['end']
                      ]
                     ],
                     ['end']
                    ]
                   ],
                   ['end']
                  ]
                 ],
                 ['end']
                ]
               ],
               ['end']
              ]
            }]
  """
  (func (;1;) (type 1) (param i32)
    (local i32)
    get_global 0
    set_local 1
    get_global 0
    get_local 0
    i32.sub
    set_global 0
    get_global 0
    get_local 1
    i32.gt_u
    if  ;; label = @1
      get_global 1
      set_local 1
      get_global 1
      i32.const 1
      i32.sub
      set_global 1
      get_global 1
      get_local 1
      i32.gt_u
      if  ;; label = @2
        get_global 2
        set_local 1
        get_global 2
        i32.const 1
        i32.sub
        set_global 2
        get_global 2
        get_local 1
        i32.gt_u
        if  ;; label = @3
          get_global 3
          set_local 1
          get_global 3
          i32.const 1
          i32.sub
          set_global 3
          get_global 3
          get_local 1
          i32.gt_u
          if  ;; label = @4
            unreachable
          end
        end
      end
    end)
  """
  #inject function to get cycles remaining
  #print_tree_expr(mod["funcs"][-1]["body"])
  mod["types"]+=[[['i32'], ['i32']]]
  mod["funcs"]+=[{'type': len(mod["types"])-1, 'locals': [],
        'body': [['get_local', 0],
                 ['i32.const', 0],
                 ['i32.eq'],
                 ['if', 'i32',
                  [
                   ['get_global', 0+global_idx_cycles],
                   ['else']
                  ],
                  [
                   ['get_local', 0],
                   ['i32.const', 1],
                   ['i32.eq'],
                   ['if', 'i32',
                    [
                     ['get_global', 1+global_idx_cycles],
                     ['else']
                    ],
                    [
                     ['get_local', 0],
                     ['i32.const', 2],
                     ['i32.eq'],
                     ['if', 'i32',
                      [
                       ['get_global', 2+global_idx_cycles],
                       ['else']
                      ],
                      [
                       ['get_global', 3+global_idx_cycles],
                       ['end']
                      ]
                     ],
                     ['end']
                    ]
                   ],
                   ['end']
                  ]
                 ],
                 ['end']
                ]
              }]
  #print("added func:")
  #print(mod["funcs"][-1]["body"])
  mod["exports"]+=[{'name': 'get_max_cycles', 'desc': ['func', len(mod["funcs"])-1]}]
  """
  (func (;2;) (type 2) (param i32) (result i32)
    get_local 0
    i32.const 0
    i32.eq
    if (result i32)  ;; label = @1
      get_global 0
    else
      get_local 0
      i32.const 1
      i32.eq
      if (result i32)  ;; label = @2
        get_global 1
      else
        get_local 0
        i32.const 2
        i32.eq
        if (result i32)  ;; label = @3
          get_global 2
        else
          get_global 3
        end
      end
    end)
  """
  #inject function to set max_cycles
  mod["types"]+=[[['i32','i32'],[]]]
  mod["funcs"]+=[{'type': len(mod["types"])-1, 'locals': [],
        'body': [['get_local', 0],
                 ['i32.const', 0],
                 ['i32.eq',],
                 ['if', [],
                  [
                   ['get_local', 1],
                   ['set_global', 0+global_idx_cycles],
                   ['else',]
                  ],
                  [
                   ['get_local', 0],
                   ['i32.const', 1],
                   ['i32.eq',],
                   ['if', [],
                    [
                     ['get_local', 1],
                     ['set_global', 1+global_idx_cycles],
                     ['else',]
                    ],
                    [
                     ['get_local', 0],
                     ['i32.const', 2],
                     ['i32.eq',],
                     ['if', [],
                      [
                       ['get_local', 1],
                       ['set_global', 2+global_idx_cycles],
                       ['else',]
                      ],
                      [
                       ['get_local', 1],
                       ['set_global', 3+global_idx_cycles],
                       ['end',]
                      ]
                     ],
                     ['end',]
                    ]
                   ],
                   ['end',]
                  ]
                 ],
                 ['end',]
                ]
              }]
  mod["exports"]+=[{'name': 'set_max_cycles', 'desc': ['func', len(mod["funcs"])-1]}]
  """
  (func (;3;) (type 3) (param i32 i32)
    get_local 0
    i32.const 0
    i32.eq
    if  ;; label = @1
      get_local 1
      set_global 0
    else
      get_local 0
      i32.const 1
      i32.eq
      if  ;; label = @2
        get_local 1
        set_global 1
      else
        get_local 0
        i32.const 2
        i32.eq
        if  ;; label = @3
          get_local 1
          set_global 2
        else
          get_local 1
          set_global 3
        end
      end
    end)
  """
  #inject function to get num chunks for max_cycles
  mod["types"]+=[[[],['i32']]]
  mod["funcs"]+=[{'type': len(mod["types"])-1, 'locals': [], 'body': [['i32.const', 4],['end',]]}]
  mod["exports"]+=[{'name': 'get_num_max_cycles_chunks', 'desc': ['func', len(mod["funcs"])-1]}]
  """
  (func (;4;) (type 4) (result i32)
    i32.const 4)
  """
  #print(mod["types"])
  #print(mod["funcs"])
  #print(mod["exports"])





def tests(mod):
  #print_tree(mod)
  #print_sections(mod)
  #print_tree(mod["funcs"])
  #print_sections(mod)
  #test metering injection to each func
  for f in mod["funcs"]:
    #print("\n")
    #pretty_print(f["body"])
    #print(f["body"])
    #print_tree_expr(f["body"])
    f["body"]=inject_metering_expr(f["body"],1000)
    #print()
    #print_tree_expr(f["body"])




def parse_wasm_and_inject_and_generate(filename):
  with open(filename, 'rb') as f:
    bytecode = memoryview(f.read())
    mod = wasm.decode_module(bytecode)
    inject_metering_calls_to_each_function(mod)
    #must inject above metering calls before injecting helper functions
    inject_helper_functions(mod)
    #print_sections(mod)
    fout = open(filename.split('.')[0]+"_metered.wasm", 'wb')
    bytecode_out = wasm.encode_module(mod)
    fout.write(bytecode_out)
    fout.close()


if __name__ == "__main__":
  import sys
  if len(sys.argv)!=2:
    print("Argument should be <filename>.wasm")
  else:
    parse_wasm_and_inject_and_generate(sys.argv[1])
