from flask import Blueprint

index_bp = Blueprint('index', __name__)
channel_bp = Blueprint('channel', __name__)
auth_bp = Blueprint('auth', __name__)
static_bp = Blueprint('static', __name__)
error_bp = Blueprint('error', __name__)

class Blueprints(object):

    def __init__(self, app):
        self.app = app

    def register(self):
        from ..views import index_view
        self.app.register_blueprint(index_bp, url_prefix='')
        from ..views import auth_view
        self.app.register_blueprint(auth_bp, url_prefix='/auth')
        from ..views import channel_view
        self.app.register_blueprint(channel_bp, url_prefix='/channel')
        from ..views import static_view
        self.app.register_blueprint(static_bp, url_prefix='/static')
        from ..views import error_view
        self.app.register_blueprint(error_bp, url_prefix='/error')

        return self.app
