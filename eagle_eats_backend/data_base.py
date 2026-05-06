import sqlite3
from datetime import datetime
from .admin_init.create_admin import ensure_admin
from .admin_init.create_admin import ensure_base_kitchens, ensure_base_schedules, ensure_base_menu
import click
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types = sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    
    return g.db

def close_db(e = None):
    database_ref = g.pop('db', None) #returns data base reference or None

    if database_ref is not None:
        database_ref.close()

#Functions that will run sql commands
def init_db():
    data_base = get_db()
    with current_app.open_resource('EEschema.sql') as schema:
        data_base.executescript(schema.read().decode('utf8'))
    ensure_admin(data_base)
    ensure_base_schedules(data_base)
    ensure_base_kitchens(data_base)
    ensure_base_menu(data_base)

@click.command('init_db')
def init_db_command():
    #clear existing data and create new tables
    init_db()
    click.echo('Initialized the Database')

def init_app(app):
    app.teardown_appcontext(close_db) #close database on clean up
    app.cli.add_command(init_db_command)