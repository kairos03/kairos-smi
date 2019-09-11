import os
import sys
import json
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--identity', default='%s/.ssh/id_rsa.pub' % os.environ['HOME'], help='location of id_rsa key to add')
parser.add_argument('-n', '--new_id', action='store_true', help='generate new id_rsa key')
parser.add_argument('-c', '--config', default=None, help='set config file to use host list')
parser.add_argument('-s', '--server', default=None, help='set a server to copy id')
args = parser.parse_args()

os.environ['LogLevel'] = 'QUITE'

# generate new rsa_id key
if args.new_id:
    os.system('ssh-keygen')

if not os.path.isfile(args.identity):
    print("IDENTITIY FILE NOT FOUND. %s"% args.identity)

# set hosts
hosts = []
if args.config is not None:
    with open(args.config, 'r') as f:
        conf = json.load(f)

    hosts.extend(conf['hosts'])

if args.server is not None:
    hosts.append(args.server)

if hosts == []:
    print("NO HOST TO COPY ID")
    exit(-1)


for host in hosts:
    try:
        sp_host = host.split(':')
        ep, port = sp_host
    except ValueError:
        ep, port = host, '22'
    
    print('====[%s]====' % ep)
    script = ['ssh-copy-id', '-i', args.identity, '-p', port, ep]
    os.system(' '.join(script))
    print(' '.join(script))
    print(args.identity)    
    # copy_id = subprocess.Popen(script, 
    #                     env={'LogLevel': 'INFO'})

    # try:
    #     restult, err = copy_id.communicate(input=sys.stdin, timeout=10)
    # except:
    #     continue

    ssh = subprocess.Popen(["ssh", "-p", port, ep, 'cat .ssh/authorized_keys'],
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
    try:
        result, err = ssh.communicate(timeout=15)
        result = result.decode().split('\n')
        my_key = subprocess.check_output(['cat', '{}/.ssh/id_rsa.pub'.format(os.environ['HOME'])], universal_newlines=True)

        if my_key.strip() in result:
            print("[OK]")
        else:
            print("[ERROR] SSH KEY check fail.")

    except subprocess.TimeoutExpired:
        ssh.kill()
        _, error = ssh.communicate(timeout=5)
        print('[Error] SSH connection refused. {}'.format(error))
        continue
    
    finally:
        if not ssh.poll():
            ssh.terminate()
        print()
