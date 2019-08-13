import os
import sys
import json
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--new_id', action='store_true', help='generate new id_rsa key')
parser.add_argument('-c', '--config', default=None, help='set config file to use host list')
parser.add_argument('-s', '--server', default=None, help='set a server to copy id')
args = parser.parse_args()

# generate new rsa_id key
if args.new_id:
    os.system('ssh-keygen')

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
    except KeyError:
        ep, port = host, 22

    os.system('ssh-copy-id {} -p {}'.format(ep, port))

    ssh = subprocess.Popen(["ssh", "-p", port, ep, 'cat ~/.ssh/authorized_keys'],
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    if result == []:
        error = ssh.stderr.readlines()[0].decode('utf-8')
        raise Exception('SSH connection refused. {}'.format(error))
        # print (sys.stderr, "ERROR: %s" % error)
    else:
        my_key = subprocess.check_output(['cat', '{}/.ssh/id_rsa.pub'.format(os.environ['HOME'])], universal_newlines=True)
        my_key = my_key.split(' ')
        for i, key in enumerate(result):
            result[i] = key.decode('utf-8').split(' ')[1]

        if my_key[1] in result:
            print("[OK] {}".format(host))
        else:
            print("[Fail] {}".format(host))
