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


class OpenApiCli:

    API_CMD_LABEL = 'api'
    MODEL_CMD_LABEL = 'model'

    def __init__(self):
        self.called_cmd = ''
        self.called_api_name = ''
        self.called_method_name = ''
        self.called_args_list = {}
        self.called_type = ''
        self.api_manager = None

    def __callback_model_generator(self, model_name):
        def model_subparser_callback(args):
            self.called_cmd = OpenApiCli.MODEL_CMD_LABEL
            self.called_type = model_name
        return model_subparser_callback

    def __callback_api_generator(self, api_name, method_name, params):
        def api_subparser_callback(args):
            self.called_cmd = OpenApiCli.API_CMD_LABEL
            self.called_api_name = api_name
            self.called_method_name = method_name
            self.called_args_list = params
        return api_subparser_callback

    def __display_model_help(self, model_name):
        model_swagger_definition = self.api_manager.model_manager.get_model_swagger_definition(model_name)
        print(json.dumps(model_swagger_definition, indent=4))

    def __execute_api_method(self, api_name, method_name, param_list, args):
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

        self.api_manager = ApiManager(configuration)

        params = ()
        for param in param_list:
            value = getattr(args, param['name'])
            if param['type'] == 'str':
                params = (*params, value)
            else:
                params = (*params, json.loads(value))

        try:
            result = self.api_manager.get_api_method(api_name, method_name)(*params, **dict())
            if debug:
                print('body:')
            print(result)
        except swagger_client.rest.ApiException as ex:
            errprint('Exception: ' + str(ex))

    def __build_api_command_parser(self, parser, api_choice_list):
        api_parsers = parser.add_parser(OpenApiCli.API_CMD_LABEL)
        api_parsers.add_argument('-X', '--proxy', help='Proxy url (for example: \'http://localhost:8080\')')
        api_parsers.add_argument('-k', '--insecure', help='Disable SSL verification (use at your own risks!)',
                                 action='store_true')
        api_parsers.add_argument('-v', '--verbose', help='Display debug infos', action='store_true')
        authentication_group = api_parsers.add_mutually_exclusive_group(required=False)
        authentication_group.add_argument('--access_token', help='Access token')
        authentication_group.add_argument('--basic',
                                          help='Basic authentication. Format: \"{\"username\": '
                                               '\"the_user_name\", \"password\": \"the_password\"}\"')
        authentication_group.add_argument('--api_key', help='The API Key.')
        apis_subparsers = api_parsers.add_subparsers(title='API',
                                                     description='The API you want to interact with',
                                                     required=True)
        for api_choice in api_choice_list:
            api_parser = apis_subparsers.add_parser(api_choice)
            api_method_list = self.api_manager.get_api_method_list(api_choice)
            api_subparsers = api_parser.add_subparsers(title='Method',
                                                       description='The kind of interaction you want with your API',
                                                       required=True)
            for api_method in api_method_list:
                api_method_description = self.api_manager.get_method_description(api_choice, api_method)
                api_subparser = api_subparsers.add_parser(api_method, help=api_method_description)
                method_param = self.api_manager.get_method_parameters(api_choice, api_method)
                param_list = []
                for param in method_param:
                    api_subparser.add_argument('--' + param['name'].lower(),
                                               help='' + param['description'] + '  (type: ' + param['type'] + ')',
                                               required=True)
                    param_list.append({'name': param['name'].lower(),
                                       'type': param['type']})

                api_subparser.set_defaults(func=self.__callback_api_generator(api_choice, api_method, param_list))

        return api_parsers

    def __build_model_command_parser(self, parser):
        model_parsers = parser.add_parser(OpenApiCli.MODEL_CMD_LABEL)
        model_helper_subparser = model_parsers.add_subparsers(title='Model helper',
                                                              description='Model helper: display model expected format',
                                                              required=True)
        model_list = self.api_manager.model_manager.get_model_list()
        for model in model_list:
            model_parser = model_helper_subparser.add_parser(model)
            model_parser.set_defaults(func=self.__callback_model_generator(model))

        return model_parsers

    def run(self, argv):
        self.api_manager = ApiManager(swagger_client.Configuration())
        api_choice_list = self.api_manager.get_api_list()

        parser = argparse.ArgumentParser(description='Rest API command line interface.')

        subparsers = parser.add_subparsers(title='Command',
                                           description='The command',
                                           required=True)

        api_parsers = self.__build_api_command_parser(subparsers, api_choice_list)
        model_parsers = self.__build_model_command_parser(subparsers)

        argcomplete.autocomplete(parser)
        args = {}
        # argparse throw exception if there's only required subparse and no command is provided
        # we have to handle it ourselves.
        try:
            args = parser.parse_args(argv)
            args.func(args)
        except TypeError:
            if len(sys.argv) >= 2:
                if sys.argv[1] == OpenApiCli.MODEL_CMD_LABEL:
                    model_parsers.print_help()
                    exit(-1)
                else:
                    api_parsers.print_help()
                    exit(-1)
            parser.print_help()
            exit(-1)

        if self.called_cmd == OpenApiCli.MODEL_CMD_LABEL:
            self.__display_model_help(self.called_type)
        if self.called_cmd == OpenApiCli.API_CMD_LABEL:
            self.__execute_api_method(self.called_api_name, self.called_method_name, self.called_args_list, args)


if __name__ == "__main__":
    open_api_cli = OpenApiCli()
    open_api_cli.run(sys.argv[1:])
