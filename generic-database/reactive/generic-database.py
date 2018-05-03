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

@when('pgsqldb.connected')
def request_db(pgsql):
    pgsql.set_database('mydb_one')
    status_set('maintenance', 'requesting pgsql db')

@when('config.changed')
def check_admin_pass():
    admin_pass = config()['admin-pass']
    if admin_pass:
        set_flag('admin-pass')
    else:
        clear_flag('admin-pass')

@when('pgsqldb.master.available', 'admin-pass')
def render_config(pgsql):
    render('pgsql-config.j2', '/var/www/pgsql/pgsqlconf.html', {
        'db_master': pgsql.master,
        'db_standbys': pgsql.standbys,
        'db_conn': pgsql.connection_string,
        'admin_pass': config('admin-pass'),
    })
    set_flag('restart-app')

@when('restart-app')
def restart_app():
    host.service_reload('apache2')
    clear_flag('restart-app')
    status_set('active', 'app ready')
