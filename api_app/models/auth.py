from flask_oauth import OAuth
import urllib
import json
from flask import request
from utils.openshift import get_app_url

oauth = OAuth()


class RegisterSocNetwork:

    soc_networks = ('facebook', 'vkontakte', 'google')

    def __init__(self, service=None):
        self.service = service
        self.get_service = self.build(self.service)

    @staticmethod
    def build(service_name):
        service = False
        host = get_app_url()
        if service_name == 'facebook':
            service = oauth.remote_app('tvonline.in.ua',
                                       base_url='https://graph.facebook.com/',
                                       request_token_url=None, access_token_url='/oauth/access_token',
                                       authorize_url='https://www.facebook.com/dialog/oauth',
                                       consumer_key='1047252288640078',
                                       consumer_secret='8a1bdcf07a5fc98975775f36f947397a',
                                       request_token_params={'scope': 'email'})
        elif service_name == 'vkontakte':
            service = 'https://oauth.vk.com/authorize?client_id={client_id}&display=page&scope={scope}&redirect_uri=' \
                      '{redirect_url}&v=5.0&response_type=code'.format(
                       client_id='5145835', scope='email',
                       redirect_url='{host}/auth/vkontakte_login/authorized'.format(host=host))

        elif service_name == 'google':
            service = oauth.remote_app('google',
                                       base_url='https://www.google.com/accounts/',
                                       authorize_url='https://accounts.google.com/o/oauth2/auth',
                                       request_token_url=None,
                                       request_token_params={'scope': 'https://www.googleapis.com/auth/plus.login',
                                                             'response_type': 'code'},
                                       access_token_url='https://accounts.google.com/o/oauth2/token',
                                       access_token_method='GET',
                                       access_token_params={'grant_type': 'authorization_code'},
                                       consumer_key='382845359434-uv6dnoqibqb9pf0s1nvvfhdgrgv1gshl.'
                                                    'apps.googleusercontent.com',
                                       consumer_secret='1r7us2GYy-QS42BOnxnxSfTl')

        return service

    def get_token(self, code):
        url = ''
        host = get_app_url()
        if self.service == 'vkontakte':
            url = 'https://oauth.vk.com/access_token?client_id={client_id}&' \
                  'client_secret={client_secret}&redirect_uri={redirect_url}&code={code}'.format(
                       client_id='5145835', client_secret='910H8XhkfJs0qayNRKRM',
                       redirect_url='{host}/auth/vkontakte_login/authorized'.format(host=host), code=code)
        return json.load(urllib.urlopen(url))
