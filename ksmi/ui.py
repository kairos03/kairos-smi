"""
ksmi Terminal UI module
"""
import curses


MIN_COL_LEN=100


def main(hosts, data):
    curses.wrapper(display, hosts, data)


def display(screen, hosts, data):
    # get display size
    _, cols = screen.getmaxyx()
    # ditermin num cols
    num_col = 1
    if cols >= MIN_COL_LEN * 2: 
        num_col = 2

    # clear screen
    screen.clear()
 
    cur_col = 0
    cur_row = 0

    for host in hosts:
        gpu_stat = data[host].get('gpus')
        app_stat = data[host].get('apps')
        active_gpus = len(set(app_info[0] for app_info in app_stat))
        
        # print gpu stat
        # if gpu stat is empty
        screen.addstr('[{:.30}]'.format(host.split(':')[0]))
        if gpu_stat == None or app_stat == None or len(gpu_stat) == 0:
            screen.addstr('\n| ERROR |')
            continue
        else:
            screen.addstr('{:>20}'.format("Apps {:2} GPUs {:2}/{:2}\n".format(len(app_stat), active_gpus, len(gpu_stat))))
            screen.addstr("| No | Temp | Utils |       Memory       |\n")
        
        # print apps
        for i, gpu in enumerate(gpu_stat):
            if len(gpu) != 9:
                continue
            screen.addstr("| {:2} | {:3s}C | {:>5s} | {:>6s} / {:9s} |\n".format(i, gpu[5], gpu[6], gpu[7][:-4], gpu[8]))
            
    screen.refresh()
    screen.getkey()

if __name__ == "__main__":
    hosts = ["mlvc07@163.180.186.49:2222"]
    wrong_host = ["test@123.123.123.123:2211"]     
    data = {'mlvc07@163.180.186.49:2222': 
                {'apps': 
                    [['GPU-e831358e-b0e6-38c1-eea8-4f08d58ebe5d', '12275', 'python3', '1355 MiB'], 
                     ['GPU-e831358e-b0e6-38c1-eea8-4f08d58ebe5d', '9824', 'python3', '6341 MiB'], 
                    ],
                'gpus': 
                    [['2019/08/28 14:56:39.039', 'GPU-e831358e-b0e6-38c1-eea8-4f08d58ebe5d', '7', 'GeForce RTX 2080 Ti', 'P2', '61', '15 %', '7709 MiB', '10989 MiB'], 
                     ['2019/08/28 14:56:39.046', 'GPU-25ca9c48-5004-6d7a-57ba-f8fce126957c', '7', 'GeForce RTX 2080 Ti', 'P8', '29', '0 %', '11 MiB', '10989 MiB'], 
                    ]
                }
            }
    main(hosts, data)