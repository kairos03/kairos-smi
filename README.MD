# kairos-smi
multi-server gpu moniroting program

```
usage: kairos-smi.py [-h] [-l] [-c CONFIG]

optional arguments:
  -h, --help            show this help message and exit
  -l, --loop            loop forever
  -c CONFIG, --config CONFIG
                        set config file location
```

# quick start
## 0. setup
### create rsa key
Create ssh public key. If you already has a key, you can skip this.
```shell
$ ssh-keygen
$ cat ~/.ssh/id_rsa.pub
```

### copy the public key to gpu server
Copy generated public key in your gpu server.

In server
```shell
$ echo [your-ssh-public-key] >> ~/.ssh/authorized_keys
$ cat ~/.ssh/authorized_keys
```

## 1. config
Edit `config.json`. Add your gpu server address in `config.json`.
```json
{
	"hosts": [
		"<username>@<host>[:port]",
		"<username>@<host>[:port]"
	]
}
```

## 2. run
```shell
$ python3 kairos-smi
```

