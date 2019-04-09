# kairos-smi
Multi-server gpu moniroting program

![sample.png](img/sample.png)

```
usage: kairos-smi.py [-h] [-l] [-c CONFIG]

optional arguments:
  -h, --help            show this help message and exit
  -l, --loop            loop forever
  -c CONFIG, --config CONFIG
                        set config file location
```

# quick start
## 1. install 
Install with pip
```shell
$ pip install ksmi
or
$ pip3 install ksmi
```

## 2. Setup config file
Edit `config.json`. Add your gpu server address in `config.json`.
```json
{
	"hosts": [
		"<username>@<host>[:port]",
		"<username>@<host>[:port]"
	]
}
```

## 3. Add rsa_id to server

create new rea_id and add to your server

```shell
$ python3 -m ksmi.auto-copy-id -c ./config.json -n
```

## 4. Run It!
```shell
$ python3 -m ksmi.kairos-smi -l
```

