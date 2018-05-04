import pwd
import os
from subprocess import call
from charmhelpers.core import host
from charmhelpers.core.hookenv import log, status_set, config
from charmhelpers.core.templating import render
from charms.reactive import when, when_not, set_flag, clear_flag, when_file_changed

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
    status_set('maintenance', 'requesting pgsql db')


@when('pgsqldb.master.available', 'gdb.pgsql.requested')
def render_pgsql_config(pgsql):
    render('gdb-config.j2', '/var/www/generic-database-charm/gdb-config.html', {
        'db_master': pgsql.master,
    })
    clear_flag('gdb.pgsql.requested')
    set_flag('gdb.pgsql.available')
    set_flag('restart-app')

# todo ? config changed

@when('pgsqldb.master.available', 'gdb.pgsql.available')
def new_incoming_relation(pgsql):
    render('gdb-config.j2', '/var/www/generic-database-charm/gdb-config.html', {
        'db_master': pgsql.master,
    })
    set_flag('restart-app')

@when('restart-app')
def restart_app():
    host.service_reload('apache2')
    clear_flag('restart-app')
    status_set('active', 'app ready')
