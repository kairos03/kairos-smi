import unittest

from ksmi.kairos_smi import *

class test_kairos_smi(unittest.TestCase):
    def test_get_gpu_status_v2(self):
        # success case
        hosts = ["mlvc01@163.180.186.41:2222"]
        results = get_gpus_status_v2(hosts)
        #print(results)
        self.assertEqual(type(results), type({}))
        self.assertEqual(len(results), 1)
        self.assertTrue(hosts[0] in results.keys())
        for entry in results.keys():
            self.assertEqual(type(results[entry]), type({}))
            self.assertEqual(len(results[entry]), 2)
            self.assertTrue('gpus' in results[entry].keys())
            self.assertTrue('apps' in results[entry].keys())
            # print(results[entry]['apps'])
            # print(results[entry]['gpus'])


    def test_ssh_remote_command(self):
        # success case
        result = ssh_remote_command("mlvc01@163.180.186.41:2222", "echo hello; echo hi")
        self.assertEqual(result,
            {
                'entry': 'mlvc01@163.180.186.41:2222', 
                'command': 'echo hello; echo hi', 
                'result': [['hello'], ['hi']]
            })
    