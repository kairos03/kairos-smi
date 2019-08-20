import unittest

from ksmi.kairos_smi import ssh_remote_command, QUERY_APP, QUERY_GPU

class test_ssh_remote_command(unittest.TestCase):
    
    def setUp(self):
        self.host = "mlvc07@163.180.186.49:2222"
        self.wrong_host = "test@123.123.123.123:2211"
        self.timeout = 2

    def tearDown(self):
        pass

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

    def test_query_success(self):
        # success case
        result = ssh_remote_command(self.host, QUERY_GPU, self.timeout)
        self.assertEqual(result['status'], 'Success')
        
    def test_query_fail(self):
        # fail case
        result = ssh_remote_command(self.wrong_host, 'echo hello', self.timeout)
        self.assertEqual(result['status'], 'Timeout')
