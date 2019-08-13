import unittest

from ksmi.kairos_smi import *

class test_kairos_smi(unittest.TestCase):
    
    def setUp(self):
        self.hosts = ["mlvcgpu@211.254.217.54:16022"]

    def test_ssh_remote_command(self):
        # success case
        result = ssh_remote_command('mlvcgpu@211.254.217.54:16022', 'echo hello; echo hi')
        self.assertEqual(result,
            {
                'status': 'Success',
                'entry': 'mlvcgpu@211.254.217.54:16022', 
                'command': 'echo hello; echo hi', 
                'data': [['hello'], ['hi']]
            })
        # success case
        result = ssh_remote_command('mlvcgpu@211.254.217.54:16022', QUERY_GPU)
        self.assertEqual(result['status'], 'Success')
        
        # fail case
        result = ssh_remote_command('test@1.1.1.1:2222', 'echo hello')
        self.assertEqual(result['status'], 'Timeout')

    def test_get_gpu_status_v2(self):
        # success case
        hosts = ["mlvcgpu@211.254.217.54:16022"]
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
            self.assertTrue(len(results[entry]['gpus']) != 0)
            self.assertTrue(len(results[entry]['apps']) != 0)
            # print(results[entry]['apps'])

        # fail case
        hosts = ["mlvcgpu@testtest:16022"]
        results = get_gpus_status_v2(hosts)
        print(results)
        self.assertEqual(type(results), type({}))
        self.assertEqual(len(results), 1)
        self.assertTrue(hosts[0] in results.keys())
        for entry in results.keys():
            self.assertEqual(type(results[entry]), type({}))
            self.assertEqual(len(results[entry]), 2)
            self.assertTrue('gpus' in results[entry].keys())
            self.assertTrue('apps' in results[entry].keys())
            self.assertTrue(len(results[entry]['gpus']) == 0)
            self.assertTrue(len(results[entry]['apps']) == 0)
            #print(results[entry]['apps'])

    def test_display_gpu_status(self):
        result = get_gpus_status_v2(self.hosts)
        display_gpu_status(self.hosts, result)

    def test_main(self):
        args = get_args()
        main(args)