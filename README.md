Filament: A Fabric-based deployment tool for Flask
==================================================


Filament is still in its early stages. The goal of the
project is to provide an program *fil* that can execute
common tasks related to Flask application development.

The main task is to provide a framework for deployment
to the cloud without requiring a lot of setup. With just
a couple of short ini files in a filament directory in
your Flask project you can deploy a new VPS and set it
up within just one command.

Filament is intended to be used for production-ready
deployment, and so it deals with a lot of things that
aren't fun like your iptables setup and root security.

Filament was created to support the projects at Algorithmic.ly,
but I'm hoping it will be useful to others and that if anyone
finds it useful they might contribute back to it.

Status
======

Currently pre-alpha. Assistance is welcome. Don't use
in production. The project is only about 2 weeks old.

Usage
=====

Filament is pretty easy to use. You just need to create
a directory called filament in your project directory at
the same level as your flask file or module. Then, inside
that directory you need to put two files:

    filament/
        provider.ini
        uwsgi.ini

The provider.ini file looks like this:

    [Digital Ocean]
    client_id = [redacted]
    api_key   = [redacted]
    size      = 512MB
    image     = Ubuntu 13.04 x64
    region    = nyc2
    ssh_keys  = mysshkey

Each of the variables in provider.ini is directly tied to part of your
Digital Ocean account, so it should be easy to fill out. Currently
only Digital Ocean is supported, and testing has only been done with
Ubuntu 13.04, but support will be expanded to cover other providers
in the future.

The uwsgi.ini file contains your uwsgi variables and looks like this:

    [uwsgi]
    socket = /tmp/uwsgi-www.sock
    module = www
    callable = site
    processes = 4
    threads = 8
    stats = 127.0.0.1:9191

Where *module* and *callable* are used by filament to find your flask application.
For further information about uwsgi configuration, see the uWSGI docs.

To start a deployment once you have your ini files set up, wile in your working directory,
run this command:

    fil deploy
