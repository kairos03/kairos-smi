import unittest

from ksmi.kairos_smi import get_gpus_status

class test_get_gpu_status(unittest.TestCase):
    
    def setUp(self):
        self.success_hosts = ["success@111.111.111.111:22"]
        self.error_hosts = ["error@123.123.123.123:2211"]
        self.timeout = 10
        self.success_return = {
            "success@111.111.111.111:22":{
                "gpus":[['2019/08/30 18:36:43.366', 'GPU-744c553a-2cfe-636a-9a49-ef88a4de14f4', '4', 'GeForce GTX 1080 Ti', 'P8', '29', '0 %', '1 MiB', '11178 MiB'], 
                        ['2019/08/30 18:36:43.370', 'GPU-3c7715ab-2204-60a3-bf01-accb2360644f', '4', 'GeForce GTX 1080 Ti', 'P2', '62', '100 %', '4347 MiB', '11178 MiB'], 
                        ['2019/08/30 18:36:43.372', 'GPU-94405968-473a-6e5f-4002-ba9e6243091d', '4', 'GeForce GTX 1080 Ti', 'P2', '62', '99 %', '4421 MiB', '11178 MiB'], 
                        ['2019/08/30 18:36:43.387', 'GPU-2fd0b93b-1d0f-cce9-c282-fdc43ab5eeb0', '4', 'GeForce GTX 1080 Ti', 'P8', '39', '0 %', '1 MiB', '11175 MiB']], 
                'apps': [['GPU-3c7715ab-2204-60a3-bf01-accb2360644f', '2275', '24827', 'youmin', '99.3', '3.8', '04:25:31', 'python3', './train.py', '--type', 'cifar100', '--model', 'resnet56', '--augtype', 'puzzle6_4', '--tn', 'ox_100_2'], 
                        ['GPU-3c7715ab-2204-60a3-bf01-accb2360644f', '2061', '5753', 'mlvcgpu', '99.1', '4.2', '03:14:16', 'python3', 'train_CIFAR10.py', '-act', 'PRELU3', '-net', 'resnet', '-resume', 'no'], 
                        ['GPU-94405968-473a-6e5f-4002-ba9e6243091d', '2275', '8736', 'youmin', '99.2', '3.8', '04:25:03', 'python3', './train.py', '--type', 'cifar100', '--model', 'resnet56', '--augtype', 'puzzle6_4', '--tn', 'ox_100_3'], 
                        ['GPU-94405968-473a-6e5f-4002-ba9e6243091d', '2135', '25653', 'mlvcgpu', '99.3', '4.2', '02:49:49', 'python3', 'train_CIFAR10.py', '-act', 'PRELU4', '-error', '0.09', '-net', 'resnet']]
            }
        }

    def test_get_gpu_status_success(self):
        # success case
        results = get_gpus_status(self.success_hosts, self.timeout)
        print(results)
        self.assertEqual(type(results), type({}))
        self.assertEqual(len(results), 1)
        self.assertTrue(self.success_hosts[0] in results.keys())
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
        results = get_gpus_status(self.error_hosts, self.timeout)
        self.assertEqual(type(results), type({}))
        self.assertEqual(len(results), 1)
        self.assertTrue(self.error_hosts[0] in results.keys())
        for entry in results.keys():
            #print(results)
            self.assertEqual(type(results[entry]), type({}))
            self.assertEqual(len(results[entry]), 2)
            self.assertTrue('gpus' in results[entry].keys())
            self.assertTrue('apps' in results[entry].keys())
            self.assertTrue(len(results[entry]['gpus']) == 0)
            self.assertTrue(len(results[entry]['apps']) == 0)
            #print(results[entry]['apps'])

    @unittest.skip("skip when unittest")
    def test_real(self):
        results = get_gpus_status(["mlvc03@mlvc03:2222"], self.timeout)
        print(results)