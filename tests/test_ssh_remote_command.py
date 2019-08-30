import unittest
from unittest.mock import patch, MagicMock
import subprocess

from ksmi.kairos_smi import ssh_remote_command, QUERY_APP, QUERY_GPU

class test_ssh_remote_command(unittest.TestCase):
    
    def setUp(self):
        self.host = "mlvc07@163.180.186.49:2222"
        self.wrong_host = "test@123.123.123.123:2211"
        self.timeout = 1
        self.return_ssh = b"""

        """

    def tearDown(self):
        pass

    def _mock_ssh_command(self, command):
        mock_ret = mock.MagicMock()


    # TODO skip
    def test_echo_success(self):
        # success case
        
        result = ssh_remote_command(self.host, 'echo hello; echo hi', self.timeout)
        self.assertEqual(result,
            {
                'status': 'Success',
                'entry': self.host, 
                'command': 'echo hello; echo hi', 
                'data': [['hello'], ['hi']]
            })
    
    @patch.object(subprocess.Popen, 'communicate',
            return_value=(
                            b'2019/08/30 12:04:44.462, GPU-e831358e-b0e6-38c1-eea8-4f08d58ebe5d, 7, GeForce RTX 2080 Ti, P2, 70, 81 %, 10256 MiB, 10989 MiB\n2019/08/30 12:04:44.472, GPU-25ca9c48-5004-6d7a-57ba-f8fce126957c, 7, GeForce RTX 2080 Ti, P8, 29, 0 %, 11 MiB, 10989 MiB\n',
                            b''))
    def test_query_success(self, mock_Popen):
        # success case
        result = ssh_remote_command(self.host, QUERY_GPU, self.timeout)
        self.assertEqual(result['status'], 'Success')
        
    def test_query_fail(self):
        # fail case
        result = ssh_remote_command(self.wrong_host, 'echo hello', self.timeout)
        self.assertEqual(result['status'], 'Timeout')
