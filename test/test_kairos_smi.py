import unittest

from ksmi.kairos_smi import *

class test_kairos_smi(unittest.TestCase):
    def test_get_gpu_status_v2(self):
        
        hosts = ["mlvc01@163.180.186.41:2222"]

        results = get_gpus_status_v2(hosts)
        print(results)
    
    def test_ssh_remote_command(self):
        result = ssh_remote_command("mlvc01@163.180.186.41:2222", "echo hello; echo hi")
        self.assertEqual(result, 
            {
                'entry': 'mlvc01@163.180.186.41:2222', 
                'command': 'echo hello; echo hi', 
                'result': [['hello'], ['hi']]
            })