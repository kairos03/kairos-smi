import subprocess
import json
from multiprocessing import Process, Queue

from . import queries


def write_and_flush(fd, string):
    assert isinstance(string, str)
    fd.write(string+'\n')
    fd.flush()


def new_ssh_connection(entrypoint, port=22, timeout=2):
    ssh = subprocess.Popen(['ssh', entrypoint, '-p', str(port), '-T', '-o','StrictHostKeyChecking=no'],
                       shell=False,
                       stdin=subprocess.PIPE,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE,
                       universal_newlines=True
                       )
    write_and_flush(ssh.stdin, "echo START")

    while True:
        line = ssh.stdout.readline()
        if line.strip() == 'START':
            break
        print(line.strip())

    # for line in iter(ssh.stdout.readline, ''):
    #     print(line.strip())
    #     if line.strip() == 'START':
    #         break
    return ssh


def close_connection(connection):
    connection.terminate()


def execute_remote_command(ssh, command):
    # type check
    assert isinstance(ssh, subprocess.Popen)
    assert isinstance(command, str)
    
    # send command
    command += ';echo DONE'
    write_and_flush(ssh.stdin, command)

    # get result
    lines = []
    # for line in iter(ssh.stdout.readline, ''):
    #     lines.append(line.strip())
    #     if line.strip() == 'DONE':
    #         ssh.stdout.flush()
    #         break
    while True:
        line = ssh.stdout.readline()
        if line.strip() == 'DONE':
            break
        print(line.strip())

    return lines
