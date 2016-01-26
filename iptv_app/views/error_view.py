from ..urls.blueprints import error_bp
from flask import render_template


@error_bp.route('/<string:error>')
def error(error):
    return render_template('error.html', error=error)
