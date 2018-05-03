# Proto-adminer: A basic php app that uses mysql



TODO add details when finished

# Roadmap, a getting started tutorial with the reactive framework in juju

## Introduction

..

## Juju - non reactive charms

..

## Layers, interfaces ...

..

## Use case: proto-adminer

### Situation

This paragraph will illustrate what we want to achieve with the "proto-adminer" charm. The name comes from prototyping and adminer (this refers to [adminer.php](https://www.adminer.org/)). Adminer is a single php file that allows users to interact with databasesystems. Think of a single-page phpmyadmin. 

The charm we are trying to create consists of 3 major components. First it needs to install a webserver, that becomes accessible. We will use apache. Then we will deploy an application (some php pages including adminer) on the webserver. And finally the application will interact with a database, mysql in this case.

Extra possibilities:
- populate database 
- a webapp (PoC) to help people choosing a database technology

### Design choices

Juju, the reactive framework and it's philosophies (OASIS TOSCA) all share the idea of reusability. They all want to be clear and easy to use. Therefore one of the requirements in this use case is to re-use as much as possible. The things we will use are:
- The [adminer](https://www.adminer.org/) php file
- The [apache](https://github.com/juju-solutions/layer-apache-php) base layer
- The [mysql-shared](https://github.com/openstack/charm-interface-mysql-shared) interface
- The [http](https://github.com/juju-solutions/interface-http) interface
- The existing [mysql](https://jujucharms.com/mysql/58) charm from the charm store

The ``metadata.yaml`` is a good starting point to visualise the interactions with the charm. The first few lines give some general metadata but the provides and requires are crucial for the structure of the charm. Note the **http** and **mysql-shared** interface. 

```yaml
name: proto-adminer
summary: Few Php pages + adminer.php on apache that require a mysql charm and use mysql-shared interface. 
maintainer: student <student@student-VirtualBox>
description: |
  This charm is meant as an example to work with layers, interfaces and the reactive framework. It uses the apache layer and the mysql-shared interface. Some php pages will be deployed (including adminer.php) and the mysql database will be populated as well. 
tags:
  - ops
subordinate: false
provides:
  website:
    interface: http
requires:
  mysqldatabase:
    interface: mysql-shared
```

Another small, but crucial, file is the ``layer.yaml``. We start from the basic layer, put the apache-php on top of it and use 2 interfaces.

```yaml
includes: ['layer:basic', 'layer:apache-php', 'interface:http', 'interface:mysql-shared']
```

The heart of the charm resides in the ``reactive/proto-adminer.py`` file:

```python
import pwd
import os
from subprocess import call
from charmhelpers.core.hookenv import log, status_set
from charmhelpers.core.templating import render
from charms.reactive import when, when_not, set_flag, clear_flag

# Http interface
@when('website.available')
def configure_website(website):
    website.configure(port=hookenv.config('port'))

@when('website.available', 'mysqldatabase.connected')
def request_db(database):
    database.configure('proto', 'admin', 'admin', prefix="proto")
    log("db requested")

@when('website.available', 'mysqldatabase.available')
def setup_app(mysql):
    render(source='mysql_configure.php',
        target='/var/www/proto-adminer/mysql_conf.php',
        owner='www-data',
        perms=0o775,
        context={
            'db': mysql,
        })
    log("in setup function")
    set_flag('website.start')
    status_set('maintenance', 'Setting up application')


@when('website.available')
@when_not('mysqldatabase.connected')
def no_mysql_relation():
    #set_flag('website.db.waiting')
    status_set('waiting', 'Waiting for mysql relation')


@when('mysqldatabase.connected')
@when_not('mysqldatabase.available')
def mysql_connected_but_waiting(mysql):
    #set_flag('website.db.waiting')
    status_set('waiting', 'Waiting for mysql service')

@when('website.started')
def apache_started():
    #clear_flag('website.db.waiting')
    status_set('active', 'Ready')
```
