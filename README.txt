
+++ WORK IN PROGRESS - basic functionality, documentation under construction. +++

TGN - Traffic Generator
IXL - IxLoad

This package implements Python OO API for Ixia IxLoad traffic generator.

Installation:
stable - pip instsll ixlooapi
testing - pip install ixlooapi -r --extra-index-url https://testpypi.python.org/pypi

Prerequisite:
IxLoad application installed.

Functionality
The current version supports the following test flow:
	Load configuration -> Get/Set attributes -> Start/Stop traffic -> Get statistics.
Supported operations:
	- Basic operations - get/set attributes, get/create children.
	- Load configuration - load configuration (rxf), select test, reserve ports and analyze the configuration
	- Start/Stop - test
	- Statistics - read views
	- Save configuration
	- Disconnect

Known limitations:
- one traffic flow per test

Contact:
Feel free to contact me with any question or feature request at yoram@ignissoft.com
