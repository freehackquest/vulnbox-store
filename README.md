# vulnbox-store

## Requirements

* python

## Installation

```
$ git clone %Your http link% ~/vulnbox-store.git
$ apt install apache # or apt install nginx
$ cd ~/vulnbox-store.git
$ ln -s `pwd`/html /var/www/html/vbs # make link from repository to web folder
$ ./build-html.py
```

How available you local vulnbox-store by http://localhost/vbs/

## Add new service

After add new service to services please run `./build-html.py`

## Install vbs

Linux:

```
$ sudo curl -L "https://vulnbox.store/vbs.py" -o /usr/local/bin/vbs
```

## Install some services

Download services you can manually from [https://vulnbox.store/](https://vulnbox.store/)
