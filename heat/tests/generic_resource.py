#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_log import log as logging
import six

from heat.common.i18n import _LW
from heat.engine import attributes
from heat.engine import constraints
from heat.engine import properties
from heat.engine import resource
from heat.engine.resources import signal_responder
from heat.engine.resources import stack_user

LOG = logging.getLogger(__name__)


class GenericResource(resource.Resource):
    '''
    Dummy resource for use in tests
    '''
    properties_schema = {}
    attributes_schema = {'foo': attributes.Schema('A generic attribute'),
                         'Foo': attributes.Schema('Another generic attribute')}

    def handle_create(self):
        LOG.warn(_LW('Creating generic resource (Type "%s")'),
                 self.type())

    def handle_update(self, json_snippet, tmpl_diff, prop_diff):
        LOG.warn(_LW('Updating generic resource (Type "%s")'),
                 self.type())

    def handle_delete(self):
        LOG.warn(_LW('Deleting generic resource (Type "%s")'),
                 self.type())

    def _resolve_attribute(self, name):
        return self.name

    def handle_suspend(self):
        LOG.warn(_LW('Suspending generic resource (Type "%s")'),
                 self.type())

    def handle_resume(self):
        LOG.warn(_LW('Resuming generic resource (Type "%s")'),
                 self.type())


class ResWithComplexPropsAndAttrs(GenericResource):

    properties_schema = {
        'a_string': properties.Schema(properties.Schema.STRING),
        'a_list': properties.Schema(properties.Schema.LIST),
        'a_map': properties.Schema(properties.Schema.MAP),
        'an_int': properties.Schema(properties.Schema.INTEGER)}

    attributes_schema = {'list': attributes.Schema('A list'),
                         'map': attributes.Schema('A map'),
                         'string': attributes.Schema('A string')}
    update_allowed_properties = ('an_int',)

    def _resolve_attribute(self, name):
        try:
            return self.properties["a_%s" % name]
        except KeyError:
            return None


class ResourceWithProps(GenericResource):
    properties_schema = {
        'Foo': properties.Schema(properties.Schema.STRING),
        'FooInt': properties.Schema(properties.Schema.INTEGER)}


class ResourceWithPropsAndAttrs(ResourceWithProps):
    attributes_schema = {'Bar': attributes.Schema('Something.')}


class ResourceWithResourceID(GenericResource):
    properties_schema = {'ID': properties.Schema(properties.Schema.STRING)}

    def handle_create(self):
        super(ResourceWithResourceID, self).handle_create()
        self.resource_id_set(self.properties.get('ID'))

    def handle_delete(self):
        self.mox_resource_id(self.resource_id)

    def mox_resource_id(self, resource_id):
        pass


class ResourceWithComplexAttributes(GenericResource):
    attributes_schema = {
        'list': attributes.Schema('A list'),
        'flat_dict': attributes.Schema('A flat dictionary'),
        'nested_dict': attributes.Schema('A nested dictionary'),
        'none': attributes.Schema('A None')
    }

    list = ['foo', 'bar']
    flat_dict = {'key1': 'val1', 'key2': 'val2', 'key3': 'val3'}
    nested_dict = {'list': [1, 2, 3],
                   'string': 'abc',
                   'dict': {'a': 1, 'b': 2, 'c': 3}}

    def _resolve_attribute(self, name):
        if name == 'list':
            return self.list
        if name == 'flat_dict':
            return self.flat_dict
        if name == 'nested_dict':
            return self.nested_dict
        if name == 'none':
            return None


class ResourceWithRequiredProps(GenericResource):
    properties_schema = {'Foo': properties.Schema(properties.Schema.STRING,
                                                  required=True)}


class SignalResource(signal_responder.SignalResponder):
    properties_schema = {}
    attributes_schema = {'AlarmUrl': attributes.Schema('Get a signed webhook')}

    def handle_create(self):
        super(SignalResource, self).handle_create()
        self.resource_id_set(self._get_user_id())

    def handle_signal(self, details=None):
        LOG.warn(_LW('Signaled resource (Type "%(type)s") %(details)s'),
                 {'type': self.type(), 'details': details})

    def _resolve_attribute(self, name):
        if name == 'AlarmUrl' and self.resource_id is not None:
            return six.text_type(self._get_signed_url())


class StackUserResource(stack_user.StackUser):
    properties_schema = {}
    attributes_schema = {}

    def handle_create(self):
        super(StackUserResource, self).handle_create()
        self.resource_id_set(self._get_user_id())


class ResourceWithCustomConstraint(GenericResource):
    properties_schema = {
        'Foo': properties.Schema(
            properties.Schema.STRING,
            constraints=[constraints.CustomConstraint('neutron.network')])}


class ResourceWithAttributeType(GenericResource):
    attributes_schema = {
        'attr1': attributes.Schema('A generic attribute',
                                   type=attributes.Schema.STRING),
        'attr2': attributes.Schema('Another generic attribute',
                                   type=attributes.Schema.MAP)
    }

    def _resolve_attribute(self, name):
        if name == 'attr1':
            return "valid_sting"
        elif name == 'attr2':
            return "invalid_type"
