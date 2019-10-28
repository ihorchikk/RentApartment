RentApartment
====================

Local install
-------------

1. Setup and activate a python3.5 virtualenv via your preferred method. e.g. and install production requirements:

::

    $ make ve

2. or install dev requirements too:

::

    $ make dev
    
    
Scrapy process
=================

Run ``scrapy crawl`` from spider folder:

::

    $ scrapy crawl {spider-name}

Directory layout
================


    ria_ua_crawler
    ├── settings_server.ini
    └── ria_ua_crawler
            ├── items.py
            ├── middlewares.py
            ├── piplines.py
            ├── settings.py
            └── spiders
                    └── dom_ria_com.py
    

**Create settings_server.ini file in ria_ua_crawler/ folder for scrapy project to setup config**


        
        [PG]
        PG_DB_NAME=Postgres database name
        PG_TB_NAME=Postgres table name
        PG_USER=Postgres user
        PG_HOST=Postgres host
        PG_PASS=Postgres password
        
        [ES]
        ES_SOCKET=Elasticsearch socket

Web-Application process
=========================

Run application local:

`python3 manage.py runserver {socket}`


Run tests:

`python3 manage.py test`


Directory layout
================


    webapp/
    ├── flats
    │    ├── admin.py
    │    ├── apps.py
    │    ├── forms.py
    │    ├── models.py
    │    ├── tests.py
    │    ├── urls.py
    │    ├── utils.py
    │    ├── views.py
    │    └── templates 
    ├── webapp
    │    ├── settings.py
    │    ├── urls.py
    │    └── wsgi.py
    ├── manage.py
    └── settings_server.ini
    
 
**Create settings_server.ini file in webapp/ folder for webapp project to setup config**

        [PG]
        PG_DB_NAME=Postgres database name
        PG_TB_NAME=Postgres table name
        PG_USER=Postgres user
        
        [ES]
        ES_SOCKET=Elasticsearch socket
        ES_INDEX=Elasticsearch index
        
        [Django]
        ITEMS_PER_PAGE = Count of items per page

