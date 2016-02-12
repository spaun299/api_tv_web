from ..urls.blueprints import index_bp
from flask import render_template, g
from ..constants.constants import ACTIVE_PAGES


@index_bp.route('/')
@index_bp.route('/index')
def index():
    return render_template('index.html', active_page=ACTIVE_PAGES['main'])
