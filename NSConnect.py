"""
NSConnect.py

Net Scout simple CLI script to connect and disconnect ports based on their
port names. After single execution will store connection and login info into
a settings file that is not secure. It is encoded to provide minimal security.

This module can be added to provide much more functionality as requested.

Execute NetScout command

optional arguments:
  -h, --help            show this help message and exit
  --connect port1 port2
                        Create a connection between two ports
  --disconnect port [port ...]
                        Disconnect a port(s) from its connection

Copyright 2016 Christian Trautman ctrautma@redhat.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import argparse
import base64
import os
import sys

if sys.version_info[0] == 2:
    import ConfigParser as configparser
else:
    import configparser
import locale
import telnetliblog
from time import sleep

_LOCALE = locale.getlocale()[1]


class NetScout_Command(object):
    def __init__(self, parser, args):
        self.args = args
        if not any([args.connect,
                    args.disconnect,
                    args.downloadhelp,
                    args.listports,
                    args.listgroups,
                    args.portinfo,
                    args.resetconfig,
                    args.isconnected,
                    args.showconnections]):
            print("No actions provided...")
            parser.print_help()
            sys.exit(1)

        self._cfg = configparser.ConfigParser()

        if self.args.resetconfig:
            self.resetconfig()

        print("Checking for config file...")
        self._cfg.read('settings.cfg')

        try:
            self._ip_addr = base64.b64decode(
                self._cfg['INFO']['host']).decode(_LOCALE)
            self._port = base64.b64decode(
                self._cfg['INFO']['port']).decode(_LOCALE)
            self._username = base64.b64decode(
                self._cfg['INFO']['username']).decode(_LOCALE)
            self._password = base64.b64decode(
                self._cfg['INFO']['password']).decode(_LOCALE)
            print("Config file found and read...")
        except KeyError:
            self.write_settings()

        print("Connecting to Netscout at {}".format(self._ip_addr))
        self.tn = telnetliblog.Telnet2(self._ip_addr, self._port)

        try:
            self.logon()
        except Exception as e:
            print(e)
            import sys
            sys.exit()

        if self.args.downloadhelp:
            self.downloadhelp()

        self.model = self.get_switch_model()
        self.parse_args()

    #def connect(self, ports):
    #    self.issue_command('connect PORT {} to PORT {} force'.format(*ports))

    def connect(self, ports):
        if self.model == "HS-3200":
            self.connect_hs3200(ports)
        else:
            self.issue_command('connect PORT {} to PORT {} force'.format(*ports))

    def connect_hs3200(self, ports):
        substr = "ERROR"
        port_compatible= "Port interfaces are not compatible!"
        print('Connecting ports {} {}'.format(*ports))
        port_list = self.list_ports_internal()
        for i in ports:
            if not i in port_list:
                print("INPUT PORT invalid ,please check")
                return
        #First disconnet all ports
        print("First disconnect all ports that connected")
        self.disconnect_hs3200(ports)
        conn_out = self.get_command_output('connect -d PORT {} PORT {}'.format(*ports))
        #print(conn_out)
        if port_compatible in str(conn_out):
            print(port_compatible)
            return
        out = self.get_command_output('activate -d PORT {} PORT {}'.format(*ports))
        #print(out)
        out = out.decode(_LOCALE).split('\r\n')
        for line in out[0:-1]:
            if substr in line:
                self.disconnect_hs3200(ports)
                self.connect_hs3200(ports)
                break
        print('Connecting ports {} {} Done OK'.format(*ports))
        pass

    #def disconnect(self, ports):
    #    for port in ports:
    #        self.issue_command('connect PORT {} to null force'.format(port))

    def disconnect(self, ports):
        if self.model == "HS-3200":
            self.disconnect_hs3200(ports)
        else:
            for port in ports:
                self.issue_command('connect PORT {} to null force'.format(port))

    def disconnect_hs3200(self, ports):
        print('Disconnecting connections to ports {}'.format(" ".join(ports)))
        for port in ports:
            connected_ports = self.getconnected(port)
            if len(connected_ports) != 0:
                self.issue_command('disconnect -d PORT {} PORT {}'.format(*connected_ports))


    def getalltopo(self):
        out = self.get_command_output('show topo all', timeout=60)
        out = out.decode(_LOCALE).split('\r\n')
        return [ " ".join(i.split(" ")[0:-1]).rstrip(" ") for i in out[2:-2]]


    def isconnected(self, port):
        connect_status=0
        connected_ports = self.getconnected(port[0])
        if len(connected_ports) != 0:
            connect_status=1
        print(connect_status)

    def getconnected(self, port):
        substr="Name"
        ifaces=[]
        out = self.get_command_output('show connection details port {}'.format(port), timeout=60)
        out = out.decode(_LOCALE).split('\r\n')
        for line in out[0:-1]:
            if substr in line:
                part = line.split()[2]
                ifaces.append(part)
        return ifaces

    def get_switch_name(self):
        out = self.get_command_output('show switch', timeout=60)
        out = out.decode(_LOCALE).split('\r\n')
        switch_name = out[0:-1][2]
        return switch_name

    def get_switch_model(self):
        substr = "Model"
        switch_model=""
        switch_name = self.get_switch_name()
        out = self.get_command_output('show switch {}'.format(switch_name), timeout=60)
        out = out.decode(_LOCALE).split('\r\n')
        for line in out[0:-1]:
            if substr in line:
                switch_model = line.split()[3][:-1]
                break
        return switch_model

    def downloadhelp(self):
        self.tn.write('\r'.encode(_LOCALE))
        out = self.tn.expect(['=\>'.encode(_LOCALE)], timeout=30)
        self.tn.write('help\r'.encode(_LOCALE))
        print("Downloading help file to helpfile.txt")
        out = self.tn.expect(['=\> '.encode(_LOCALE)], timeout=300, decoding='windows-1252')
        with open('helpfile.txt', 'w') as fh:
            fh.writelines(str(out[2]))
        sys.exit(0)

    def issue_command(self, cmd, timeout=30):
        self.tn.write('{}\r'.format(cmd).encode(_LOCALE))
        out = self.tn.expect(['=\>'.encode(_LOCALE)], timeout=timeout)
        if out[0] != -1:
            return True
        else:
            return False

    def get_command_output(self, cmd, timeout=30):
        self.tn.write('{}\r'.format(cmd).encode(_LOCALE))
        out = self.tn.expect(['=\>'.encode(_LOCALE)], timeout=timeout)
        if out[0] != -1:
            return out[2]
        else:
            return ''

    def list_groups(self):
        out = self.get_command_output('show groups', timeout=60)
        out = out.decode(_LOCALE).split('\r\n')
        for line in out[2:-2]:
            print(line)

    def list_ports_internal(self):
        out = self.get_command_output('show ports', timeout=60)
        out = out.decode(_LOCALE).split('\r\n')
        return out[2:-2]

    def list_ports(self):
        out = self.list_ports_internal()
        for line in out:
            print(line)

    def logon(self):
        print("Attempting to logon to Netscout...")
        self.tn.write('\r'.encode(_LOCALE))
        out = self.tn.expect(['=\>'.encode(_LOCALE)], timeout=30)
        if out[0] != -1:
            self.tn.write('logon {}\r'.format(self._username).encode(_LOCALE))
        else:
            raise RuntimeError('Failed to get basic prompt on telnet!!!')
        out = self.tn.expect(['Password:'.encode(_LOCALE)], timeout=30)
        sleep(1)
        if out[0] != -1:
            self.tn.write('{}\r'.format(self._password).encode(_LOCALE))
        else:
            raise RuntimeError('Did not get password prompt!!!')
        out = self.tn.expect(['=\>'.encode(_LOCALE)], timeout=30)
        if str(out[2]).find('Access denied. Username/Password is invalid!') > -1:
            raise Exception('Access denied. Username/Password is invalid!')
        if out[0] == -1:
            raise RuntimeError('Failed to logon!!!')

    def parse_args(self):
        if self.args.connect:
            self.connect(self.args.connect)
        if self.args.disconnect:
            self.disconnect(self.args.disconnect)
        if self.args.listports:
            self.list_ports()
        if self.args.listgroups:
            self.list_groups()
        if self.args.portinfo:
            self.show_port_info(self.args.portinfo)
        if self.args.showconnections:
            self.show_port_connections()
        if self.args.isconnected:
            self.isconnected(self.args.isconnected)


    def resetconfig(self):
        if os.path.exists('settings.cfg'):
            os.remove('settings.cfg')

    def show_port_connections(self):
        out = self.get_command_output('show connected ports', timeout=60)
        out = out.decode(_LOCALE).split('\r\n')
        for line in out[2:-2]:
            print(line)

    def show_port_info(self, ports):
        for port in ports:
            out = self.get_command_output(
                'show information Port {}'.format(port), timeout=60)
            out = out.decode(_LOCALE).split('\r\n')
            for line in out[0:-1]:
                print(line)

    def write_settings(self):
        print("Config file not present....")
        print("Please answer the following questions.")
        self._ip_addr = input("Netscout IP address:")
        self._port = input("Netscout telnet port:")
        self._username = input("Netscout username:")
        from getpass import getpass
        self._password = getpass("Netscout password:")
        self._cfg['INFO'] = {
            'host': base64.b64encode(self._ip_addr.encode(_LOCALE)).decode(),
            'port': base64.b64encode(self._port.encode(_LOCALE)).decode(),
            'username': base64.b64encode(
                self._username.encode(_LOCALE)).decode(),
            'password': base64.b64encode(
                self._password.encode(_LOCALE)).decode()}
        with open('settings.cfg', 'w') as fh:
            self._cfg.write(fh)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Execute NetScout command')

    parser.add_argument('--connect', nargs=2, type=str,
                        help='Create a connection between two ports',
                        required=False, metavar=('port1', 'port2'))
    parser.add_argument('--disconnect', nargs='+', type=str,
                        help='Disconnect a port(s) from its connection',
                        required=False, metavar=('port', 'port'))
    parser.add_argument('--downloadhelp', action='store_true',
                        help='download help to local file and exit', required=False)
    parser.add_argument('--listgroups', action='store_true',
                        help='Show list of available groups', required=False)
    parser.add_argument('--listports', action='store_true',
                        help='Show list of available ports', required=False)
    parser.add_argument('--portinfo', nargs='+', type=str,
                        help='Show information on ports', required=False)
    parser.add_argument('--resetconfig', action='store_true',
                        help='Reset config file', required=False)
    parser.add_argument('--showconnections', action='store_true',
                        help='Show active port connections', required=False)
    parser.add_argument('--isconnected', nargs='+', type=str,
                        help='Returns 1 if port is connected. Need port as an argument.', required=False)
    args = parser.parse_args()
    NETS = NetScout_Command(parser, args)
