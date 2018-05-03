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

from charms.reactive import Endpoint
from charms.reactive import when, when_not
from charms.reactive import set_flag, clear_flag
from charms.reactive import data_changed

class GenericDatabaseClient(Endpoint):
    
    @when('endpoint.{endpoint_name}.joined')
    def _handle_joined(self):
        set_flag(self.expand_name('{endpoint_name}.available'))

    @when('endpoint.{endpoint_name}.joined')
    def _handle_concrete(self):
        """
        Concrete is the term used to illustrate that a certain technology has been chosen. In other words the generic database isn't generic anymore.
        """
        technology = endpoint.all_units.received['technology']
        
        if technology:
            set_flag(self.expand_name('{endpoint_name}.{technology}.ready)

    def request(self, technology):
        to_publish['technology'] = technology

    def mysql_configure(self, dbname, dbuser='admin', dbpass='admin'):
        """
        host & port are determined by the service
        databasename, user and password are determined by requesting charm
        """
        to_publish['databasename'] = dbname
        to_publish['user'] = dbuser
        to_publish['password'] = dbpass


    def technology(self):
        """
        Return the technology of the generic database.
        """
        return self.all_joined_units.received['technology']

    def concrete_connection_string(self):
        """
        Returns the chosen, concrete connection string
        """
        if self.mysql_connection_string:
            return self.mysql_connection_string
        if self.postgresql_connection_string:
            return self.postgresql_connection_string
        if self.mongodb_connection_string:
            return self.mongodb_connection_string

    def mysql_connection_string(self):
        """
        Returns myqsl connection_string if mysql otherwise None.
        The connection string will be in the format::
            'host={host} port={port} dbname={database} '
            'user={user} password={password}'
        """
        if self.technology() == 'mysql':
            data = {
            'host': self.host(),
            'port': self.port(),
            'database': self.databasename(),
            'user': self.user(),
            'password': self.password(),
            }
            if all(data.values()):
                return str.format(
                    'host={host} port={port} dbname={database} '
                    'user={user} password={password}',
                    **data)
            return None

    def postgresql_connection_string(self):
        """
        Returns postgresql connection_string if postgresql otherwise None.
        """
        # TODO
        return None

    def mongodb_connection_string(self):
        """
        Returns mongodb connection_string if mongodb otherwise None.
        """
        # TODO
        return None

    def databasename(self):
        """
        Return the name of the provided database.
        """
        return self.all_joined_units.received['database']

    def host(self):
        """
        Return the host for the provided database.
        """
        return self.all_joined_units.received['host']

    def port(self):
        """
        Return the port the provided database.
        """
        return self.all_joined_units.received['port']

    def user(self):
        """
        Return the username for the provided database.
        """
        return self.all_joined_units.received['user']

    def password(self):
        """
        Return the password for the provided database.
        """
        return self.all_joined_units.received['password']

    # as an example of something that wont be implemented yet
    def keyspace(self):
        """
        Return the keyspace for the provided database. Cfr Cassandra.
        """
        return self.all_joined_units.received['keyspace']

        
