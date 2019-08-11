#!/usr/bin/python3
# PYTHON_ARGCOMPLETE_OK

import argparse
import json
import argcomplete
from swagger_client import api as api_list
from swagger_client import models
import swagger_client
import inspect
import sys


def errprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class ModelDescriptionManager:
    def __init__(self):
        self._models = dict()
        for model_name in [model_name for model_name in dir(models)
                           if not model_name.startswith('__')
                           and not (model_name == 'absolute_import')
                           and not callable(getattr(models, model_name))]:
            model = getattr(models, model_name)
            for class_name in [class_name for class_name in dir(model)
                               if inspect.isclass(getattr(model, class_name))]:
                self._models[class_name] = getattr(swagger_client, class_name)

    def get_model_list(self):
        return self._models.keys()

    def get_model(self, model_name):
        if model_name in self._models:
            return self._models[model_name]
        return None

    def get_model_swagger_definition(self, model_name):
        model = self.get_model(model_name)
        if model:
            return model.swagger_types
        return None


class ApiManager:
    def __init__(self, configuration):
        self.model_manager = ModelDescriptionManager()
        self.configuration = configuration
        self._apis = dict()
        for api_name in [api_name for api_name in dir(api_list)
                         if not api_name.startswith('__')
                         and not (api_name == 'absolute_import')
                         and not callable(getattr(api_list, api_name))]:
            api = getattr(api_list, api_name)
            for class_name in [class_name for class_name in dir(api)
                               if inspect.isclass(getattr(api, class_name))
                               and not class_name == 'ApiClient']:
                self._apis[class_name] = \
                    getattr(swagger_client, class_name)(swagger_client.ApiClient(self.configuration))

    def get_api(self, api_name):
        if api_name in self._apis.keys():
            return self._apis[api_name]
        return None

    def get_api_method(self, api_name, method_name):
        api = self.get_api(api_name)
        if api:
            if method_name in dir(api):
                return getattr(api, method_name)
        return None

    def get_method_description(self, api_name, method_name):
        method = self.get_api_method(api_name, method_name)
        docstring = method.__doc__.partition('\n')[0]
        string_to_delete = '  # noqa: E501'
        if docstring.endswith(string_to_delete):
            return docstring[:-len(string_to_delete)]
        return ""

    def get_method_parameters(self, api_name, method_name):
        method = self.get_api_method(api_name, method_name)
        docstring = method.__doc__
        param_list = []
        for line in [line for line in iter(docstring.splitlines())
                     if line.startswith(':param', 8)
                     and not line.endswith('async_req bool')]:
            param_line = line[15:]
            param_split = param_line.split(':')
            param_first_part = param_split[0]
            param_second_part = param_split[1]
            [param_type, param_name] = param_first_part.split(' ')
            param_required = True if param_second_part.endswith('(required)') else False
            param_description = param_second_part
            if param_required:
                param_description = param_description.split('(')[0][:-1]

            param_list.append({'name': param_name,
                               'type': param_type,
                               'description': param_description,
                               'required': param_required})
        return param_list

    def get_api_method_list(self, api_name, prefix=''):
        api_method_list = []
        api = self.get_api(api_name)
        if api:
            for method_name in [method_name for method_name in dir(api)
                                if not method_name.startswith('__')
                                and not method_name.endswith('_with_http_info')
                                and getattr(api, method_name)
                                and callable(getattr(api, method_name))
                                and (not prefix or method_name.startswith(prefix))]:
                api_method_list.append(method_name)

        return api_method_list

    def get_api_list(self):
        return self._apis.keys()


CALLED_CMD = ''
CALLED_API_NAME = ''
CALLED_METHOD_NAME = ''
CALLED_ARGS_LIST = ()
CALLED_TYPE = ''


def callback_model_generator(model_name):
    def model_subparser_callback(args):
        global CALLED_CMD
        CALLED_CMD = 'type'
        global CALLED_TYPE
        CALLED_TYPE = model_name
    return model_subparser_callback


def callback_api_generator(api_name, method_name, params):
    def api_subparser_callback(args):
        global CALLED_CMD
        CALLED_CMD = 'api'
        global CALLED_API_NAME
        CALLED_API_NAME = api_name
        global CALLED_METHOD_NAME
        CALLED_METHOD_NAME = method_name
        global CALLED_ARGS_LIST
        CALLED_ARGS_LIST = params
    return api_subparser_callback


api_manager = None


def display_model_help(model_name):
    model_swagger_definition = api_manager.model_manager.get_model_swagger_definition(CALLED_TYPE)
    print(json.dumps(model_swagger_definition, indent=4))


def execute_api_method(api_name, method_name, param_list, args):
    proxy = args.proxy
    verify_ssl = args.insecure
    debug = args.verbose
    access_token = args.access_token
    basic = args.basic
    if basic:
        basic = json.loads(basic)
    api_key = args.api_key

    configuration = swagger_client.Configuration()
    configuration.proxy = proxy
    configuration.verify_ssl = False if verify_ssl else True
    configuration.debug = True if debug else False
    if basic:
        configuration.username = basic.username
        configuration.password = basic.password
    if access_token:
        configuration.access_token = access_token
    if api_key:
        configuration.api_key['api_key'] = api_key

    global api_manager
    api_manager = ApiManager(configuration)

    params = ()
    for param in param_list:
        value = getattr(args, param['name'])
        if param['type'] == 'str':
            params = (*params, value)
        else:
            params = (*params, json.loads(value))

    try:
        result = api_manager.get_api_method(api_name, method_name)(*params, **dict())
        if debug:
            print('body:')
        print(result)
    except swagger_client.rest.ApiException as ex:
        errprint('Exception: ' + str(ex))


def main():
    global api_manager
    api_manager = ApiManager(swagger_client.Configuration())
    api_choice_list = api_manager.get_api_list()

    parser = argparse.ArgumentParser(description='Rest API command line interface.')
    parser.add_argument('-X', '--proxy', help='Proxy url (for example: \'http://localhost:8080\')')
    parser.add_argument('-k', '--insecure', help='Disable SSL verification (use at your own risks!)',
                        action='store_true')
    parser.add_argument('-v', '--verbose', help='Display debug infos', action='store_true')

    authentication_group = parser.add_mutually_exclusive_group(required=False)
    authentication_group.add_argument('--access_token', help='Access token')
    authentication_group.add_argument('--basic',
                                      help='Basic authentication. Format: \'{\'username\': '
                                           '\'the_user_name\', \'password\': \'the_password\'}\'')
    authentication_group.add_argument('--api_key', help='The API Key.')

    subparsers = parser.add_subparsers(title='Command',
                                       description='The command',
                                       required=True)

    api_parsers = subparsers.add_parser('api')
    apis_subparsers = api_parsers.add_subparsers(title='API',
                                                 description='The API you want to interact with',
                                                 required=True)

    # ---- Model helper
    model_parser = subparsers.add_parser('model')
    model_helper_subparser = model_parser.add_subparsers(title='Model helper',
                                                         description='Model helper: display model expected format',
                                                         required=True)
    model_list = api_manager.model_manager.get_model_list()
    for model in model_list:
        model_parser = model_helper_subparser.add_parser(model)
        model_parser.set_defaults(func=callback_model_generator(model))
    # ---- end model helper

    for api_choice in api_choice_list:
        api_parser = apis_subparsers.add_parser(api_choice)
        api_method_list = api_manager.get_api_method_list(api_choice)
        api_subparsers = api_parser.add_subparsers(title='Method',
                                                   description='The kind of interaction you want with your API',
                                                   required=True)
        for api_method in api_method_list:
            api_method_description = api_manager.get_method_description(api_choice, api_method)
            api_subparser = api_subparsers.add_parser(api_method, help=api_method_description)
            method_param = api_manager.get_method_parameters(api_choice, api_method)
            param_list = []
            for param in method_param:
                api_subparser.add_argument('--' + param['name'].lower(),
                                           help='' + param['description'] + '  (type: ' + param['type'] + ')',
                                           required=True)
                param_list.append({'name': param['name'].lower(),
                                   'type': param['type']})

            api_subparser.set_defaults(func=callback_api_generator(api_choice, api_method, param_list))

    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    args.func(args)

    if CALLED_CMD == 'type':
        display_model_help(CALLED_TYPE)
    else:
        execute_api_method(CALLED_API_NAME, CALLED_METHOD_NAME, CALLED_ARGS_LIST, args)


if __name__ == "__main__":
    main()
