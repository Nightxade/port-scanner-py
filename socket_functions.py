import socket

PROTOCOL_TO_SOCKET = {'tcp': socket.SOCK_STREAM, 'udp': socket.SOCK_DGRAM}

def handle_tcp(target: int | str, port: int) -> bool:
    '''
    Check if the specified target and port is open for TCP connections
        target: address of target
        port: number in [1, 65537] denoting the port # to scan
    Return: open port for UDP?
    '''
    try:
        with socket.socket(socket.AF_INET, PROTOCOL_TO_SOCKET['tcp']) as s:
            s.settimeout(0.25)
            if s.connect_ex((target, port)) == 0:
                return True
            else:
                return False
    except:
        return False
    
def handle_udp(target: int | str, port: int) -> bool:
    '''
    Check if the specified target and port is open for UDP connections
        target: address of target
        port: number in [1, 65537] denoting the port # to scan
    Return: open port for UDP?
    '''
    try:
        with socket.socket(socket.AF_INET, PROTOCOL_TO_SOCKET['udp']) as s:
            s.settimeout(0.5)
            s.sendto(b"test", (target, port))
            s.recvfrom(1024)
            return True
    except:
        return False
    
def get_service(port: int) -> str:
    '''
    Retrieve the name of the service associated with a port
    Return: service name
    '''
    try:
        return socket.getservbyport(port)
    except:
        return 'unknown'

PROTOCOL_HANDLING = {'tcp': handle_tcp, 'udp': handle_udp}