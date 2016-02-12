import os


def get_app_url():
    url = 'http://api-tvprogram.rhcloud.com'
    return url if os.environ.get('OPENSHIFT_APP_DNS') else url + ':8080'
