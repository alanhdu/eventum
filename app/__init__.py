from flask import Flask
from flask.ext.mongoengine import MongoEngine

db = MongoEngine()
app = None


def create_app(**config_overrides):
    """This is normal setup code for a Flask app, but we give the option
    to provide override configurations so that in testing, a different
    database can be used.
    """
    # we want to modify the global app, not a local copy
    global app
    app = Flask(__name__)

    # Load config then apply overrides
    app.config.from_object('config')
    app.config.update(config_overrides)

    # Setup the database.
    db.init_app(app)


def register_blueprints():
    """Registers all the Blueprints (modules) in a function, to avoid
    circular dependancies.

    Be careful rearranging the order of the app.register_blueprint()
    calls, as it can also result in circular dependancies.
    """
    from app.mod_auth.controllers import mod_auth as auth_module
    from app.mod_base.controllers import mod_base as base_module
    from app.mod_learn.controllers import mod_learn as learn_module
    from app.mod_events.controllers import mod_events as events_module
    from app.mod_blog.controllers import mod_blog as blog_module
    from app.mod_networking.controllers import mod_networking as \
        networking_module

    app.register_blueprint(auth_module)
    app.register_blueprint(base_module)
    app.register_blueprint(learn_module)
    app.register_blueprint(events_module)
    app.register_blueprint(blog_module)
    app.register_blueprint(networking_module)

def run():
	app.run(host='0.0.0.0', port=5000)
