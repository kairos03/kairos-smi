import sys
import os
import unittest

import curses

from ksmi import ui

class test_display(unittest.TestCase):
    def setUp(self):
        # set envs
        os.environ['TERM'] = 'linux'
        os.environ['TERMINFO'] = '/etc/terminfo'
        self.screen = ui.init_screen()
        self.hosts = ["test@163.180.111.111:22"]
        self.wrong_host = ["test@123.123.123.123:2211"]     
        self.data = {'test@163.180.111.111:22': \
                        {'apps': \
                            [['GPU-e831358e-b0e6-38c1-eea8-4f08d58ebe5d', '12275', 'python3', '1355 MiB'], \
                             ['GPU-e831358e-b0e6-38c1-eea8-4f08d58ebe5d', '9824', 'python3', '6341 MiB'], 
                            ]
                        }
                    }
    
    def tearDown(self):
        try:
            pass
        except:
            pass

    def test_display(self):
        ui.display(self.screen, self.hosts, self.data)
        print(self.screen.)
