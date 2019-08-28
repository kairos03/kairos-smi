import sys
import os
import unittest

import curses

from ksmi.ui import display
from ksmi.ui import main

class test_display(unittest.TestCase):
    def setUp(self):
        # set envs
        os.environ['TERM'] = 'linux'
        os.environ['TERMINFO'] = '/etc/terminfo'

        self.screen = curses.initscr()
        curses.noecho()

        self.hosts = ["mlvc07@163.180.186.49:2222"]
        self.wrong_host = ["test@123.123.123.123:2211"]     
        self.data = {'mlvc07@163.180.186.49:2222': \
                        {'apps': \
                            [['GPU-e831358e-b0e6-38c1-eea8-4f08d58ebe5d', '12275', 'python3', '1355 MiB'], \
                             ['GPU-e831358e-b0e6-38c1-eea8-4f08d58ebe5d', '9824', 'python3', '6341 MiB'], 
                            ]
                        }
                    }
    
    def test_display(self):
        display(self.screen, self.hosts, self.data)

    def tearDown(self):
        pass