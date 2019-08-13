import os
import subprocess
import sys
import json
from multiprocessing import Process, Queue
import argparse
import logging

logging.basicConfig(level=logging.ERROR)

# querys
QUERY_GPU = "nvidia-smi --query-gpu=timestamp,gpu_uuid,count,name,pstate,temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv,noheader"
QUERY_APP = "nvidia-smi --query-compute-apps=gpu_uuid,pid,process_name,used_memory --format=csv,noheader"


def ssh_remote_command(entrypoint, command):

    def postprocessing(data):
        return [x.split(', ') for x in data.decode('utf-8').split('\n')[:-1]]

    try:
        host, port = entrypoint.split(':')
    except ValueError:
        host, port = entrypoint, '22'

    ssh = subprocess.Popen(['ssh', host, '-p', port, command],
                       shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    try:
        out, _ = ssh.communicate(timeout=1)    
        return {'status': 'Success', 'entry': entrypoint, 'command': command, 'data': postprocessing(out)}

    except subprocess.TimeoutExpired:
        ssh.kill()
        _, err = ssh.communicate()
        return {'status': 'Timeout', 'entry': entrypoint, 'command': command, 'data': postprocessing(err)}
    

def get_gpus_status_v2(hosts):

    result = {}
    que = Queue(maxsize=100)
    procs = []

    def run_command_and_inque(q, host, query):
        result = ssh_remote_command(host, query)
        q.put(result)

    for host in hosts:
        for query in [QUERY_GPU, QUERY_APP]:
            proc = Process(target=run_command_and_inque, args=(que, host, query))
            proc.start()
            procs.append(proc)

    for proc in procs:
        proc.join()

    while not que.empty():
        item = que.get()
        entry = item.get('entry')
        item_type = 'apps' if item.get('command') == QUERY_APP else 'gpus'
        
        if entry not in result.keys():
            result[entry] = {}
        
        result[entry].update({item_type: item.get('data')})

    que.close()

    return result


def display_gpu_status(hosts, data):
    """Display gpu status
    """
    for host in hosts:
        gpu_stat = data[host]['gpus']
        app_stat = data[host]['apps']
        
        # print gpu stat
        # if gpu stat is empty
        print('[{:.30}]'.format(host), end='')
        if len(gpu_stat) == 0:
            print('\n|{}|'.format(' ERROR '), end='\n')
            continue
        else:
            print('{:>26}'.format("Running [{:2}/{:2}]".format(len(app_stat), len(gpu_stat))), end='\n')
        
        # print apps
        for i, gpu in enumerate(gpu_stat):
            print("| {} | Temp {:2s}C | Util {:>5s} | Mem {:>6s} / {:9s} |".format(i, gpu[5], gpu[6], gpu[7][:-4], gpu[8]))
            
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--loop', action='store_true', help='loop forever')
    parser.add_argument('-c', '--config', default='config.json', help='set config file location')
    args = parser.parse_args()
    return args

def main():
    args = get_args()
    
    try:
        with open(args.config, 'r') as f:
            conf = json.load(f)
    except FileNotFoundError:
        print("[ERROR] Config file '{}' not found.".format(args.config))
        exit()

    HOSTS = conf['hosts']

    while(True):
        result = get_gpus_status_v2(HOSTS)

        if args.loop:
            os.system('cls' if os.name == 'nt' else "printf '\033c'")

        logging.debug("result {}".format(result))
        display_gpu_status(HOSTS, result)
        
        if not args.loop:
            
            break


if __name__ == '__main__':
    main()
