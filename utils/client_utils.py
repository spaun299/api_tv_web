from flask import jsonify


def ajax_response(message=None, redirect_url=None, error=None, data=None, alert=None, reload_page=False):
    return jsonify(dict(message=message, redirect_url=redirect_url, error=error, data=data, alert=alert,
                        reload_page=reload_page))
