#!/usr/bin/python

"""
Create a network and start sshd(8) on each host.

While something like rshd(8) would be lighter and faster,
(and perfectly adequate on an in-machine network)
the advantage of running sshd is that scripts can work
unchanged on mininet and hardware.

In addition to providing ssh access to hosts, this example
demonstrates:

- creating a convenience function to construct networks
- connecting the host network to the root namespace
- running server processes (sshd in this case) on hosts
"""

from mininet.net import init, Mininet
from mininet.cli import CLI
from mininet.log import lg
from mininet.node import Node, KernelSwitch
from mininet.topolib import TreeTopo
from mininet.util import createLink

def TreeNet( depth=1, fanout=2, **kwargs ):
    "Convenience function for creating tree networks."
    topo = TreeTopo( depth, fanout )
    return Mininet( topo, **kwargs )
   
def connectToRootNS( network, switch, ip, prefixLen, routes ):
   """Connect hosts to root namespace via switch. Starts network.
      network: Mininet() network object
      switch: switch to connect to root namespace
      ip: IP address for root namespace node
      prefixLen: IP address prefix length (e.g. 8, 16, 24)
      routes: host networks to route to"""
   # Create a node in root namespace and link to switch 0
   root = Node( 'root', inNamespace=False )
   port = max( switch.ports.values() ) + 1
   createLink( root, 0, switch, port )
   root.setIP( root.intfs[ 0 ], ip, prefixLen )
   # Start network that now includes link to root namespace
   network.start()
   intf = root.intfs[ 0 ]
   # Add routes from root ns to hosts
   for net in routes:
      root.cmd( 'route add -net ' + net + ' dev ' + intf )

def sshd( network, cmd='/usr/sbin/sshd -D' ):
   "Start a network, connect it to root ns, and run sshd on all hosts."
   switch = network.switches[ 0 ] # switch to use
   ip = '10.123.123.1' # our IP address on host network
   routes = [ '10.0.0.0/8' ] # host networks to route to
   connectToRootNS( network, switch, ip, 8, routes )
   for host in network.hosts: host.cmd( cmd + ' &' )
   print
   print "*** Hosts are running sshd at the following addresses:"
   print
   for host in network.hosts: print host.name, host.IP()
   print
   print "*** Type 'exit' or control-D to shut down network"
   CLI( network )
   for host in network.hosts: host.cmd( 'kill %' + cmd )
   network.stop()
   
if __name__ == '__main__':
   lg.setLogLevel( 'info')
   init()
   network = TreeNet( depth=1, fanout=4, switch=KernelSwitch )
   sshd( network )
