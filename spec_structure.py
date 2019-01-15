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

verbose = 0

###############
###############
# 2 STRUCTURE #
###############
###############

#Chapter 2 defines the abstract syntax, which is used throughout the implementation. Not much is needed from this section, since most abstrct syntax is nested lists and dictionaries

# 2.2.3 FLOATING-POINT

# functions in this sectio are not currently used since we decided to use native Python floats, and struct.pack()/unpack() to encode/decode, but we may use these later to pass the rest of the NaN tests

def spec_fN(N,f):
  fNmag = spec_fNmag(N,f)
  if f>=0:
    return fNmag
  else:
    return -1*fNmag

def spec_fNmag(N,f):
  M=spec_signif(N)
  E=spec_expon(N)
  e=bitstring[1:E+1]
  m=bitstring[E+1:]
  if -1*(2**(E-1)) + 2 <= e <= 2**(E-1)-1:
    pass

def spec_signif(N):
  if verbose>=1: print("spec_signif(",N,")")
  if N==32:
    return 23
  elif N==64:
    return 52
  else:
    return None

def spec_signif_inv(signif):
  if verbose>=1: print("spec_signif_inv(",signif,")")
  if signif == 23:
    return 32
  elif signif == 52:
    return 64
  else:
    return None

def spec_expon(N):
  if verbose>=1: print("spec_expon(",N,")")
  if N==32:
    return 8
  elif N==64:
    return 11
  else:
    return None

def spec_expon_inv(expon):
  if verbose>=1: print("spec_expon_inv(",expon,")")
  if expon == 8:
    return 32
  elif expon == 11:
    return 64
  else:
    return None


# 2.3.8 EXTERNAL TYPES

#similar things are defined in 2.5.10 and 4.2.11, we will reuse these for those

def spec_funcs(star):
  funcs = []
  for e in star:
    if e[0] == 'func':
      funcs += [e[1]]
  return funcs

def spec_tables(star):
  tables = []
  for e in star:
    if e[0] == 'table':
      tables += [e[1]]
  return tables

def spec_mems(star):
  mems = []
  for e in star:
    if e[0] == 'mem':
      mems += [e[1]]
  return mems

def spec_globals(star):
  globals_ = []
  for e in star:
    if e[0] == 'global':
      globals_ += [e[1]]
  return globals_


