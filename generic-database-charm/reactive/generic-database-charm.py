import pwd
import os
from subprocess import call
from charmhelpers.core import host
from charmhelpers.core.hookenv import log, status_set, config
from charmhelpers.core.templating import render
from charms.reactive import when, when_not, set_flag, clear_flag, when_file_changed

concrete_config = {}

@when('apache.available')
def finishing_up_setting_up_sites():
    host.service_reload('apache2')
    set_flag('apache.start')

@when('apache.start')
def ready():
    host.service_reload('apache2')
    status_set('active', 'apache ready')
    # temp to set flag here
    set_flag('gdb.pgsql.requested')


@when('pgsqldb.connected', 'gdb.pgsql.requested')
def request_db(pgsql):
    pgsql.set_database('mygdb_first')
    concrete_config['technology'] = "postgresql"
    status_set('maintenance', 'requesting pgsql db')


@when('pgsqldb.master.available', 'gdb.pgsql.requested')
def render_pgsql_config(pgsql):
    concrete_config['master'] = pgsql.master['master']
    concrete_config['user'] = pgsql.master['user']
    concrete_config['password'] = pgsql.master['password']
    concrete_config['port'] = pgsql.master['port']
    concrete_config['dbname'] = pgsql.master['dbname']
    
    render('gdb-config.j2', '/var/www/generic-database-charm/gdb-config.html', {
        'db_master': pgsql.master,
        'db_pass': pgsql.master['password'],
        'db_host': pgsql.master['dbname'],
        'db_user': pgsql.master['user'],
        'db_port': pgsql.master['port'],
    })
    clear_flag('gdb.pgsql.requested')
    set_flag('gdb.pgsql.available')
    set_flag('restart-app')

# todo ? config changed

@when('pgsqldb.master.available', 'gdb.pgsql.available')
def new_incoming_relation():
    # share details to new consumer
    render('gdb-config.j2', '/var/www/generic-database-charm/gdb-second.html', {
        'db_master': concrete_config['master'],
        'db_pass': concrete_config['password'],
        'db_host': concrete_config['dbname'],
        'db_user': concrete_config['user'],
        'db_port': concrete_config['port'],
    })
    set_flag('restart-app')

@when('restart-app')
def restart_app():
    host.service_reload('apache2')
    clear_flag('restart-app')
    status_set('active', 'app ready')
