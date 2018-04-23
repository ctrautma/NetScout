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

# Installation RHEl 7.x
Install Python 3.4 using scl
python install scl-utils -y

# install SCL for python34 by adding a repo to find its location to install it
cat <<'EOT' >> /etc/yum.repos.d/python34.repo
[centos-sclo-rh]
name=CentOS-7 - SCLo rh
baseurl=http://mirror.centos.org/centos/7/sclo/$basearch/rh/
gpgcheck=0
enabled=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-SIG-SCLo
EOT

# install python34 packages
yum -y install $(echo "
rh-python34
rh-python34-python-tkinter
" | grep -v ^#)

# cleanup python 34 repo file
rm -f /etc/yum.repos.d/python34.repo

To install selectors34 first create a virtualenv for python34
scl enable rh-python34 bash
$MYENV=<path to your desired virtual env> # /home/python3env works well for most cases
virtualenv "$MYENV"
yum install -y python-setuptools
easy_install pip
pip install selectors34

For automation you can use code blocks like this
scl enable rh-python34 - << \EOF
    source $MYENV/bin/activate
    pip install selectors34
    python NSConnect.py -h
EOF

If using python 3.3 the selectors package will cause a problem
because it it not readily available. To resolve install the 
selectors34  package with pip.

