# OpenAPI CLI

## Description

From an OpenAPI / Swagger you can generate a Python client. OpenAPI CLI is intended to make a CLI from this client.

## Requirements

- Python 3.7+
- argcomplete (tested with 1.10.0)

Or for the Docker version:

- Docker 1.13+

## How to use

First, you have to generate a Python client, from [Swagger Editor](https://editor.swagger.io/) or with [swagger-codegen](https://github.com/swagger-api/swagger-codegen). 

For example:

```sh
sudo docker run --rm -v ${PWD}:/local swaggerapi/swagger-codegen-cli:latest generate \
    -i https://petstore.swagger.io/v2/swagger.json \
    -l python \
    -o /local/out/python
```

Then you copy `open-api-cli.py` at the root directory of the generated Python client:

```sh
$ cp open-api-cli.py out/python/
$ cd out/python/
$ ./open-api-cli.py --help
```

If needed, you can add argcomplete in your generated Python client as follow:

```sh
$ echo "argcomplete" >> requirements.txt
[ ... or ... ]
$ echo "argcomplete >= 1.10.0" >> requirements.txt
```

And then install all needed requirements:

```sh
$ pip3 install -r requirements.txt
```

A Dockerfile is available to build a image that contains all needed requirements. You can build it as follow:

```sh
$ sudo docker build -t open-api-cli:0.1 .
```

To use it:

```sh
$ sudo docker run -it --rm -v $(pwd)/petstore-python-client:/app:ro open-api-cli:0.1
$ user@900e050de182:/app$ open-api-cli.py api StoreApi get_inventory 
{'sold': 15, 'string': 6, 'avaliable': 1, 'pending': 6, 'available': 204, 'HEHEHE': 1}
```

A automated build is available at [Docker Hub](https://hub.docker.com/r/booyaabes/open-api-cli):

```sh
$ sudo docker pull booyaabes/open-api-cli:latest
```

## Security Disclaimer

__Reminder__: If the OpenAPI/Swagger spec is obtained from an untrusted source, please make sure you've reviewed the spec before using Swagger Codegen to generate the API client, server stub or documentation as code injection may occur.

Don't expose your `open-api-cli.py` to not trusted user as one can inject Python object from command line arguments.

## Bash completion activation

This project use [argcomplete](https://pypi.org/project/argcomplete/) to achieve bash completion. Please read argcomplete documentation about completion activation.

## Examples

Examples with [PetStore API](https://petstore.swagger.io/#/).

Help displays available API:

```sh
$ ./open-api-cli.py --help
usage: open-api-cli.py [-h] {api,model} ...

Rest API command line interface.

optional arguments:
  -h, --help   show this help message and exit

Command:
  The command

  {api,model}
```

Type help displays defined types:

```sh
$ ./open-api-cli.py model --help
usage: open-api-cli.py model [-h]
                             {ApiResponse,Body,Body1,Category,Order,Pet,Tag,User}
                             ...

optional arguments:
  -h, --help            show this help message and exit

Model helper:
  Model helper: display model expected format

  {ApiResponse,Body,Body1,Category,Order,Pet,Tag,User}
```

Display Pet type format:

```sh
$ ./open-api-cli.py model Pet
{
    "id": "int",
    "category": "Category",
    "name": "str",
    "photo_urls": "list[str]",
    "tags": "list[Tag]",
    "status": "str"
}
```

Display the help to select an API:

```sh
$ ./open-api-cli.py api --help
usage: open-api-cli.py api [-h] [-X PROXY] [-k] [-v]
                           [--access_token ACCESS_TOKEN | --basic BASIC | --api_key API_KEY]
                           {PetApi,StoreApi,UserApi} ...

optional arguments:
  -h, --help            show this help message and exit
  -X PROXY, --proxy PROXY
                        Proxy url (for example: 'http://localhost:8080')
  -k, --insecure        Disable SSL verification (use at your own risks!)
  -v, --verbose         Display debug infos
  --access_token ACCESS_TOKEN
                        Access token
  --basic BASIC         Basic authentication. Format: '{'username':
                        'the_user_name', 'password': 'the_password'}'
  --api_key API_KEY     The API Key.

API:
  The API you want to interact with

  {PetApi,StoreApi,UserApi}
```

API help displays available actions:

```sh
$ ./open-api-cli.py api PetApi --help
usage: open-api-cli.py api PetApi [-h]
                                  {add_pet,delete_pet,find_pets_by_status,find_pets_by_tags,get_pet_by_id,update_pet,update_pet_with_form,upload_file}
                                  ...

optional arguments:
  -h, --help            show this help message and exit

Method:
  The kind of interaction you want with your API

  {add_pet,delete_pet,find_pets_by_status,find_pets_by_tags,get_pet_by_id,update_pet,update_pet_with_form,upload_file}
    add_pet             Add a new pet to the store
    delete_pet          Deletes a pet
    find_pets_by_status
                        Finds Pets by status
    find_pets_by_tags   Finds Pets by tags
    get_pet_by_id       Find pet by ID
    update_pet          Update an existing pet
    update_pet_with_form
                        Updates a pet in the store with form data
    upload_file         uploads an image
```

Action help displays arguments:

```sh
./open-api-cli.py api PetApi get_pet_by_id --help
usage: open-api-cli.py api PetApi get_pet_by_id [-h] --pet_id PET_ID

optional arguments:
  -h, --help       show this help message and exit
  --pet_id PET_ID  ID of pet to return (type: int)
```

Example of usages, and return values:

```sh
$ ./open-api-cli.py api PetApi get_pet_by_id --pet_id 1
{"id":1,"category":{"id":1,"name":"String"},"name":"String","photoUrls":["string"],"tags":[{"id":10,"name":"String"}],"status":"available"}
```

```sh
$ ./open-api-cli.py api StoreApi get_inventory
{"sold":5,"string":289,"alive":1,"Nonavailable":1,"pending":14,"available":657,"hehe":1,"adopted":1}
```

You can pipe the result to `jq`:

```shell
$ ./open-api-cli.py api PetApi find_pets_by_status --status '["available"]' | jq ".[0]"
{
  "id": 9222968140498485000,
  "category": {
    "id": 0,
    "name": "string"
  },
  "name": "fish",
  "photoUrls": [
    "string"
  ],
  "tags": [
    {
      "id": 0,
      "name": "string"
    }
  ],
  "status": "available"
}
```

## TODO

- ~~add the possibility to pass JSON object as cli arguement,~~
- Handle authentication:
  - ~~API key~~
  - ~~Oauth~~
  - ~~Basic~~
  - Cookie based auth? Maybe just add the possibility to add Cookie header, or any header?
- ~~add help for argument format (API Models). Add 'type' subparser?~~
- ~~add the possibility to change the host url~~
- add unit tests
- ~~Make `--host` mandatory, if default server url is not set in swagger,~~
- ~~add debug mode~~
- ~~add proxy support~~
- ~~add the possibility to disable SSL verification~~
- add a better way to integrate with generated code
- add a `requirements.txt` ?
