import unittest

from ksmi.kairos_smi import *

class test_kairos_smi(unittest.TestCase):
    
    def setUp(self):
        self.hosts = ["mlvcgpu@211.254.217.54:16022"]

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
        #print(results)
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

    #def test_main(self):
    #    main()