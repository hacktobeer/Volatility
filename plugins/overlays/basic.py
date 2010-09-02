# Volatility
#
# Authors:
# Michael Cohen <scudette@users.sourceforge.net>
# Mike Auty <mike.auty@gmail.com>
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

""" This file defines some basic types which might be useful for many
OS's
"""
# FIXME: It's currently important these are imported here, otherwise
# they don't show up in the MemoryObjects registry
from volatility.obj import BitField, Pointer, Void, Array, CType #pylint: disable-msg=W0611
import volatility.obj as obj
import volatility.debug as debug #pylint: disable-msg=W0611
import volatility.constants as constants

class String(obj.NativeType):
    """Class for dealing with Strings"""
    def __init__(self, theType, offset, vm = None,
                 length = 1, parent = None, profile = None, name = None, **args):
        ## Allow length to be a callable:
        try:
            length = length(parent)
        except TypeError:
            pass

        ## length must be an integer
        obj.NativeType.__init__(self, theType, offset, vm, parent = parent, profile = profile,
                            name = name, format_string = "{0}s".format(length))

    def proxied(self, name):
        """ Return an object to be proxied """
        return self.__str__()

    def __str__(self):
        data = self.v()
        ## Make sure its null terminated:
        result = data.split("\x00")[0]
        if not result:
            return ""
        return result

    def __format__(self, formatspec):
        return format(self.__str__(), formatspec)

    def __add__(self, other):
        """Set up mappings for concat"""
        return str(self) + other

    def __radd__(self, other):
        """Set up mappings for reverse concat"""
        return other + str(self)

class Flags(obj.NativeType):
    """ This object decodes each flag into a string """
    ## This dictionary maps each bit to a String
    bitmap = {}

    ## This dictionary maps a string mask name to a bit range
    ## consisting of a list of start, width bits
    maskmap = {}

    def __init__(self, theType = None, offset = 0, vm = None, parent = None,
                 bitmap = None, name = None, maskmap = None, target = "unsigned long",
                 **args):
        if bitmap:
            self.bitmap = bitmap

        if maskmap:
            self.maskmap = maskmap

        self.target = obj.Object(target, offset = offset, vm = vm, parent = parent)
        obj.NativeType.__init__(self, theType, offset, vm, parent, **args)

    def v(self):
        return self.target.v()

    def __str__(self):
        result = []
        value = self.v()
        keys = self.bitmap.keys()
        keys.sort()
        for k in keys:
            if value & (1 << self.bitmap[k]):
                result.append(k)

        return ', '.join(result)

    def __format__(self, formatspec):
        return format(self.__str__(), formatspec)

    def __getattr__(self, attr):
        maprange = self.maskmap.get(attr)
        if not maprange:
            return obj.NoneObject("Mask {0} not known".format(attr))

        bits = 2 ** maprange[1] - 1
        mask = bits << maprange[0]

        return self.v() & mask

class Enumeration(obj.NativeType):
    """Enumeration class for handling multiple possible meanings for a single value"""

    def __init__(self, theType = None, offset = 0, vm = None, parent = None,
                 choices = None, name = None, target = "unsigned long",
                 **args):
        self.choices = {}
        if choices:
            self.choices = choices

        self.target = obj.Object(target, offset = offset, vm = vm, parent = parent)
        obj.NativeType.__init__(self, theType, offset, vm, parent, **args)

    def v(self):
        return self.target.v()

    def __str__(self):
        value = self.v()
        if value in self.choices.keys():
            return self.choices[value]
        return 'Unknown choice ' + str(value)

    def __format__(self, formatspec):
        return format(self.__str__(), formatspec)

class VolatilityMagic(obj.BaseObject):
    """Class to contain Volatility Magic value"""

    def __init__(self, theType, offset, vm, parent = None, value = None, name = None):
        try:
            obj.BaseObject.__init__(self, theType, offset, vm, parent, name)
        except obj.InvalidOffsetError:
            pass
        self.value = value

    def v(self):
        # We explicitly want to check for None,
        # in case the user wants a value 
        # that gives not self.value = True
        if self.value is None:
            return self.get_best_suggestion()
        else:
            return self.value

    def __str__(self):
        return self.v()

    def get_suggestions(self):
        """Returns a list of possible suggestions for the value
        
           These should be returned in order of likelihood, 
           since the first one will be taken as the best suggestion
           
           This is also to avoid a complete scan of the memory address space,
           since 
        """
        yield self.v()


    def get_best_suggestion(self):
        """Returns the best suggestion for a list of possible suggestsions"""
        for val in self.get_suggestions():
            return val
        else:
            return obj.NoneObject("No suggestions available")

class VOLATILITY_MAGIC(obj.CType):
    """Class representing a VOLATILITY_MAGIC namespace
    
       Needed to ensure that the address space is not verified as valid for constants
    """
    def __init__(self, theType, offset, vm, parent = None, members = None, name = None, size = 0):
        try:
            obj.CType.__init__(self, theType, offset, vm, parent = parent, members = members, name = name, size = size)
        except obj.InvalidOffsetError:
            # The exception will be raised before this point,
            # so we must finish off the CType's __init__ ourselves
            self.__initialized = True

class VolatilityDTB(VolatilityMagic):

    def get_suggestions(self):
        offset = 0
        while 1:
            data = self.vm.read(offset, constants.SCAN_BLOCKSIZE)
            found = 0
            if not data:
                break

            while 1:
                found = data.find(str(self.parent.DTBSignature), found + 1)
                if found >= 0:
                    # (_type, _size) = unpack('=HH', data[found:found+4])
                    proc = obj.Object("_EPROCESS",
                                             offset = offset + found,
                                             vm = self.vm)
                    if 'Idle' in proc.ImageFileName.v():
                        yield proc.Pcb.DirectoryTableBase.v()
                else:
                    break

            offset += len(data)

