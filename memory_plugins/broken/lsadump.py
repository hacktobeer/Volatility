# Volatility
# Copyright (C) 2008 Volatile Systems
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
@author:       AAron Walters and Brendan Dolan-Gavitt
@license:      GNU General Public License 2.0 or later
@contact:      awalters@volatilesystems.com,bdolangavitt@wesleyan.edu
@organization: Volatile Systems
"""

#pylint: disable-msg=C0111

import sys
import forensics.win32.lsasecrets as lsasecrets
import forensics.win32.hashdump as hashdumpmod
import forensics.utils as utils
import forensics
config = forensics.conf.ConfObject()

FILTER = ''.join([(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])

def hd(src, length=16):
    N = 0
    result = ''
    while src:
        s, src = src[:length], src[length:]
        hexa = ' '.join(["%02X" % ord(x) for x in s])
        s = s.translate(FILTER)
        result += "%04X   %-*s   %s\n" % (N, length*3, hexa, s)
        N += length
    return result

class lsadump(forensics.commands.command):
    """Dump (decrypted) LSA secrets from the registry"""
    # Declare meta information associated with this plugin
    
    meta_info = forensics.commands.command.meta_info 
    meta_info['author'] = 'Brendan Dolan-Gavitt'
    meta_info['copyright'] = 'Copyright (c) 2007,2008 Brendan Dolan-Gavitt'
    meta_info['contact'] = 'bdolangavitt@wesleyan.edu'
    meta_info['license'] = 'GNU General Public License 2.0 or later'
    meta_info['url'] = 'http://moyix.blogspot.com/'
    meta_info['os'] = 'WIN_32_XP_SP2'
    meta_info['version'] = '1.0'

    def __init__(self, *args):
        config.add_option('SYS-OFFSET', short_option='y', type='int',
                          help='SYSTEM hive offset (virtual)')
        config.add_option('SEC-OFFSET', short_option='s', type='int',
                          help='SECURITY hive offset (virtual)')
        forensics.commands.command.__init__(self, *args)
    
    def calculate(self):
        addr_space = utils.load_as()

        # In general it's not recommended to update the global types on the fly,
        # but I'm special and I know what I'm doing ;)
        # types.update(regtypes)

        if not config.sys_offset or not config.sec_offset:
            config.error("Both SYSTEM and SECURITY offsets must be provided")
        
        secrets = lsasecrets.get_memory_secrets(addr_space, config.sys_offset, config.sec_offset)
        if not secrets:
            config.error("Unable to read LSA secrets from registry")

    def render_text(self, outfd, data):
        for k in data:
            outfd.write(k + "\n")
            outfd.write(hd(data[k]) + "\n")

class hashdump(forensics.commands.command):
    
    def __init__(self, *args):
        config.add_option('SYS-OFFSET', short_option='y', type='int',
                          help='SYSTEM hive offset (virtual)')
        config.add_option('SAM-OFFSET', short_option='s', type='int',
                          help='SAM hive offset (virtual)')
        forensics.commands.command.__init__(self, *args)        
    
    def execute(self):
        addr_space = utils.load_as()

        if not config.sys_offset or not config.sam_offset:
            config.error("Both SYSTEM and SAM offsets must be provided")
        
        hashdumpmod.dump_memory_hashes(addr_space, config.sys_offset, config.sam_offset)
