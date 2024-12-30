import argparse
from concurrent.futures import ThreadPoolExecutor
from time import time, sleep
import os
import threading
import keyboard
# import sys
# import platform
# import msvcrt
# import select

# other files
import socket_functions
import utils

def keyboard_interrupt_exit(executor: ThreadPoolExecutor) -> None:
    '''
    Exit on KeyboardInterrupt exception during scanning, clean up threads
        executor: the ThreadPoolExecutor used for multithreading
    Return: None
    '''
    print('Cleaning up threads...')
    executor.shutdown(wait=False, cancel_futures=True)
    print('Exiting program...')
    exit(0)

def invalid_args_exit(param: str, arg: str) -> None:
    '''
    Exit when invalid arguments are provided
        param: the invalid parameter
        arg: the invalid argument
    Return: None
    '''
    print(f'Invalid arguments provided for {param}: {arg}')
    exit(0)

def update_on_press() -> None:
    '''
    Update user based on key pressed
    Return: None
    '''
    if keyboard.is_pressed('p'):
        completed = int(100 * (COUNT / len(ARGS['ports'])))
        print(f"\nProgress: {COUNT}/{len(ARGS['ports'])}")
        print('▕' + completed*'▓' + (100 - completed)*'░' + '▏\n')

# def check_stdin() -> bool:
#     '''
#     Checks if stdin contains user input, method dependent on OS
#     Return: input exists in stdin?
#     '''
#     if OS == 'Windows':
#         return msvcrt.kbhit()
#     else:
#         return bool(select.select([sys.stdin], [], [], 0.0)[0])

def _progress_decorator(func):
    '''
    Decorator to help check scanning progress
    '''
    def dec(*args, **kwargs):
        global COUNT

        res = func(*args, **kwargs)

        with LOCK:
            COUNT += 1

        return res

    return dec

@_progress_decorator
def scan_port(target: int | str, port: int, protocols: list=['tcp', 'udp']) -> list:
    '''
    Scan the specified port for the target
        target: address of target
        port: number in [1, 65537] denoting the port # to scan
        protocols: list of network protocols to try
    Return: [open port? for each protocol]
    '''
    results = []
    for protocol in protocols:
        results.append(socket_functions.PROTOCOL_HANDLING[protocol](target, port))
    return results
    
def get_args() -> None:
    '''
    Parse arguments passed in command line, sets global dictionary ARGS
    Return: None
    '''
    global ARGS

    ap = argparse.ArgumentParser(prog=f"/path/to/python3/interpreter {os.path.basename(__file__)}")
    ap.add_argument('TARGET',
                    help='address of target')
    ap.add_argument('-p', '--ports', nargs=2, type=int, default=[1, 65537], metavar=('START', 'END'),
                    help='port range to scan, defaults to all ports 1-65537; ports in the range [START, END], inclusive, are scanned')
    ap.add_argument('-t', '--threads', type=int, default=100, metavar="NUM_THREADS",
                    help='number of threads to use, defaults to 100; \033[31;1m[WARN] Excessively high thread count can crash your computer.\033[0m')
    ap.add_argument('--protocols', nargs='+', type=str, default=[], action='extend', metavar="PROTOCOL",
                    help='the protocols to scan for, defaults to [TCP, UDP]; currently supported: TCP, UDP')

    args = ap.parse_args()
    ARGS = dict()
    ARGS['target'] = args.TARGET
    ARGS['ports'] = range(*((lambda l: [l[0], l[1] + 1])(args.ports)))
    ARGS['threads'] = args.threads

    if len(args.protocols) == 0:
        ARGS['protocols'] = ['tcp', 'udp']
    else:
        ARGS['protocols'] = []
        for protocol in args.protocols:
            if protocol.lower() not in SUPPORTED_PROTOCOLS:
                invalid_args_exit('--protocols', protocol)
            ARGS['protocols'].append(protocol)

    print(ARGS['protocols'])

def setup():
    '''
    Set globals COUNT, LOCK, OS
        COUNT: count of ports scanned so far
        LOCK: thread lock
        OS: operating system
    Return: None
    '''
    global COUNT
    global LOCK
    # global OS
    global SUPPORTED_PROTOCOLS

    COUNT = 0
    LOCK = threading.Lock()
    # OS = platform.system()
    SUPPORTED_PROTOCOLS = set(('tcp', 'udp'))
    
def main():
    '''
    Main program functionality
    '''
    setup()
    get_args()

    # multithreading
    open_ports = []
    start = time()
    with ThreadPoolExecutor(max_workers=ARGS['threads']) as executor:
        res = []
        print(f"Started scanning at {'{:.2f}'.format(time() - start)}s")
        for port in ARGS['ports']:
            res.append(executor.submit(scan_port, ARGS['target'], port, ARGS['protocols']))

        # output updates based on user key presses
        try:
            while any(map(lambda e: e.running(), res)):
                update_on_press()
                sleep(0.1)
        except KeyboardInterrupt:
            keyboard_interrupt_exit(executor)

        # process results
        ind = 0
        for port in ARGS['ports']:
            result = res[ind].result()
            open_ports.extend([(port, ARGS['protocols'][i]) for i in range(len(result)) if result[i]])
            ind += 1
        print(f"Finished scanning at {'{:.2f}'.format(time() - start)}s")
    
    # sort ports + output to user
    print()
    open_ports = sorted(open_ports)
    columns = ['PORT', 'PROTOCOL', 'SERVICE']
    widths = [len(column) + 4 for column in columns]
    print(utils.ljust_all(columns, widths))
    for port,protocol in open_ports:
        print(utils.ljust_all([str(port), protocol, socket_functions.get_service(port)], widths))

if __name__ == '__main__':
    main()