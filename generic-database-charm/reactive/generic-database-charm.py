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


#@when('gdb.connected')
#def incomming_relation(gdb):
#    # determine the technology
#    if gdb.technology() == 'pgsql':
#        set_flag('gdb.pgsql.requested')
#    if gdb.technology() == 'mysql':
#        set_flag('gdb.mysql.requested')
#    if gdb.technology() == 'mongodb':
#        set_flag('gdb.mongodb.requested')
#    else
#        status_set('blocked', 'Could not determine technology')

@when('pgsqldb.connected', 'gdb.pgsql.requested')
def request_pgsqldb(pgsql):
    pgsql.set_database('mygdb_first')
    concrete_config['technology'] = "postgresql"
    status_set('maintenance', 'requesting pgsql db')


@when('pgsqldb.master.available', 'gdb.pgsql.requested')
def render_pgsql_config(pgsql):   
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

# todo config changed ?
# todo when new charms gets a new relation to this charm - share the details of the chosen db connection

@when('restart-app')
def restart_app():
    host.service_reload('apache2')
    clear_flag('restart-app')
    status_set('active', 'app ready')
