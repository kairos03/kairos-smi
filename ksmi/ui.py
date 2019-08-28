"""
ksmi Terminal UI module
"""
import curses


MIN_COL_LEN=100


def main(hosts, data):
    curses.wrapper(display, hosts, data)


def display(screen, hosts, data):
    # get display size
    rows, cols = screen.getmaxyx()
    # ditermin num cols
    num_col = 1
    if cols >= MIN_COL_LEN * 2: 
        num_col = 2
    


    # clear screen
    screen.clear()
 
    screen.addstr("{} x {}".format(rows, cols))

    screen.refresh()
    screen.getkey()

if __name__ == "__main__":
    hosts = ["mlvc07@163.180.186.49:2222"]
    wrong_host = ["test@123.123.123.123:2211"]     
    data = {'mlvc07@163.180.186.49:2222': 
                {'apps': 
                    [['GPU-e831358e-b0e6-38c1-eea8-4f08d58ebe5d', '12275', 'python3', '1355 MiB'], 
                     ['GPU-e831358e-b0e6-38c1-eea8-4f08d58ebe5d', '9824', 'python3', '6341 MiB'], 
                    ]
                }
            }
    main(hosts, data)