import unittest
from unittest.mock import patch, MagicMock
import subprocess

from ksmi.kairos_smi import ssh_remote_command, QUERY_APP, QUERY_GPU

class test_ssh_remote_command(unittest.TestCase):
    
    def setUp(self):
        self.success_host = "success@111.111.111.111:22"
        self.error_host = "error@123.123.123.123:2211"
        self.timeout = 1
        self.return_ssh_success = (
            b'2019/08/30 12:04:44.462, GPU-e831358e-b0e6-38c1-eea8-4f08d58ebe5d, 7, GeForce RTX 2080 Ti, P2, 70, 81 %, 10256 MiB, 10989 MiB\n'
            + b'2019/08/30 12:04:44.472, GPU-25ca9c48-5004-6d7a-57ba-f8fce126957c, 7, GeForce RTX 2080 Ti, P8, 29, 0 %, 11 MiB, 10989 MiB\n',
            b'')
        self.return_ssh_error = (b'', b'Error')
        self.return_ssh_timeout = (b'', b'Timeout')
        
    def tearDown(self):
        pass

    @patch('subprocess.Popen.communicate')
    def test_echo_success(self, mock_subprocess):
        mock_subprocess.return_value = (b'hello\nhi\n', b'')
        # success case
        command = 'echo hello; echo hi'
        result = ssh_remote_command(self.success_host, command, self.timeout)
        self.assertEqual(result,
            {
                'status': 'Success',
                'entry': self.success_host, 
                'command': command, 
                'data': [['hello'], ['hi']]
            })
    
    @patch('subprocess.Popen.communicate')
    def test_query_success(self, mock_subprocess):
        mock_subprocess.return_value = self.return_ssh_success
        # success case
        result = ssh_remote_command(self.success_host, QUERY_GPU, self.timeout)
        self.assertEqual(result['status'], 'Success')
        print(result['data'])
        
    def test_query_fail(self):
        # fail case
        result = ssh_remote_command(self.error_host, 'echo hello', self.timeout)
        self.assertEqual(result['status'], 'Timeout')
