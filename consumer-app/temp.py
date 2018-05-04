#!/usr/bin/python
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pwd
import os
from subprocess import call
from charmhelpers.core import host
from charmhelpers.core.hookenv import log, status_set, config
from charmhelpers.core.templating import render
from charms.reactive import when, when_not, set_flag, clear_flag, when_file_changed

@when('apache.available')
def finishing_up_setting_up_sites():
    #...
    set_flag('apache.start')

@when('apache.start')
def ready():
    host.service_reload('apache2')
    status_set('active', 'apache ready')

# hier niet joined?
@when('generic-database.available')
def request_type_of_db():
    """
    This function requests 1 type of database technology to a charm over the generic-database interface.
    To see the available functions on the endpoint object, refer to the requires.py file in the generic-database layer.
    The charm writer of an application that uses a generic-database should know 'at design time' the technology the application needs.

    FUTURE: maybe in a future version, the generic-database layer will offer the ability to pass a list of technologies.
    """
    
    endpoint = endpoint_from_flag('generic-database.available')
    if endpoint:
        endpoint.request("pgsql")
        status_set('maintenance', 'requesting pgsql')
        #clear_flag('generic-database.available')
        #set_flag('generic-database.pgsql.available')
    else:
        # endpoint is None
        log("Endpoint is None, in request_type_of_db function")

# if the request function gets a list of different technologies, multiple handlers need to be written, for each supported technology that is

@when('generic-database.pgsql.connected')
def pgsql_setup():
    """
    This function will share configuration details such as databasename, username, password.
    """
    pgsql = endpoint_from_flag('generic-database.pgsql.connected')
    if pgsql:
        #pgsql.pgsql_configure('...')
    else:
        log("Endpoint(pgsql) is None in pgsql_setup function")

    # set_flag('app.pgsql.waiting') <-- ?

@when('generic-database.pgsql.available')
def pgsql_render_config():
    """
    The generic-database represents a pgsql database. This function will render the config file in order to use the pgsql database.
    Configuration details: host(), port(), databasename(), user(), password() 
    """
    
    pgsql = endpoint_from_flag('generic-database.pgsql.available')

    render_template('app-config.j2', '/var/consumer-app/pgsqlconfig.php', {
        'db_host' : pgsql.host(),
        'db_port' : pgsql.port(),
        'db_name' : pgsql.databasename(),
        'db_user' : pgsql.user(),
        'db_pass' : pgsql.password(),
    })
    # clear_flag('app.pgsql.waiting') <-- ?
    set_flag('restart-app')


@when('restart-app')
def restart_app():
    host.service_reload('apache2')
    clear_flag('restart-app')
    status_set('active', 'app ready')