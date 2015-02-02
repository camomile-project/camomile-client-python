#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2014 Hervé BREDIN (http://herve.niderb.fr/)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import requests
import simplejson as json
from six.moves.urllib_parse import urljoin
import time


class CamomileClient(object):

    def __init__(self, username, password, url, delay=0):
        super(CamomileClient, self).__init__()

        # add trailing slash if missing
        self.url = url + ('/' if url[-1] != '/' else '')
        self.session = requests.Session()
        self.delay = delay
        self.previous_call = 0.0
        self.login(username, password)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.logout()

    # common function #

    def _pause(self):
        if self.delay > 0:
            current_time = time.time()
            elapsed = current_time - self.previous_call
            if elapsed < self.delay:
                time.sleep(self.delay - elapsed)
            self.previous_call = current_time

    def _check_error(self, resp):
        if 400 <= resp.status_code < 600:
            try:
                msg = '%s Error: %s - %s' % (
                    resp.status_code, resp.reason, resp.json()['message'])
            except:
                msg = '%s Error: %s' % (resp.status_code, resp.reason)
            raise requests.exceptions.HTTPError(msg, response=resp)

    def _get(self, route):
        self._pause()
        url = urljoin(self.url, route)
        r = self.session.get(url)
        self._check_error(r)
        return r.json()

    def _delete(self, route):
        self._pause()
        url = urljoin(self.url, route)
        r = self.session.delete(url)
        self._check_error(r)
        return r.json()

    def _post(self, route, data=None):
        self._pause()
        url = urljoin(self.url, route)
        r = self.session.post(url,
                              data=json.dumps(data),
                              headers={'Content-Type': 'application/json'})
        self._check_error(r)
        return r.json()

    def _put(self, route, data=None):
        self._pause()
        url = urljoin(self.url, route)
        r = self.session.put(url,
                             data=json.dumps(data),
                             headers={'Content-Type': 'application/json'})
        self._check_error(r)
        return r.json()

    # authenticate #
    def login(self, username, password):
        return self._post('login', {'username': username, 'password': password})

    def logout(self):
        return self._post('logout', {})

    def me(self):
        return self._get('me')
    # alias
    get_me = me

    # user #

    def create_user(self, username, password, description='', role='user'):
        params = {'username': username, 'password': password,
                  'description': description, 'role': role}
        return self._post('user', params)

    def get_user(self, id_user=None):
        if id_user is None:
            return self._get('user')
        else:
            return self._get('user/' + id_user)

    def get_user_id(self, username):
        return {i['username']: i['_id'] for i in self._get_user()}[username]

    def update_user(self, id_user, password=None, description=None, role=None):
        params = {}
        if password is not None:
            params['password'] = password
        if description is not None:
            params['description'] = description
        if role is not None:
            params['role'] = role
        return self._put('user/' + id_user, params)

    def delete_user(self, id_user):
        return self._delete('user/' + id_user)

    def get_user_group(self, id_user):
        return self._get('user/' + id_user + '/group')

    # group #

    def create_group(self, name, description=''):
        params = {'name': name, 'description': description}
        return self._post('group', params)

    def get_group(self, id_group=None):
        if id_group is None:
            return self._get('group')
        else:
            return self._get('group/' + id_group)

    def get_group_id(self, name):
        return {i['name']: i['_id'] for i in self._get_group()}[name]

    def update_group(self, id_group, description):
        params = {'description': description}
        return self._put('group/' + id_group, params)

    def delete_group(self, id_group):
        return self._delete('group/' + id_group)

    def update_group_user(self, id_group, id_user):
        return self._put('group/' + id_group + '/user/' + id_user, {})

    # alias
    add_group_user = update_group_user

    def delete_group_user(self, id_group, id_user):
        return self._delete('group/' + id_group + '/user/' + id_user)
    # alias
    remove_group_user = delete_group_user

    # corpus #

    def create_corpus(self, name, description=''):
        params = {'name': name, 'description': description}
        return self._post('corpus', params)

    def get_corpus(self, id_corpus=None, history=False):
        history = '?history=ON' if history else ''
        if id_corpus is None:
            return self._get('corpus' + history)
        else:
            return self._get('corpus/' + id_corpus + history)

    def get_corpus_id(self, name):
        return {i['name']: i['_id'] for i in self._get_corpus()}[name]

    def update_corpus(self, id_corpus, name=None, description=None):
        params = {}
        if name is not None:
            params['name'] = name
        if description is not None:
            params['description'] = description
        return self._put('corpus/' + id_corpus, params)

    def delete_corpus(self, id_corpus):
        return self._delete('corpus/' + id_corpus)

    def create_corpus_media(self, id_corpus, media_list=None, name=None,
                            url='', description=''):
        if media_list is not None:
            params = media_list
        else:
            params = {'name': name, 'url': url, 'description': description}
        return self._post('corpus/' + id_corpus + '/media', params)

    def create_corpus_layer(self, id_corpus, name, description, fragment_type,
                            data_type, annotations=[]):
        params = {'name': name, 'description': description,
                  'fragment_type': fragment_type, 'data_type': data_type,
                  'annotations': annotations}
        return self._post('corpus/' + id_corpus + '/layer', params)

    def get_corpus_media(self, id_corpus):
        return self._get('corpus/' + id_corpus + '/media')

    def get_corpus_media_id(self, id_corpus, name):
        return {i['name']: i['_id']
                for i in self._get_corpus_media(id_corpus)}[name]

    def get_corpus_layer(self, id_corpus):
        return self._get('corpus/' + id_corpus + '/layer')

    def get_corpus_layer_id(self, id_corpus, name):
        return {i['name']: i['_id']
                for i in self._get_corpus_layer(id_corpus)}[name]

    def get_corpus_ACL(self, id_corpus):
        return self._get('corpus/' + id_corpus + '/ACL')

    def update_corpus_user(self, id_corpus, id_user, right):
        params = {'right': right}
        return self._put('corpus/' + id_corpus + '/user/' + id_user, params)

    def update_corpus_group(self, id_corpus, id_group, right):
        params = {'right': right}
        return self._put('corpus/' + id_corpus + '/group/' + id_group, params)

    def delete_corpus_user(self, id_corpus, id_user):
        return self._delete('corpus/' + id_corpus + '/user/' + id_user)
    # alias
    remove_corpus_user = delete_corpus_user

    def delete_corpus_group(self, id_corpus, id_group):
        return self._delete('corpus/' + id_corpus + '/group/' + id_group)
    # alias
    remove_corpus_group = delete_corpus_group

    # media #

    def get_media(self, id_media=None):
        if id_media is None:
            return self._get('media')
        else:
            return self._get('media/' + id_media)

    def update_media(self, id_media, name=None, url=None, description=None):
        params = {}
        if name is not None:
            params['name'] = name
        if url is not None:
            params['url'] = url
        if description is not None:
            params['description'] = description
        return self._put('media/' + id_media, params)

    def delete_media(self, id_media):
        return self._delete('media/' + id_media)

    def get_media_video(self, id_media):
        return self._get('media/' + id_media + '/video')

    def get_media_webm(self, id_media):
        return self._get('media/' + id_media + '/webm')

    def get_media_mp4(self, id_media):
        return self._get('media/' + id_media + '/mp4')

    def get_media_ogv(self, id_media):
        return self._get('media/' + id_media + '/ogv')

    # layer #
    def get_layer(self, id_layer=None):
        if id_layer is None:
            return self._get('layer')
        else:
            return self._get('layer/' + id_layer)

    def update_layer(self, id_layer, name=None, description=None,
                     fragment_type=None, data_type=None):
        params = {}
        if name is not None:
            params['name'] = name
        if description is not None:
            params['description'] = description
        if fragment_type is not None:
            params['fragment_type'] = fragment_type
        if data_type is not None:
            params['data_type'] = data_type
        return self._put('layer/' + id_layer, params)

    def delete_layer(self, id_layer):
        return self._delete('layer/' + id_layer)

    def create_layer_annotation(self, id_layer, annotation_list=None,
                                id_media=None, fragment=None, data=None):
        if annotation_list is not None:
            params = annotation_list
        else:
            params = {'id_media': id_media, 'fragment': fragment, 'data': data}
        return self._post('layer/' + id_layer + '/annotation', params)

    def get_layer_annotation(self, id_layer, media=None):
        if media is None:
            return self._get('layer/' + id_layer + '/annotation')
        else:
            return self._get('layer/' + id_layer + '/annotation?media=' + media)

    def get_layer_ACL(self, id_layer):
        return self._get('layer/' + id_layer + '/ACL')

    def update_layer_user(self, id_layer, id_user, right):
        params = {'right': right}
        return self._put('layer/' + id_layer + '/user/' + id_user, params)

    def update_layer_group(self, id_layer, id_group, right):
        params = {'right': right}
        return self._put('layer/' + id_layer + '/group/' + id_group, params)

    def delete_layer_user(self, id_layer, id_user):
        return self._delete('layer/' + id_layer + '/user/' + id_user)

    def delete_layer_group(self, id_layer, id_group):
        return self._delete('layer/' + id_layer + '/group/' + id_group)

    # annotation #

    def get_annotation(self, id_annotation=None):
        if id_annotation is None:
            return self._get('annotation')
        else:
            return self._get('annotation/' + id_annotation)

    def update_annotation(self, id_annotation, fragment=None, data=None):
        params = {}
        if fragment is not None:
            params['fragment'] = fragment
        if data is not None:
            params['data'] = data
        return self._put('annotation/' + id_annotation, params)

    def delete_annotation(self, id_annotation):
        return self._delete('annotation/' + id_annotation)

    # queue #

    def create_queue(self, name, description=''):
        params = {'name': name, 'description': description}
        return self._post('queue', params)

    def get_queue(self, id_queue=None):
        if id_queue is None:
            return self._get('queue')
        else:
            return self._get('queue/' + id_queue)

    def update_queue(self, id_queue, name=None, description=None, list=None):
        params = {}
        if name is not None:
            params['name'] = name
        if description is not None:
            params['description'] = description
        if list is not None:
            params['list'] = list
        return self._put('queue/' + id_queue, params)

    def update_queue_next(self, id_queue, list):
        params = {'list': list}
        return self._put('queue/' + id_queue + '/next', params)

    def get_queue_next(self, id_queue):
        return self._get('queue/' + id_queue + '/next')

    def delete_queue(self, id_queue):
        return self._delete('queue/' + id_queue)

    # tools #

    def get_date(self):
        return self._get('date')
