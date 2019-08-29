import os
import subprocess
import sys
import json
from multiprocessing import Process, Queue
import argparse
import logging
import curses

try: 
    from . import ui
except ImportError:
    import ui

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

def ssh_remote_command(entrypoint, command, timeout=1, type='ssh'):

    try:
        host, port = entrypoint.split(':')
    except ValueError:
        host, port = entrypoint, '22'

    ssh = subprocess.Popen(['ssh', host, '-p', port, command],
                       shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    try:
        out, err = ssh.communicate(timeout=timeout)
        #print(out, err)
        if err != b'':
            return {'status': 'Error', 'entry': entrypoint, 'command': command, 'data': postprocessing(err, type)}
        return {'status': 'Success', 'entry': entrypoint, 'command': command, 'data': postprocessing(out, type)}

    except subprocess.TimeoutExpired:
        ssh.kill()
        out, err = ssh.communicate()
        #print(out, err)
        return {'status': 'Timeout', 'entry': entrypoint, 'command': command, 'data': postprocessing(err, type)}

    except KeyboardInterrupt:
        pass

def get_gpus_status(hosts, timeout=1):

    result = {}
    que = Queue(maxsize=100)
    procs = []

    def run_command_and_inque(q, host, query):
        result = ssh_remote_command(host, query, timeout=timeout)
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
        
        # new entry check
        if entry not in result.keys():
            result[entry] = {}

        # error data check
        data = {}
        if item['status'] == 'Success':
            data = item.get('data')

        result[entry].update({item_type: data})

    que.close()

    return result

def get_apps_status(hosts, data, timeout=1):


    apps_status_result = {}

    def run_command_query_process_details(q, host, query):
        result = ssh_remote_command(host, query, timeout=timeout, type='ps')
        q.put(result)

    for host in hosts:
        gpu_stat = data[host]['gpus']
        app_stat = data[host]['apps']
        
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
                username, command = app_detail.split(" ", 1)
                apps_status_result[host][gpu_uuid].append([app[1], username, app[3], command])

            # for fast search, delete already searched processes

            app_stat = [app for idx, app in enumerate(app_stat) if idx not in used_indices]
            # print processes
    return apps_status_result


@DeprecationWarning
def display_gpu_status(hosts, data, app_data, target_user=None):
    """Display gpu status
       params: target_user => display all the processes by "target_user"
    """

    def run_command_query_process_details(q, host, query):
        result = ssh_remote_command(host, query, 'ps')
        q.put(result)

    for host in hosts:
        gpu_stat = data[host].get('gpus')
        app_stat = data[host].get('apps')
        active_gpus = len(set(app_info[0] for app_info in app_stat))
        
        # if gpu stat is empty
        print('[{:.30}]'.format(host), end='')
        if gpu_stat == None or app_stat == None or len(gpu_stat) == 0:
            print('\n|{}|'.format(' ERROR '), end='\n')
            continue
        else:
            print('{:>26}'.format("APPs [{:2}] GPUs [{:2}/{:2}]".format(len(app_stat), active_gpus, len(gpu_stat))), end='\n')
        
        # print apps
        for i, gpu in enumerate(gpu_stat):
            if len(gpu) != 9:
                continue
            print("| {} | Temp {:2s}C | Util {:>5s} | Mem {:>6s} / {:9s} |".format(i, gpu[5], gpu[6], gpu[7][:-4], gpu[8]))
            # for fast search 
            if app_data:
                nvidia_app_infos = []
                ps_infos = Queue(maxsize=100)
                if gpu[1] in app_data[host].keys():
                    for i, app in enumerate(app_data[host][gpu[1]]):
                        if target_user is not None:
                            if target_user == app[1]:
                                print("\t└── process PID {:s} | Username {:s} | command {:s} ".format(app[0], app[1], app[3]))

                        else:
                            print("\t└── process PID {:s} | Username {:s} | used_memory {:s} ".format(app[0], app[1], app[2]))
                    
                        
            

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='config.json', help='set config file location')
    parser.add_argument('-p', '--process', action='store_true', help='watch process details (PID, owner, memory, etc)')
    parser.add_argument('-u', '--user', default=None, help='find all the processes by username')
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
        result = get_gpus_status(HOSTS)

        if args.process:
            if num_it % APP_DETAIL_QUERY_INTERVAL == 0:
                app_result = get_apps_status(HOSTS, result)
        else:
            app_result = None

        if args.loop:
            os.system('cls' if os.name == 'nt' else "printf '\033c'")

        logging.debug("result {}".format(result))

        display_gpu_status(HOSTS, result, app_result, args.user)
        
        if not args.loop:
            
            break
        num_it += 1
    """
    # init screen
    screen = ui.init_screen()
    while(True):
        result = get_gpus_status(HOSTS)

        key = screen.getch()
        if key == ord('q'):
            curses.endwin()
            break

        logging.debug("result {}".format(result))
        try:
            ui.display(screen, HOSTS, result)
        except curses.error:
            pass

    """

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    finally:
        ui.cleanup_screen()
