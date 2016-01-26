from ..urls.blueprints import static_bp
from flask import send_file


@static_bp.route('/<string:file_name>')
def static(file_name):
    return send_file(file_name)
