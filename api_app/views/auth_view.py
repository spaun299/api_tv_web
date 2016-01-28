#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ..urls.blueprints import auth_bp
from flask import render_template, request, redirect, url_for, g, current_app, flash, jsonify, \
    session
from flask.ext.login import login_user, current_user, logout_user
from ..models.user import User
from db_init import db_query
from flask_user.views import _call_or_get, _endpoint_url, _send_registered_email, signals
from sqlalchemy.exc import IntegrityError
from flask_user.passwords import verify_password
from ..models.auth import RegisterSocNetwork
import datetime
from utils.client_utils import ajax_response
from sqlalchemy import or_
import json
import urllib
from oauth2client import client
from utils.openshift import get_app_url
import os
from exceptions import IOError


facebook = RegisterSocNetwork(service='facebook').get_service
vkontakte = RegisterSocNetwork(service='vkontakte')


@auth_bp.route('/login', methods=['POST'])
def login():
    """ Prompt for username/email and password and sign the user in."""
    user_manager = current_app.user_manager
    db_adapter = user_manager.db_adapter
    data = request.form
    next = request.args.get('next', _endpoint_url(user_manager.after_login_endpoint))
    reg_next = request.args.get('reg_next', _endpoint_url(user_manager.after_register_endpoint))

    # Immediately redirect already logged in users

    if _call_or_get(current_user.is_authenticated) and user_manager.auto_login_at_login:
        return redirect(next)
    user = None
    user_email = None

    # user = user_manager.find_user_by_username(data.get('user_name'))
    user = db_query(User).filter(or_(User.email == data.get('user_name'),
                                     User.username == data.get('user_name'))).first()
    if not user:
        return ajax_response(message="Ви ввели невірний логін або пароль")
    else:
        if user.password:
            if not verify_password(user_manager, data.get('password'), user.password):
                user = None
                return ajax_response(message="Ви ввели невірний логін або пароль")
        else:
            return ajax_response(message="Ви ввели невірний логін або пароль")
    user_email = None
    session['login_via'] = request.host
    remember_me = True if data.get('remember_me') else False
    if user and db_adapter.UserEmailClass:
        user_email = db_adapter.find_first_object(db_adapter.UserEmailClass,
                                                  user_id=int(user.get_id()), is_primary=True, )
    if not user and user_manager.enable_email:
        user, user_email = user_manager.find_user_by_email(data.get('user_name'))
    if user:
        _do_login_user(user, request.referrer, remember_me=remember_me)
    return ajax_response(message="Ви були успішно залоговані", reload_page = True)


@auth_bp.route('/logout')
def logout():

    logout_user()
    return redirect(url_for('index.index'))


@auth_bp.route('/register', methods=['POST'])
def register():
    """ Display registration form and create new User."""

    user_manager = current_app.user_manager
    db_adapter = user_manager.db_adapter
    # info = Info(username=request.form.get('username'), email=request.form.get('email'),
    #             password=request.form.get('password'))
    # info.save()

    # next = request.args.get('next', _endpoint_url(user_manager.after_login_endpoint))
    reg_next = request.args.get('reg_next', _endpoint_url(user_manager.after_register_endpoint))
    # invite token used to determine validity of registeree
    invite_token = request.values.get("token")

    # require invite without a token should disallow the user from registering
    # if user_manager.require_invitation and not invite_token:
    #     flash("Registration is invite only", "error")
    #     return redirect(url_for('user.login'))

    user_invite = None
    # if invite_token and db_adapter.UserInvitationClass:
    #     user_invite = db_adapter.find_first_object(db_adapter.UserInvitationClass, token=invite_token)

    if request.method == 'POST':
        # Create a User object using Form fields that have a corresponding User field
        User = db_adapter.UserClass
        user_class_fields = User.__dict__
        user_fields = {}

        # Create a UserEmail object using Form fields that have a corresponding UserEmail field
        if db_adapter.UserEmailClass:
            UserEmail = db_adapter.UserEmailClass
            user_email_class_fields = UserEmail.__dict__
            user_email_fields = {}

        # Create a UserAuth object using Form fields that have a corresponding UserAuth field
        if db_adapter.UserAuthClass:
            UserAuth = db_adapter.UserAuthClass
            user_auth_class_fields = UserAuth.__dict__
            user_auth_fields = {}

        # Enable user account
        if db_adapter.UserProfileClass:
            if hasattr(db_adapter.UserProfileClass, 'active'):
                user_auth_fields['active'] = True
            elif hasattr(db_adapter.UserProfileClass, 'is_enabled'):
                user_auth_fields['is_enabled'] = True
            else:
                user_auth_fields['is_active'] = True
        else:
            if hasattr(db_adapter.UserClass, 'active'):
                user_fields['active'] = True
            elif hasattr(db_adapter.UserClass, 'is_enabled'):
                user_fields['is_enabled'] = True
            else:
                user_fields['is_active'] = True
        data = request.form
        # For all form fields
        user_fields['registered_via'] = request.args
        for field_name, field_value in data.items():
            # Hash password field
            if field_name == 'password':
                if len(field_value) < 7:
                    return ajax_response(message='Пароль повинен містити не менше семи символів')
                hashed_password = user_manager.hash_password(field_value)
                if db_adapter.UserAuthClass:
                    user_auth_fields['password'] = hashed_password
                else:
                    user_fields['password'] = hashed_password
            # Store corresponding Form fields into the User object and/or UserProfile object
            else:
                if field_name in user_class_fields:
                    user_fields[field_name] = field_value
                if db_adapter.UserEmailClass:
                    if field_name in user_email_class_fields:
                        user_email_fields[field_name] = field_value
                if db_adapter.UserAuthClass:
                    if field_name in user_auth_class_fields:
                        user_auth_fields[field_name] = field_value

        # Add User record using named arguments 'user_fields'
        user = db_adapter.add_object(User, **user_fields)
        if db_adapter.UserProfileClass:
            user_profile = user

        # Add UserEmail record using named arguments 'user_email_fields'
        if db_adapter.UserEmailClass:
            user_email = db_adapter.add_object(UserEmail, user=user, is_primary=True, **user_email_fields)
        else:
            user_email = None

        # Add UserAuth record using named arguments 'user_auth_fields'
        if db_adapter.UserAuthClass:
            user_auth = db_adapter.add_object(UserAuth, **user_auth_fields)
            if db_adapter.UserProfileClass:
                user = user_auth
            else:
                user.user_auth = user_auth

        require_email_confirmation = True
        if user_invite:
            if user_invite.email == data.get('email'):
                require_email_confirmation = False
                db_adapter.update_object(user, confirmed_at=datetime.datetime.utcnow())

        try:
            db_adapter.commit()
        except IntegrityError as e:
            if e.message.find('email') != -1:
                return ajax_response(message='Така електронна адреса вже зареєстрована на нашому сайті')
            elif e.message.find('username') != -1:
                return ajax_response(message='Юзер з таким ніком вже зареєстрований на нашому сайті.'
                                             'Виберіть інший нік')

        # Send 'registered' email and delete new User object if send fails
        if user_manager.send_registered_email:
            try:
                # Send 'registered' email
                _send_registered_email(user, user_email, require_email_confirmation)

            except Exception as e:
                # delete new User object if send  fails
                db_adapter.delete_object(user)
                db_adapter.commit()
                raise

        # Send user_registered signal
        signals.user_registered.send(current_app._get_current_object(), user=user,
                                     user_invite=user_invite)

        # Redirect if USER_ENABLE_CONFIRM_EMAIL is set
        if user_manager.enable_confirm_email and require_email_confirmation:
            next = request.args.get('next', _endpoint_url(user_manager.after_register_endpoint))
            return ajax_response(message='На вашу електронну адресу був відправленний лист з підтвердженням реєстрації.'
                                         'Перейдіть на вашу поштову скриньку, щоб завершити реєстрацію на нашому '
                                         'сайті.<h5><a href="{mail_url}" target="_blank">Перейти</a></h5>"Якщо лист не прийшов '
                                         'перейдіть за <a href="{resend_email}">цим</a> посиланням і ми '
                                         'відправимо лист ще раз'.format(
                                          mail_url='http://'+data.get('email').split('@')[-1]+'/mail',
                                          resend_email=url_for('user.resend_confirm_email')),
                                 alert='На вашу електронну адресу був відправленний лист з підтвердженням реєстрації.'
                                       'Перейдіть на вашу поштову скриньку, щоб завершити реєстрацію на нашому сайті.')

        # Auto-login after register or redirect to login page
        next = request.args.get('next', _endpoint_url(user_manager.after_confirm_endpoint))
        if user_manager.auto_login_after_register:
            return _do_login_user(user, reg_next)                     # auto-login
        else:
            return ajax_response(message='На вашу електронну адресу був відправленний лист з підтвердженням реєстрації.'
                                         'Перейдіть на вашу поштову скриньку, щоб завершити реєстрацію на нашому '
                                         'сайті.<h5><a href="{mail_url}">Перейти</a></h5>"Якщо лист не прийшов '
                                         'перейдіть за <a href="{resend_email}" target="_blank">цим</a> посиланням і ми '
                                         'відправимо лист ще раз'.format(
                                          mail_url='http://'+data.get('email').split('@')[-1]+'/mail',
                                          resend_email=url_for('user.resend_confirm_email')),
                                 alert='На вашу електронну адресу був відправленний лист з підтвердженням реєстрації.'
                                       'Перейдіть на вашу поштову скриньку, щоб завершити реєстрацію на нашому сайті')

    # Process GET or invalid POST
    return redirect(request.referrer)


def _do_login_user(user, next, remember_me=False):

    # Check if user account has been disabled
    if not _call_or_get(user.is_active):
        return ajax_response(message='Ваша електронна адреса не була підтверджена.'
                                     'Перевірте вашу електронну скриньку на наявність листа.'
                                     'У цьому листі натисніть підтвердити електронну адресу. '
                                     'Якщо лист не прийшов перейдіть за '
                                     '<a href="%s">цим</a> посиланням.' % url_for('user.resend_confirm_email'))

    # Check if user has a confirmed email address
    user_manager = current_app.user_manager
    if user_manager.enable_email and user_manager.enable_confirm_email \
            and not current_app.user_manager.enable_login_without_confirm_email \
            and not user.has_confirmed_email():
        url = url_for('user.resend_confirm_email')
        return ajax_response(message='Ваша електронна адреса не була підтверджена.'
                                     'Перевірте вашу електронну скриньку на наявність листа.'
                                     'У цьому листі натисніть підтвердити електронну адресу. '
                                      'Якщо лист не прийшов перейдіть за '
                                      '<a href="%s">цим</a> посиланням.' % url_for('user.resend_confirm_email'))

    # Use Flask-Login to sign in user
    #print('login_user: remember_me=', remember_me)
    login_user(user, remember=remember_me)

    # Send user_logged_in signal
    signals.user_logged_in.send(current_app._get_current_object(), user=user)

    # # Prepare one-time system message
    # flash(_('You have signed in successfully.'), 'success')
    #
    # # Redirect to 'next' URL
    print(next)
    return


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')


@auth_bp.route('/facebook_login')
def facebook_login():
    next_url = request.args.get('next') or url_for('index.index')
    return facebook.authorize(callback=url_for('auth.facebook_authorized',
                                               next=next_url, _external=True))


@auth_bp.route('/facebook_login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    next_url = request.args.get('next') or url_for('index.index')
    if resp is None:
        return redirect(url_for('error.error', error='Помилка при логуванні, попробуйте ще раз'))
    session['oauth_token'] = (resp['access_token'], '')
    user_data = facebook.get('me?fields=id,email,name').data
    user = db_query(User, email=user_data.get('email')).first()
    if user is None:
        new_user = User(email=user_data['email'], registered_via='facebook',
                        username=user_data['email'], shown_name=user_data['name'],
                        confirmed_at=datetime.datetime.utcnow(), active=True, facebook_id=user_data['id'])
        g.db.add(new_user)
        login_user(new_user)
    else:
        if not user.facebook_id:
            user.facebook_id=user_data['id']
        login_user(user)
    g.db.commit()
    session['login_via'] = 'facebook'
    return redirect(next_url)


@auth_bp.route('/vkontakte_login')
def vkontakte_login():
    return redirect(vkontakte.get_service)


@auth_bp.route('/vkontakte_login/authorized/')
def vkontakte_authorized():

    next_url = request.args.get('next') or url_for('index.index')
    if request.args.get('code'):
        token = vkontakte.get_token(code=request.args.get('code'))
        session['access_token'] = token.get('access_token')
        if not token.get('email'):
            return redirect(url_for('error.error', error='Помилка при логуванні. '
                                                         'Можливо ви не підтвердили вашу електронну адресу в vkontakte '
                                                         'або заборонили доступ до вашої електронної адреси в '
                                                         'налаштуваннях. Спробуйте залогуватися через іншу систему'))
        else:
            user = db_query(User, email=token.get('email')).first()
            if user is None:
                user_name = json.load(urllib.urlopen(
                    "https://api.vk.com/method/users.get?v=5.8&access_token={access_token}".format(
                        access_token=token.get('access_token'))))['response'][0]
                print(user_name)
                user_name = user_name.get('first_name') + ' ' + user_name.get('last_name')
                new_user = User(email=token.get('email'), registered_via='vkontakte',
                                username=token.get('email'), shown_name=user_name,
                                confirmed_at=datetime.datetime.utcnow(), active=True)
                g.db.add(new_user)
                g.db.commit()
                login_user(new_user)
            else:
                login_user(user)
    else:
        return redirect(url_for('error.error', error='Помилка при логуванні. Спробуйте ще раз, '
                                                     'або спробуйте залогуватися через іншу систему'))
    session['login_via'] = 'vkontakte'
    return redirect(next_url)


@auth_bp.route('/google_login')
def google_login():
    print(os.getcwd())
    try:
        flow = client.flow_from_clientsecrets(os.getcwd() + '/app-root/runtime/repo/client_secret.json',
                                              scope=['https://www.googleapis.com/auth/userinfo.email',
                                                     'https://www.googleapis.com/auth/userinfo.profile'],
                                              redirect_uri='{host}/auth/google_login'.format(host=get_app_url()))
    except IOError as e:
        flow = client.flow_from_clientsecrets('client_secret.json',
                                              scope=['https://www.googleapis.com/auth/userinfo.email',
                                                     'https://www.googleapis.com/auth/userinfo.profile'],
                                              redirect_uri='{host}/auth/google_login'.format(host=get_app_url()))
    flow.params['access_type'] = 'online'
    if 'code' not in request.args:
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)
    else:
        auth_code = request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        user_data = json.load(
            urllib.urlopen('https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token={token}'.format(
                token=credentials.access_token)))
        session['credentials'] = credentials.to_json()
    if not user_data.get('email'):
        return redirect(url_for('error.error', error='Помилка при логуванні. '
                                                     'Можливо ви не підтвердили вашу електронну адресу в vkontakte '
                                                     'або заборонили доступ до вашої електронної адреси в '
                                                     'налаштуваннях. Спробуйте залогуватися через іншу систему'))
    user = db_query(User, email=user_data.get('email')).first()
    if user is None:
        new_user = User(email=user_data.get('email'), registered_via='google',
                        username=user_data.get('email'), shown_name=user_data.get('name'),
                        confirmed_at=datetime.datetime.utcnow(), active=True, google_id=user_data['id'])
        g.db.add(new_user)
        login_user(new_user)
        g.db.commit()
    else:
        if not user.google_id:
            user.google_id = user_data['id']
        login_user(user)
    g.db.commit()
    session['login_via'] = 'google'
    return redirect(url_for('index.index'))
