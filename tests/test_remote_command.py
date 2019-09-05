import subprocess
import unittest

from ksmi import remote_command
from ksmi import queries

class test_new_ssh_connection(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        remote_command.close_connection(self.ssh)

    def test_connection(self):
        self.ssh = remote_command.new_ssh_connection("mlvc08@163.180.186.51", 2222)
        self.assertIsInstance(self.ssh, subprocess.Popen)


class test_execute_remote_command(unittest.TestCase):
    def setUp(self):
        self.ssh = remote_command.new_ssh_connection("mlvc08@163.180.186.51", 2222)
        
    
    def tearDown(self):
        remote_command.close_connection(self.ssh)

    def test_execution(self):
        #remote_command.execute_remote_command(self.ssh, remote_command.QUERY_APP)
        lines = remote_command.execute_remote_command(self.ssh, queries.QUERY_APP_PROCESS)
        for line in lines:
            print(line)
        #remote_command.execute_remote_command(self.ssh, remote_command.QUERY_GPU)
