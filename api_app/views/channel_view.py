from ..urls.blueprints import channel_bp
from flask import render_template
from ..constants.constants import ACTIVE_PAGES
from flask.ext.login import login_required


@channel_bp.route('/')
@login_required
def channel():

    return render_template('channel.html', active_page=ACTIVE_PAGES['channels'])
