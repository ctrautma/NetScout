# NetScout
Simple Netscout script to create/delete port pairings and to report information about ports, connections etc.

Includes an extended telnetlib library that provides a telnet.log so commands can be tracked.

Can be used to connect or disconnect ports by name.

## Various options

-h, --help : show this help message and exit
  
--connect port1 port2 : Create a connection between two ports
  
--disconnect port [port ...] : Disconnect a port(s) from its connection

--listgroups : Lists all the configured groups

--listports : Lists all the ports on the netscout

--portinfo port : Prints port information

--showconnections : Lists all the connections on netscout

--downloadhelp : Downloads CLI command help for netscout in txt file

--resetconfig : Resets config file

##Examples: How to use
```
/root/Python-3.4.3/python NSConnect.py --connect {port 1} {port2}

/root/Python-3.4.3/python NSConnect.py --disconnect {port1} {port2}

/root/Python-3.4.3/python NSConnect.py --listports

/root/Python-3.4.3/python NSConnect.py --showconnections

/root/Python-3.4.3/python NSConnect.py --downloadhelp

```

# Installation RHEL 7.x
## Install Python 3.4 using SCL
```
python install scl-utils -y
```

## Install SCL for python34 by adding a repository
```
cat <<'EOT' >> /etc/yum.repos.d/python34.repo
[centos-sclo-rh]
name=CentOS-7 - SCLo rh
baseurl=http://mirror.centos.org/centos/7/sclo/$basearch/rh/
gpgcheck=0
enabled=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-SIG-SCLo
EOT
```

## Install python34 packages
```
yum -y install $(echo "
rh-python34
rh-python34-python-tkinter
" | grep -v ^#)
```

## Cleanup python 34 repo file
```
rm -f /etc/yum.repos.d/python34.repo
```

#To install selectors34 first create a virtualenv for python34
```
scl enable rh-python34 bash
$MYENV=<path to your desired virtual env> # /home/python3env works well for most cases
virtualenv "$MYENV"
yum install -y python-setuptools
easy_install pip
pip install selectors34
```

#For automation you can use code blocks like this
```
scl enable rh-python34 - << \EOF
    source $MYENV/bin/activate
    pip install selectors34
    python NSConnect.py -h
EOF
```

If using python 3.3 the selectors package will cause a problem because it it not readily available. To resolve install the selectors34  package with pip.
