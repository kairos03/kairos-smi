import unittest

from ksmi.kairos_smi import get_gpus_status

class test_get_gpu_status(unittest.TestCase):
    
    def setUp(self):
        self.hosts = ["mlvc07@163.180.186.49:2222"]
        self.wrong_hosts = ["test@123.123.123.123:2211"]
        self.timeout = 10

    def test_get_gpu_status_success(self):
        # success case
        results = get_gpus_status(self.hosts, self.timeout)
        #print(results)
        self.assertEqual(type(results), type({}))
        self.assertEqual(len(results), 1)
        self.assertTrue(self.hosts[0] in results.keys())
        for entry in results.keys():
            self.assertEqual(type(results[entry]), type({}))
            self.assertEqual(len(results[entry]), 2)
            self.assertTrue('gpus' in results[entry].keys())
            self.assertTrue('apps' in results[entry].keys())
            self.assertTrue(len(results[entry]['gpus']) != 0)
            self.assertTrue(len(results[entry]['apps']) != 0)
            # print(results[entry]['apps'])

    def test_get_gpu_status_fail(self):
        # fail case
        results = get_gpus_status(self.wrong_hosts, self.timeout)
        self.assertEqual(type(results), type({}))
        self.assertEqual(len(results), 1)
        self.assertTrue(self.wrong_hosts[0] in results.keys())
        for entry in results.keys():
            #print(results)
            self.assertEqual(type(results[entry]), type({}))
            self.assertEqual(len(results[entry]), 2)
            self.assertTrue('gpus' in results[entry].keys())
            self.assertTrue('apps' in results[entry].keys())
            self.assertTrue(len(results[entry]['gpus']) == 0)
            self.assertTrue(len(results[entry]['apps']) == 0)
            #print(results[entry]['apps'])

    # def test_display_gpu_status(self):
    #     result = get_gpus_status(self.hosts)
    #     display_gpu_status(self.hosts, result)

    #def test_main(self):
    #    main()
