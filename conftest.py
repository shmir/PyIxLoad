
def pytest_addoption(parser):
    parser.addoption("--api", action="store", default="rest", help="api options: rest or tcl")
    parser.addoption("--server", action="store", default="localhost", help="server IP in format ip[:port]")
    parser.addoption("--chassis", action="store", default="192.168.42.207", help="chassis IP address")
    parser.addoption("--originate", action="store", default="192.168.42.207/1/1", help="ip1/module1/port1")
    parser.addoption("--terminate", action="store", default="192.168.42.173/1/1", help="ip2/module2/port2")
