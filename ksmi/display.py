import curses

def main(screen):
    rows, cols = screen.getmaxyx()

    # clear screen
    screen.clear()

    screen.addstr("{} x {}".format(rows, cols))
    screen.refresh()
    screen.getkey()

if __name__ == "__main__":
    curses.wrapper(main)