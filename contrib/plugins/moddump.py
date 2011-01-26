# Volatility
# Copyright (C) 2007,2008 Volatile Systems
# Copyright (c) 2008 Brendan Dolan-Gavitt <bdolangavitt@wesleyan.edu>
#
# Additional Authors:
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

import os
import re
import volatility.plugins.procdump as procdump
import volatility.win32.modules as modules
import volatility.win32.tasks as tasks
import volatility.utils as utils
import volatility.debug as debug

class ModDump(procdump.ProcExeDump):
    """Dump a kernel driver to an executable file sample"""

    def __init__(self, config, *args):
        procdump.ProcExeDump.__init__(self, config, *args)
        config.remove_option("PID")
        config.remove_option("OFFSET")
        config.add_option('REGEX', short_option = 'r',
                      help = 'Dump modules matching REGEX',
                      action = 'store', type = 'string', dest = 'regex')
        config.add_option('IGNORE-CASE', short_option = 'i',
                      help = 'Ignore case in pattern match',
                      action = 'store_true', default = False, dest = 'ignore_case')
        config.add_option('OFFSET', short_option = 'o', default = None,
                          help = 'Dump driver with base address OFFSET (in hex)',
                          action = 'store', type = 'int')

    def find_space(self, addr_space, procs, mod_base):
        """Search for an address space (usually looking for a GUI process)"""
        if addr_space.is_valid_address(mod_base):
            return addr_space
        for proc in procs:
            ps_ad = proc.get_process_address_space()
            if ps_ad != None:
                if ps_ad.is_valid_address(mod_base):
                    return ps_ad
        return None

    def calculate(self):
        addr_space = utils.load_as(self._config)

        if self._config.DUMP_DIR == None:
            debug.error("Please specify a dump directory (--dump-dir)")
        if not os.path.isdir(self._config.DUMP_DIR):
            debug.error(self._config.DUMP_DIR + " is not a directory")

        if self._config.regex:
            try:
                if self._config.ignore_case:
                    mod_re = re.compile(self._config.regex, re.I)
                else:
                    mod_re = re.compile(self._config.regex)
            except re.error, e:
                debug.error('Error parsing regular expression: %s' % e)

        mods = dict((mod.DllBase.v(), mod) for mod in modules.lsmod(addr_space))
        # We need the process list to find spaces for some drivers. Enumerate them here
        # instead of inside the find_space function, so we only have to do it once. 
        procs = list(tasks.pslist(addr_space))

        if self._config.OFFSET:
            if mods.has_key(self._config.OFFSET):
                yield addr_space, procs, mods[self._config.OFFSET]
            else:
                raise StopIteration('No such module at 0x{0:X}'.format(self._config.OFFSET))
        else:
            for mod in mods.values():
                if self._config.regex:
                    if not mod_re.search(str(mod.FullDllName)) and not mod_re.search(str(mod.BaseDllName)):
                        continue
                yield addr_space, procs, mod

    def render_text(self, outfd, data):
        for addr_space, procs, mod in data:
            space = self.find_space(addr_space, procs, mod.DllBase)
            if space != None:
                dump_file = "driver.{0:x}.sys".format(mod.DllBase)
                outfd.write("Dumping {0}, Base: {1:8x} output: {2}\n".format(mod.BaseDllName, mod.DllBase, dump_file))
                of = open(os.path.join(self._config.DUMP_DIR, dump_file), 'wb')
                try:
                    for chunk in self.get_image(outfd, space, mod.DllBase):
                        offset, code = chunk
                        of.seek(offset)
                        of.write(code)
                except ValueError, ve:
                    outfd.write("Unable to dump executable; sanity check failed:\n")
                    outfd.write("  " + str(ve) + "\n")
                    outfd.write("You can use -u to disable this check.\n")
                of.close()
            else:
                print 'Cannot dump {0} at {1:8x}'.format(mod.BaseDllName, mod.DllBase)