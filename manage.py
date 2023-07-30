#!/usr/bin/env python3
import os
# from flask_migrate import Migrate, upgrade, migrate, init
# from flask_script import Manager, Shell
from app import create_app, db
from app.models import User, Post, Province, Cell
from config import config
import ml

config_name = os.getenv('FLASK_CONFIG') or 'default'
app = create_app(config_name)
# migratecmd = Migrate(app, db)
# manager = Manager(app)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User = User, Post=Post, Province=Province, ml=ml, config_name=config_name, Cell=Cell)

@app.cli.command()
def test():
    """Run the unit test."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@app.cli.command()
def drop():
    """Drop all table."""
    db.drop_all()

@app.cli.command()
def create():
    """Create all table."""
    db.create_all()
    # Role.insert_roles()

@app.cli.command()
def recreate():
    """Recreate all table."""
    drop()
    # migrate()
    # upgrade()
    create()

@app.cli.command()
def init_data():
    """Init data to db."""
    config[config_name].init_db(app, db)

@app.cli.command()
def generate_fake():
    """Generate fake data"""
    User.generate_fake(100)
    Post.generate_fake(1000)
    
@app.cli.command()
def runserver():
    # context = ('ssl.crt', 'ssl.key')
    # app.run(ssl_context=context, threaded=True)
    app.run(threaded=True)

@app.cli.command()
def deploy():
    create()
    # upgrade()
    init_data()

@app.cli.command()
def geolocation():
    pass
    # from geopy.geocoders import OpenCage
    # geolocator = OpenCage('d1d1fbc618ef41b89d3ebde37f53d1b2')
    # for p in Province.query.all():
    #     g = geolocator.geocode( p.name + ", Việt Nam", timeout=60)
    #     p.latitude = g.latitude
    #     p.longitude = g.longitude
    #     print((p.latitude, p.longitude))
    # db.session.commit()

# manager.add_command('shell', Shell(make_context=make_shell_context))
# manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    print(config_name)
    app.run()
    # manager.run()