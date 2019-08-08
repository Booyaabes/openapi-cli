# OpenAPI CLI

## Description

From an OpenAPI / Swagger you can generate a Python client. OpenAPI CLI is intended to make a CLI from this client.

## How to use

From an OpenAPI / Swagger generate a Python client. Add `open-api.cli.py` from the current repository to the generated client. You can now acces your API from your bash and pipe result to anything you want! Use tab for autocompletion.

## Bash completion activation

This project use [argcomplete](https://pypi.org/project/argcomplete/) to achieve bash completion. Please read argcomplete documentation about completion activation.

## Examples

Examples with [PetStore API](https://petstore.swagger.io/#/).

Help displays available API:

```sh
$ ./open-api-cli.py --help
usage: open-api-cli.py [-h] {PetApi,StoreApi,UserApi} ...

Rest API command line interface.

optional arguments:
  -h, --help            show this help message and exit

API:
  The API you want to interact with

  {PetApi,StoreApi,UserApi}
```

API help displays available actions:

```sh
$ ./open-api-cli.py PetApi --help
usage: open-api-cli.py PetApi [-h]
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
$ ./open-api-cli.py PetApi get_pet_by_id --help
usage: open-api-cli.py PetApi get_pet_by_id [-h] --pet_id PET_ID

optional arguments:
  -h, --help       show this help message and exit
  --pet_id PET_ID  ID of pet to return (type: int)
```

Example of usages, and return values:

```sh
$ ./open-api-cli.py PetApi get_pet_by_id --pet_id 1
{'category': {'id': 1, 'name': 'string'},
 'id': 1,
 'name': 'cat',
 'photo_urls': ['string'],
 'status': 'available',
 'tags': [{'id': 1, 'name': 'string'}]}
```

```sh
$ ./open-api-cli.py StoreApi get_inventory
{'sold': 193, 'ksks': 1, 'c': 1, 'string': 1, 'Operated': 4, 'unavailable': 2, 'velit ': 1, 'Nonavailable': 1, 'pending': 175, 'Not-Operated': 10, 'available': 345, 'PENDING': 1, 'Not Found': 1, '767778': 1, 'tempor labore n': 1, 'AVAILABLE': 1, 'swimming': 1, 'SOLD': 2, 'amet': 1, '{{petStatus}}': 1, 'Pending': 2, 'qwe': 1, 'Reserved': 1}
```

## TODO

- Handle authentication:
  - API key
  - Oauth
  - Basic or Digest ?
- add help for argument format (API Models)
- add unit tests
- add a better way to integrate with generated code
- add a ̀`requirements.txt` ?
