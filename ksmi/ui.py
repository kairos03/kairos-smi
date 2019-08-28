"""
ksmi Terminal UI module
"""
import curses


MIN_COL_LEN=100
DEBUG=False

def init_screen():
    # init screen
    screen = curses.initscr()
    curses.newwin(50, 100)
    curses.noecho()
    curses.nocbreak()
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    screen.nodelay(True)
    return screen

def cleanup_screen():
    curses.nl()
    curses.echo()
    curses.cbreak()
    curses.curs_set(1)
    curses.endwin()

def display(hosts, data):
    curses.wrapper(_display, hosts, data)


def _display(screen, hosts, data):
    # get display size
    _, cols = screen.getmaxyx()
    # ditermin num cols
    num_col = 1
    if cols >= MIN_COL_LEN * 2: 
        num_col = 2

    # clear screen
    screen.clear()


    for host in hosts:
        gpu_stat = data[host].get('gpus')
        app_stat = data[host].get('apps')
        active_gpus = len(set(app_info[0] for app_info in app_stat))
        
        # print gpu stat
        # if gpu stat is empty
        error = gpu_stat == None or app_stat == None or len(gpu_stat) == 0
        color = curses.color_pair(1) if error else curses.color_pair(2)
        screen.addstr('{: <27}'.format('[{:<.25}]'.format(host.split(':')[0])), color)
        if error:
            screen.addstr('{: >24}'.format('| ERROR |\n'), color)
            continue
        else:
            screen.addstr('{: >24}'.format("Apps: {:<2}  GPUs: {:2}/{:2}\n".format(len(app_stat), active_gpus, len(gpu_stat))), color)
            screen.addstr("| No | Temp | Util% | Mem % |       Memory       |\n", curses.color_pair(3))
        
        # print apps
        for i, gpu in enumerate(gpu_stat):
            if len(gpu) != 9:
                continue
            screen.addstr("| {:2} | {:3s}C | {:>5s} | {:>3.0f} % | {:>6s} / {:9s} |\n".format(i, gpu[5], gpu[6], float(gpu[7][:-4])/float(gpu[8][:-4]) * 100, gpu[7][:-4], gpu[8]))
            
    screen.refresh()
    if DEBUG:
        screen.getkey()


if __name__ == "__main__":
    DEBUG=True
    hosts = ["mlvc08@163.180.186.51:2222", 'mlvc01@163.180.186.41:2222']
    wrong_host = ["test@123.123.123.123:2211"]     
    data = {
            'mlvc08@163.180.186.51:2222': 
                {
                    'apps': 
                        [['GPU-630fa4d7-2180-8cbb-04c4-694adade766b', '21515', 'python3', '2307 MiB'], 
                         ['GPU-630fa4d7-2180-8cbb-04c4-694adade766b', '13617', 'python3', '6385 MiB'], 
                         ['GPU-fa57ff88-6de4-9d3a-da7d-259b74d9b341', '21515', 'python3', '2305 MiB'], 
                         ['GPU-fa57ff88-6de4-9d3a-da7d-259b74d9b341', '13617', 'python3', '6423 MiB'], 
                         ['GPU-4369cf8c-96af-3796-1510-23ecceacd6c2', '21515', 'python3', '2305 MiB'], 
                         ['GPU-4369cf8c-96af-3796-1510-23ecceacd6c2', '13617', 'python3', '6423 MiB'], 
                         ['GPU-9cc81f29-7ebe-588b-cf02-4da70e40e95a', '21515', 'python3', '2299 MiB'], 
                         ['GPU-9cc81f29-7ebe-588b-cf02-4da70e40e95a', '13617', 'python3', '6383 MiB']], 
                    'gpus': 
                        [['2019/08/28 15:54:51.547', 'GPU-630fa4d7-2180-8cbb-04c4-694adade766b', '4', 'GeForce RTX 2080 Ti', 'P2', '45', '12 %', '8709 MiB', '10989 MiB'], 
                         ['2019/08/28 15:54:51.549', 'GPU-fa57ff88-6de4-9d3a-da7d-259b74d9b341', '4', 'GeForce RTX 2080 Ti', 'P2', '46', '11 %', '8745 MiB', '10989 MiB'], 
                         ['2019/08/28 15:54:51.551', 'GPU-4369cf8c-96af-3796-1510-23ecceacd6c2', '4', 'GeForce RTX 2080 Ti', 'P2', '45', '11 %', '8745 MiB', '10989 MiB'], 
                         ['2019/08/28 15:54:51.553', 'GPU-9cc81f29-7ebe-588b-cf02-4da70e40e95a', '4', 'GeForce RTX 2080 Ti', 'P2', '46', '11 %', '8699 MiB', '10986 MiB']]
                }, 
            'mlvc01@163.180.186.41:2222': 
                {
                    'gpus': 
                        [['2019/08/28 15:54:51.467', 'GPU-fb19aca9-d0b4-4737-fde5-e1437483dc2f', '4', 'GeForce GTX 1080 Ti', 'P2', '50', '27 %', '2286 MiB', '11178 MiB'], 
                         ['2019/08/28 15:54:51.468', 'GPU-9348dc32-6554-e4b3-c863-af5a08ec2f34', '4', 'GeForce GTX 1080 Ti', 'P2', '51', '26 %', '2286 MiB', '11178 MiB'], 
                         ['2019/08/28 15:54:51.470', 'GPU-60502ea9-e801-c65c-ab58-5e5ba27a0c3d', '4', 'GeForce GTX 1080 Ti', 'P2', '56', '78 %', '2286 MiB', '11178 MiB'], 
                         ['2019/08/28 15:54:51.471', 'GPU-2071bf07-1c43-67d0-e701-204519e7465a', '4', 'GeForce GTX 1080 Ti', 'P2', '53', '27 %', '2286 MiB', '11175 MiB']], 
                    'apps': 
                        [['GPU-fb19aca9-d0b4-4737-fde5-e1437483dc2f', '17126', 'python3', '2275 MiB'], 
                         ['GPU-9348dc32-6554-e4b3-c863-af5a08ec2f34', '24968', 'python3', '2275 MiB'], 
                         ['GPU-60502ea9-e801-c65c-ab58-5e5ba27a0c3d', '28585', 'python3', '2275 MiB'], 
                         ['GPU-2071bf07-1c43-67d0-e701-204519e7465a', '2687', 'python3', '2275 MiB']]
                }
            }
    display(hosts, data)
