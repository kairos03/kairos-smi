import unittest

from ksmi.kairos_smi import ssh_remote_command, QUERY_APP, QUERY_GPU

class test_ssh_remote_command(unittest.TestCase):
    
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_local_echo_success(self):
        # success case
        result = ssh_remote_command('localhost', 'echo hello; echo hi')
        self.assertEqual(result,
            {
                'status': 'Success',
                'entry': 'localhost', 
                'command': 'echo hello; echo hi', 
                'data': [['hello'], ['hi']]
            })

    def test_local_query_success(self):
        # success case
        result = ssh_remote_command('localhost', QUERY_GPU)
        self.assertEqual(result['status'], 'Success')
        
    def test_ssh_remote_command_fail(self):
        # fail case
        result = ssh_remote_command('test@1.1.1.1:2222', 'echo hello')
        self.assertEqual(result['status'], 'Timeout')
