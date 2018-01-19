# Discord Gacha

[![Python](https://img.shields.io/badge/python-3.5-blue.svg)](https://www.python.org/downloads/)

Discord Gacha is a Discord bot that allows users to open packs, similar to a gacha/lootbox system.

## Branches
The ``master`` branch contains then most recent stable version, whereas the ``develop`` branch contains the newest changes and may be unstable.

For the most stable performance, use the ``master`` branch.

## Database Configuration
Discord Gacha was designed to use [AWS DynamoDB](https://aws.amazon.com/dynamodb/). There are two types of tables used, tables containing set/card information and the table containing user information.

### Set/Card Tables
All of these attributes are expected to be present in order for the bot to function.
* ``rarity`` - ``String`` - Primary key; only expected values are `R`, `SR`, `UR`.
* ``cards`` - ``List`` - Attribute; contains ``Map``s with the following attributes:
    * ``image`` - ``String`` - URL to card image
    * ``name`` - ``String`` - Display name of card

### User Table
For the user table, only the primary key is needed. All other attributes will be automatically added as users use the bot. ``username`` and ``username_searchable`` are not used by the bot itself and are instead used by an accompanying web app.
* ``user_id`` - ``String`` - Primary key; unique user ID returned by Discord's API
* ``last_pack_opened`` - ``String`` - Datetime represented in ISO 8601 format.
* ``username`` - ``String`` - Discord username and ID number (ex. JohnSmith#1234)
* ``username_searchable`` - ``String`` - Discord username and ID but with no capitals (ex. johnsmith#1234)

## Configuration Files
Discord Gacha uses two configuration files, one for defining environment and application parameters and one for defining all available packs. These configuration files are expected to be in ``JSON`` format.

### Environment/Application Configuration
* ``token`` - ``String`` - Discord token used to allow bot to login
* ``hostname`` - ``String`` - Hostname to use when logging to LogDNA.
* ``ingestion_key`` - ``String`` - Ingestion key to use when logging to LogDNA
* ``dynamodb_endpoint`` - ``String`` - Endpoint for DynamoDB database
* ``users_table`` - ``String`` - Name of table containing user information

### Pack Configuration
The pack configuration file differs from the environment/application file in that it does not have set keys. The configuration's keys refer to objects with the following keys.

* ``table`` - ``String`` - Name of table containing set (pack) information
* ``name`` - ``String`` - Name of the set to be displayed

Sample:
```
{
    "pack": {
        "table": "table_name_1",
        "name": "Pack Name 1"
    },
    "pack2": {
        "table": "table_name_2",
        "name": "Pack Name 2"
    }
}
```

## Logging
Discord Gacha uses [LogDNA](https://logdna.com/) to handle logging. LogDNA allows logs to be viewed online and for objects containing relevant information to also be logged. Discord Gacha is untested if invalid LogDNA information is given in the configuration files.