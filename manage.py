#!/usr/bin/env python3
import os
from flask_migrate import Migrate, MigrateCommand, upgrade, migrate
from flask_script import Manager, Shell
from app import create_app, db, gravatar
from app.models import User, Post, Province
from config import config

config_name = os.getenv('FLASK_CONFIG') or 'default'
app = create_app(config_name)
migratecmd = Migrate(app, db)
manager = Manager(app)


def make_shell_context():
    return dict(db=db, User = User, Post=Post, Province=Province, gravatar=gravatar)

@manager.command
def test():
    """Run the unit test."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@manager.command
def drop():
    """Drop all table."""
    db.drop_all()

@manager.command
def create():
    """Create all table."""
    db.create_all()
    # Role.insert_roles()

@manager.command
def recreate():
    """Recreate all table."""
    drop()
    migrate()
    upgrade()
    create()

@manager.command
def init_data():
    """Init data to db."""
    config[config_name].init_db(app, db)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()