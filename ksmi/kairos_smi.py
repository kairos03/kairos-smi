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

# process detail query interval
APP_DETAIL_QUERY_INTERVAL = 10

def postprocessing(data, type='ssh'):
    if type == 'ssh':

        return [x.split(', ') for x in data.decode('utf-8').split('\n')[:-1]]
    elif type == 'ps':
        return data.decode('utf-8').split('\n')[:-1]

def ssh_remote_command(entrypoint, command, type='ssh'):

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
        return {'status': 'Success', 'entry': entrypoint, 'command': command, 'data': postprocessing(out, type)}

    except subprocess.TimeoutExpired:
        ssh.kill()
        _, err = ssh.communicate()
        return {'status': 'Timeout', 'entry': entrypoint, 'command': command, 'data': postprocessing(err, type)}
    

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

def get_apps_status(hosts, data):


    apps_status_result = {}

    def run_command_query_process_details(q, host, query):
        result = ssh_remote_command(host, query, 'ps')
        q.put(result)

    for host in hosts:
        gpu_stat = data[host]['gpus']
        app_stat = data[host]['apps']
        
        # print apps
        for i, gpu in enumerate(gpu_stat):

            gpu_uuid = gpu[1]
            if host not in apps_status_result.keys():
                apps_status_result[host] = {}

            if gpu_uuid not in apps_status_result[host].keys():
                apps_status_result[host][gpu_uuid] = []

            nvidia_app_infos = []
            ps_infos = Queue(maxsize=100)
            
            # for fast search 
            used_indices = []
            if True:
                for i, app in enumerate(app_stat):
                    # if app's gpu is same as current gpu
                    if app[0] == gpu[1]:
                        nvidia_app_infos.append(app)
                        used_indices.append(i)
                

                pids = [app[1] for app in nvidia_app_infos]
                pids_cat = " ".join(pids)           
                que = Queue(maxsize=100)
                query = "ps -o user=,command= -p {:s}".format(pids_cat)
                proc = Process(target=run_command_query_process_details, args=(que, host, query))
                proc.start()
                proc.join()
                        
                apps_detail = que.get().get('data')
                for i, app in enumerate(nvidia_app_infos):
                    app_detail = apps_detail[i]
                    username, command = app_detail.split(' ')[0], ''.join(app_detail.split(' ')[1:])
                    apps_status_result[host][gpu_uuid].append([app[1], username, app[3], command])

                # for fast search, delete already searched processes

                app_stat = [app for idx, app in enumerate(app_stat) if idx not in used_indices]
            # print processes
    return apps_status_result

def display_gpu_status(hosts, data, app_data):
    """Display gpu status
    """


    def run_command_query_process_details(q, host, query):
        result = ssh_remote_command(host, query, 'ps')
        q.put(result)

    for host in hosts:
        gpu_stat = data[host]['gpus']
        app_stat = data[host]['apps']
        
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
            # for fast search 
            if app_data:
                nvidia_app_infos = []
                ps_infos = Queue(maxsize=100)
                if gpu[1] in app_data[host].keys():
                    for i, app in enumerate(app_data[host][gpu[1]]):
                        if i == len(app_data[host][gpu[1]]) - 1:
                            print("\t└── process PID {:s} | Username {:s} | used_memory {:s} ".format(app[0], app[1], app[2]))
                        else:
                            print("\t├── process PID {:s} | Username {:s} | used_memory {:s} ".format(app[0], app[1], app[2]))
                    
                        
            
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--loop', action='store_true', help='loop forever')
    parser.add_argument('-c', '--config', default='config.json', help='set config file location')
    parser.add_argument('-p', '--process', action='store_true', help='watch process details (PID, owner, memory, etc)')
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
    APP_DETAIL_QUERY_INTERVAL = 10

    num_it = 0
    while(True):
        result = get_gpus_status_v2(HOSTS)

        if args.process:
            if num_it % APP_DETAIL_QUERY_INTERVAL == 0:
                app_result = get_apps_status(HOSTS, result)
        else:
            app_result = None

        if args.loop:
            os.system('cls' if os.name == 'nt' else "printf '\033c'")

        logging.debug("result {}".format(result))

        display_gpu_status(HOSTS, result, app_result)
        
        if not args.loop:
            
            break
        num_it += 1

if __name__ == '__main__':
    main()
