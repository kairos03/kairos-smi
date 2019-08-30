import unittest
from unittest.mock import patch, MagicMock
import subprocess

from ksmi.kairos_smi import ssh_remote_command, QUERY_APP, QUERY_GPU

class test_ssh_remote_command(unittest.TestCase):
    
    def setUp(self):
        self.host = "mlvc07@163.180.186.49:2222"
        self.wrong_host = "test@123.123.123.123:2211"
        self.timeout = 1
        self.return_ssh_success = (b"""
            2019/08/30 12:04:44.462, GPU-e831358e-b0e6-38c1-eea8-4f08d58ebe5d, 7, GeForce RTX 2080 Ti, P2, 70, 81 %, 10256 MiB, 10989 MiB\n
            2019/08/30 12:04:44.472, GPU-25ca9c48-5004-6d7a-57ba-f8fce126957c, 7, GeForce RTX 2080 Ti, P8, 29, 0 %, 11 MiB, 10989 MiB\n
            """,
            b'')
        self.return_ssh_error = (b'', b'Error')
        self.return_ssh_timeout = (b'', b'Timeout')
        
    def tearDown(self):
        pass

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
    
    @patch('subprocess.Popen')
    def test_query_success(self, mock_Popen):
        mock_Popen.communicate.side_effect = self.return_ssh_success
        # success case
        result = ssh_remote_command(self.host, QUERY_GPU, self.timeout)
        self.assertEqual(result['status'], 'Success')
        
    def test_query_fail(self):
        # fail case
        result = ssh_remote_command(self.wrong_host, 'echo hello', self.timeout)
        self.assertEqual(result['status'], 'Timeout')

    def test_query_process(self):
        query = """
        a=($(nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader,nounits | awk '{print $1,$2,$3}' FS=', ' OFS=','))
        for item in $a
        do
            ps=$(ps --noheader -o "pid,user,%cpu,%mem,etime,command" -p $(echo $item | awk '{print $2}' FS=','))
            echo $item | awk '{printf "%s, %s, ", $1, $3}' FS="," RS="\n" 
            echo $ps | awk 'BEGIN {OFS=", "} {$1=$1; print}' RS="\n"
        done;
        """
        
        result = ssh_remote_command(self.host, query, 2)
        print(result['data'])
        result = ssh_remote_command(self.host, 'echo test', 1)
        print(result['data'])