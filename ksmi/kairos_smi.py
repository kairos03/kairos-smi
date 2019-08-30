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
QUERY_APP = """
        a=($(nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader,nounits | awk '{print $1,$2,$3}' FS=', ' OFS=','))
        for item in $a
        do
            pid=$(echo $item | awk '{print $2}' FS=',') 
            ps=$(ps --noheader -o "pid,user,%cpu,%mem,etime,command" -p $pid)
            echo $item | awk '{printf "%s, %s, ", $1, $3}' FS="," RS="\n" 
            echo $ps | awk 'BEGIN {OFS=", "} {$1=$1; print}' RS="\n"
        done;
        """

#QUERY_APP = "nvidia-smi --query-compute-apps=gpu_uuid,pid,process_name,used_memory --format=csv,noheader"

def ssh_remote_command(entrypoint, command, timeout=1):

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
        out, err = ssh.communicate(timeout=timeout)
        #print(out, err)
        if err != b'':
            return {'status': 'Error', 'entry': entrypoint, 'command': command, 'data': postprocessing(err)}
        return {'status': 'Success', 'entry': entrypoint, 'command': command, 'data': postprocessing(out)}

    except subprocess.TimeoutExpired:
        ssh.kill()
        out, err = ssh.communicate()
        #print(out, err)
        return {'status': 'Timeout', 'entry': entrypoint, 'command': command, 'data': postprocessing(err)}

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

@DeprecationWarning
def display_gpu_status(hosts, data):
    """Display gpu status
    """
    for host in hosts:
        gpu_stat = data[host].get('gpus')
        app_stat = data[host].get('apps')
        active_gpus = len(set(app_info[0] for app_info in app_stat))
        
        # print gpu stat
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
            

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='config.json', help='set config file location')
    parser.add_argument('-p', '--process', action='store_true', help='show process details (e.g. username, used_memory, cpu util, execution time, command)')
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

    # init screen
    screen = ui.init_screen()
    while(True):
        result = get_gpus_status(HOSTS, timeout=2)

        key = screen.getch()
        if key == ord('q'):
            curses.endwin()
            break

        logging.debug("result {}".format(result))

        try:
            ui.display(screen, HOSTS, result, args.process)
        except curses.error:
            pass


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    finally:
        ui.cleanup_screen()
