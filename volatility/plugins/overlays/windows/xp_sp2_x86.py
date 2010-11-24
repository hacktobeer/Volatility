# Volatility
# Copyright (c) 2008 Volatile Systems
# Copyright (c) 2008 Brendan Dolan-Gavitt <bdolangavitt@wesleyan.edu>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details. 
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA 
#

"""
@author:       Brendan Dolan-Gavitt
@license:      GNU General Public License 2.0 or later
@contact:      bdolangavitt@wesleyan.edu

This file provides support for windows XP SP2. We provide a profile
for SP2.
"""

#pylint: disable-msg=C0111

import windows as windows
import xp_sp2_x86_vtypes as xp_sp2_x86_vtypes
import volatility.obj as obj
import volatility.debug as debug #pylint: disable-msg=W0611

# Standard vtypes are usually autogenerated by scanning through header
# files, collecting debugging symbol data etc. This file defines
# fixups and improvements to the standard types.
xpsp2overlays = {
    'VOLATILITY_MAGIC' : [None, { \
    'DTB' : [ 0x0, ['VolatilityDTB', dict(configname = "DTB")]],
    'DTBSignature' : [ 0x0, ['VolatilityMagic', dict(value = "\x03\x00\x1b\x00")]],
    'KPCR' : [ 0x0, ['VolatilityMagic', dict(value = 0xffdff000, configname = "KPCR")]],
    'KUSER_SHARED_DATA' : [ 0x0, ['VolatilityMagic', dict(value = 0xFFDF0000)]],
    }],

    '_EPROCESS' : [ None, { \
    'CreateTime' : [ None, ['WinTimeStamp', {}]],
    'ExitTime' : [ None, ['WinTimeStamp', {}]],
    'InheritedFromUniqueProcessId' : [ None, ['unsigned int']],
    'ImageFileName' : [ None, ['String', dict(length = 16)]],
    'UniqueProcessId' : [ None, ['unsigned int']], \
    'VadRoot': [ None, ['pointer', ['_MMVAD']]], \
    }],

    '_KUSER_SHARED_DATA' : [ None, { \
    'SystemTime' : [ None, ['WinTimeStamp', {}]], \
    'TimeZoneBias' : [ None, ['WinTimeStamp', {}]], \
    }],

    '_ADDRESS_OBJECT' : [ None, { \
    'LocalPort': [ None, ['unsigned be short']], \
    'CreateTime' : [ None, ['WinTimeStamp', {}]], \
    }],

    '_OBJECT_HEADER' : [ None, {
    'Body' : [ None, ['unsigned int']],
    }],

    '_KDDEBUGGER_DATA64' : [ None, {
    'PsActiveProcessHead' : [ None, ['pointer', ['unsigned long']]], \
    }],

    '_DBGKD_GET_VERSION64' : [  None, {
    'DebuggerDataList' : [ None, ['pointer', ['unsigned long']]], \
    }],

    '_DMP_HEADER' : [ None, {
    'PsActiveProcessHead' : [ None, ['pointer' , ['unsigned long']]], \
    }],

    '_CM_KEY_NODE' : [ None, {
    'Signature' : [ None, ['String', dict(length = 2)]],
    'LastWriteTime' : [ None, ['WinTimeStamp', {}]],
    'Name' : [ None, ['String', dict(length = lambda x: x.NameLength)]],
    }],

    '_CHILD_LIST' : [ None, {
    'List' : [ None, ['pointer', ['array', lambda x: x.Count,
                                 ['pointer', ['_CM_KEY_VALUE']]]]],
    }],

    '_CM_KEY_VALUE' : [ None, {
    'Signature' : [ None, ['String', dict(length = 2)]],
    'Name' : [ None, ['String', dict(length = lambda x: x.NameLength)]],
    } ],

    '_CM_KEY_INDEX' : [ None, {
    'Signature' : [ None, ['String', dict(length = 2)]],
    'List' : [ None, ['array', lambda x: x.Count.v() * 2, ['pointer', ['_CM_KEY_NODE']]]],
    } ],

    '_IMAGE_HIBER_HEADER' : [ None, { \
    'Signature':   [ None, ['String', dict(length = 4)]],
    'SystemTime' : [ None, ['WinTimeStamp', {}]], \
    } ], \

    '_PHYSICAL_MEMORY_DESCRIPTOR' : [ None, { \
    'Run' : [ None, ['array', lambda x: x.NumberOfRuns, ['_PHYSICAL_MEMORY_RUN']]], \
    } ], \

    ## This is different between Windows 2000 and WinXP. This overlay
    ## is for xp.
    '_POOL_HEADER' : [ None, { \
    'PoolIndex': [ 0x0, ['BitField', dict(start_bit = 9, end_bit = 16)]],
    'BlockSize': [ 0x2, ['BitField', dict(start_bit = 0, end_bit = 9)]],
    'PoolType': [ 0x2, [ 'BitField', dict(start_bit = 9, end_bit = 16)]],
    } ], \

    '_TCPT_OBJECT': [ None, {
    'RemotePort': [ None, [ 'unsigned be short']],
    'LocalPort': [ None, [ 'unsigned be short']],
    } ],
    '_CLIENT_ID': [ None, {
    'UniqueProcess' : [ None, ['unsigned int']], \
    'UniqueThread' : [ None, ['unsigned int']], \
    } ],

    '_CONTROL_AREA': [ None, {
    'Flags': [ None, ['Flags',
                      {'bitmap': {
    'BeingDeleted' : 0x0,
    'BeingCreated' : 0x1,
    'BeingPurged'  : 0x2,
    'NoModifiedWriting' :  0x3,
    'FailAllIo' : 0x4,
    'Image' : 0x5,
    'Based' : 0x6,
    'File'  : 0x7,
    'Networked' : 0x8,
    'NoCache' : 0x9,
    'PhysicalMemory' : 0xa,
    'CopyOnWrite' : 0xb,
    'Reserve' : 0xc,
    'Commit' : 0xd,
    'FloppyMedia' : 0xe,
    'WasPurged' : 0xf,
    'UserReference' : 0x10,
    'GlobalMemory' : 0x11,
    'DeleteOnClose' : 0x12,
    'FilePointerNull' : 0x13,
    'DebugSymbolsLoaded' : 0x14,
    'SetMappedFileIoComplete' : 0x15,
    'CollidedFlush' : 0x16,
    'NoChange' : 0x17,
    'HadUserReference' : 0x18,
    'ImageMappedInSystemSpace' : 0x19,
    'UserWritable' : 0x1a,
    'Accessed' : 0x1b,
    'GlobalOnlyPerSession' : 0x1c,
    'Rom' : 0x1d,
    },
                       }
                      ]
               ],
    } ]
}


xpsp2overlays['_MMVAD_SHORT'] = [ None, {
    'Flags': [ None, ['Flags',
  {'bitmap': {
    'PhysicalMapping': 0x13,
    'ImageMap': 0x14,
    'UserPhysicalPages': 0x15,
    'NoChange': 0x16,
    'WriteWatch': 0x17,
    'LargePages': 0x1D,
    'MemCommit': 0x1E,
    'PrivateMemory': 0x1f,
    },
  'maskmap': {
    'CommitCharge' : [0x0, 0x13],
    'Protection' : [0x18, 0x5],
    }
  } ] ],
    } ]

xpsp2overlays['_MMVAD_LONG'] = [ None, {
    'Flags': xpsp2overlays['_MMVAD_SHORT'][1]['Flags'],

    'Flags2': [ None, ['Flags',
  {'bitmap': {
    'SecNoChange' : 0x18,
    'OneSecured' : 0x19,
    'MultipleSecured' : 0x1a,
    'ReadOnly' : 0x1b,
    'LongVad' : 0x1c,
    'ExtendableFile' : 0x1d,
    'Inherit' : 0x1e,
    'CopyOnWrite' : 0x1f,
    },
  'maskmap': {
    'FileOffset' : [0x0, 0x18],
    }
  } ] ],
    } ]

class WinXPSP2(windows.AbstractWindows):
    """ A Profile for Windows XP SP2 """
    abstract_types = xp_sp2_x86_vtypes.xpsp2types
    overlay = xpsp2overlays

class _EPROCESS(obj.CType):
    """ An extensive _EPROCESS with bells and whistles """
    def _Peb(self, _attr):
        """ Returns a _PEB object which is using the process address space.

        The PEB structure is referencing back into the process address
        space so we need to switch address spaces when we look at
        it. This method ensure this happens automatically.
        """
        process_ad = self.get_process_address_space()
        if process_ad:
            offset = self.m("Peb").v()
            peb = obj.Object("_PEB", offset, vm = process_ad,
                                    name = "Peb", parent = self)

            if peb.is_valid():
                return peb

        return obj.NoneObject("Peb not found")

    def get_process_address_space(self):
        """ Gets a process address space for a task given in _EPROCESS """
        directory_table_base = self.Pcb.DirectoryTableBase.v()

        try:
            process_as = self.vm.__class__(self.vm.base, self.vm.get_config(), dtb = directory_table_base)
        except AssertionError, _e:
            return obj.NoneObject("Unable to get process AS")

        process_as.name = "Process {0}".format(self.UniqueProcessId)

        return process_as

    def _make_handle_array(self, offset, level):
        """ Returns an array of _HANDLE_TABLE_ENTRY rooted at offset,
        and iterates over them.

        """
        if level > 0:
            count = 0x400
            targetType = "unsigned int"
        else:
            count = 0x200
            targetType = "_HANDLE_TABLE_ENTRY"

        table = obj.Object("Array", offset = offset, vm = self.vm, count = count,
                           targetType = targetType, parent = self)

        if table:
            for entry in table:
                if not entry.is_valid():
                    break

                if level > 0:
                    ## We need to go deeper:
                    for h in self._make_handle_array(entry, level - 1):
                        yield h
                else:
                    ## OK We got to the bottom table, we just resolve
                    ## objects here:
                    offset = int(entry.Object.v()) & ~0x00000007
                    item = obj.Object("_OBJECT_HEADER", offset, self.vm,
                                            parent = self)
                    try:
                        if item.Type.Name:
                            yield item

                    except AttributeError:
                        pass

    def handles(self):
        """ A generator which yields this process's handles

        _HANDLE_TABLE tables are multi-level tables at the first level
        they are pointers to second level table, which might be
        pointers to third level tables etc, until the final table
        contains the real _OBJECT_HEADER table.

        This generator iterates over all the handles recursively
        yielding all handles. We take care of recursing into the
        nested tables automatically.
        """
        h = self.ObjectTable
        if h.is_valid():
            TableCode = h.TableCode.v() & LEVEL_MASK
            table_levels = h.TableCode.v() & ~LEVEL_MASK
            offset = TableCode

            for h in self._make_handle_array(offset, table_levels):
                yield h

LEVEL_MASK = 0xfffffff8

windows.AbstractWindows.object_classes['_EPROCESS'] = _EPROCESS

## This is an object which provides access to the VAD tree.
class _MMVAD(obj.CType):
    ## parent is the containing _EPROCESS right now
    def __new__(cls, theType, offset, vm, parent, **args):
        ## Find the tag (4 bytes below the current offset). This can
        ## not have ourselves as a target.
        switch = {"Vadl": '_MMVAD_LONG',
                  'VadS': '_MMVAD_SHORT',
                  'Vad ': '_MMVAD_LONG',
                  'VadF': '_MMVAD_SHORT',
                  }

        ## All VADs are done in the process AS - so we might need to
        ## switch Address spaces now. We do this by instantiating an
        ## _EPROCESS over our parent, and having it give us the
        ## correct AS
        if vm.name.startswith("Kernel"):
            eprocess = obj.Object("_EPROCESS", offset = parent.v_offset, vm = vm)
            vm = eprocess.get_process_address_space()
            if not vm:
                return vm

        ## What type is this struct?
        tag = vm.read(offset - 4, 4)
        theType = switch.get(tag)

        if not theType:
            return obj.NoneObject("Tag {0} not knowns".format(tag))

        ## Note that since we were called from __new__ we can return a
        ## completely different object here (including
        ## NoneObject). This also means that we can not add any
        ## specialist methods to the _MMVAD class.
        result = obj.Object(theType, offset = offset, vm = vm, parent = parent, **args)
        result.newattr('Tag', tag)

        return result

windows.AbstractWindows.object_classes['_MMVAD'] = _MMVAD

class _MMVAD_SHORT(obj.CType):
    def traverse(self, visited = None):
        """ Traverse the VAD tree by generating all the left items,
        then the right items.

        We try to be tolerant of cycles by storing all offsets visited.
        """
        if visited == None:
            visited = set()

        ## We try to prevent loops here
        if self.v_offset in visited:
            return

        yield self

        for c in self.LeftChild.traverse(visited = visited):
            visited.add(c.v_offset)
            yield c

        for c in self.RightChild.traverse(visited = visited):
            visited.add(c.v_offset)
            yield c

class _MMVAD_LONG(_MMVAD_SHORT):
    pass

windows.AbstractWindows.object_classes['_MMVAD_SHORT'] = _MMVAD_SHORT
windows.AbstractWindows.object_classes['_MMVAD_LONG'] = _MMVAD_LONG
