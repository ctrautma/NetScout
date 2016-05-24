# NetScout
Simple Netscout script to create and delete port pairings

Includes an extended telnetlib library that provides a telnet.log so commands can be tracked.

Can be used to connect or disconnect ports by name.

Execute NetScout command

optional arguments:

  -h, --help            show this help message and exit
  
  --connect port1 port2
  
                        Create a connection between two ports
  
  --disconnect port [port ...]
  
                        Disconnect a port(s) from its connection
