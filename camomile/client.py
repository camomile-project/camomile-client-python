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

    ### common function ###
    def pause(self):
        if self.delay > 0:
            current_time = time.time()
            elapsed = current_time - self.previous_call
            if elapsed < self.delay :
                time.sleep(self.delay - elapsed)
            self.previous_call = current_time

    def check_error(self, resp):
        if 400 <= resp.status_code < 600 :
            try:
                msg = '%s Error: %s - %s' % (resp.status_code, resp.reason, resp.json()['message'])
            except:
                msg = '%s Error: %s' % (resp.status_code, resp.reason)
            raise requests.exceptions.HTTPError(msg, response=resp)
                
    def get(self, route):
        self.pause()
        url = urljoin(self.url, route)
        r = self.session.get(url)
        self.check_error(r)
        return r.json()

    def delete(self, route):
        self.pause()
        url = urljoin(self.url, route)
        r = self.session.delete(url)
        self.check_error(r)
        return r.json()

    def post(self, route, data):
        self.pause()
        url = urljoin(self.url, route)
        r = self.session.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        self.check_error(r)
        return r.json()

    def put(self, route, data):
        self.pause()
        url = urljoin(self.url, route)
        r = self.session.put(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        self.check_error(r)
        return r.json()

    ### authenticate ###
    def login(self, username, password):
        return self.post('login', {'username': username, 'password': password} )

    def logout(self):
        return self.post('logout', {})

    def me(self):
        return self.get('me')        

    ### user ###
    def create_user(self, data):
        return self.post('user', data)

    def get_all_user(self):
        return self.get('user')

    def get_user(self, id_user):
        return self.get('user/'+id_user)

    def update_user(self, id_user, data):
        return self.put('user/'+id_user, data)

    def delete_user(self, id_user):
        return self.delete('user/'+id_user)

    def get_all_group_of_a_user(self, id_user):
        return self.get('user/'+id_user+'/group')    

    ### group ###
    def create_group(self, data):
        return self.post('group', data)

    def get_all_group(self):
        return self.get('group')

    def get_group(self, id_group):
        return self.get('group/'+id_group)

    def update_group(self, id_group, data):
        return self.put('group/'+id_group, data)

    def delete_group(self, id_group):
        return self.delete('group/'+id_group)

    def add_user_to_a_group(self, id_group, id_user):
        return self.put('group/'+id_group+'/user/'+id_user, {})

    def remove_user_to_a_group(self, id_group, id_user):
        return self.delete('group/'+id_group+'/user/'+id_user)

    ### corpus ###
    def create_corpus(self, data):
        return self.post('corpus', data)

    def get_all_corpus(self):
        return self.get('corpus')

    def get_corpus(self, id_corpus):
        return self.get('corpus/'+id_corpus)

    def update_corpus(self, id_corpus, data):
        return self.put('corpus/'+id_corpus, data)

    def delete_corpus(self, id_corpus):
        return self.delete('corpus/'+id_corpus)

    def add_media(self, id_corpus, data):
        return self.post('corpus/'+id_corpus+'/media', data)

    def add_layer(self, id_corpus, data):
        return self.post('corpus/'+id_corpus+'/layer', data)

    def get_all_media_of_a_corpus(self, id_corpus):
        return self.get('corpus/'+id_corpus+'/media')

    def get_all_layer_of_a_corpus(self, id_corpus):
        return self.get('corpus/'+id_corpus+'/layer')

    def get_ACL_of_a_corpus(self, id_corpus):
        return self.get('corpus/'+id_corpus+'/ACL')

    def update_user_ACL_of_a_corpus(self, id_corpus, id_user, data):
        return self.put('corpus/'+id_corpus+'/user/'+id_user, data)

    def update_group_ACL_of_a_corpus(self, id_corpus, id_group, data):
        return self.put('corpus/'+id_corpus+'/group/'+id_group, data)

    def remove_user_from_ACL_of_a_corpus(self, id_corpus, id_user):
        return self.delete('corpus/'+id_corpus+'/user/'+id_user)

    def remove_group_from_ACL_of_a_corpus(self, id_corpus, id_group):
        return self.delete('corpus/'+id_corpus+'/group/'+id_group)

    ### media ###
    def get_all_media(self):
        return self.get('media')

    def get_media(self, id_media):
        return self.get('media/'+id_media)

    def update_media(self, id_media, data):
        return self.put('media/'+id_media, data)

    def delete_media(self, id_media):
        return self.delete('media/'+id_media)

    def get_media_video_stream(self, id_media):
        return self.get('media/'+id_media+'/video')

    def get_media_webm_stream(self, id_media):
        return self.get('media/'+id_media+'/webm')

    def get_media_mp4_stream(self, id_media):
        return self.get('media/'+id_media+'/mp4')

    def get_media_ogv_stream(self, id_media):
        return self.get('media/'+id_media+'/ogv')                

    ### layer ###
    def get_all_layer(self):
        return self.get('layer')

    def get_layer(self, id_layer):
        return self.get('layer/'+id_layer)

    def update_layer(self, id_layer, data):
        return self.put('layer/'+id_layer, data)

    def delete_layer(self, id_layer):
        return self.delete('layer/'+id_layer)

    def add_annotation(self, id_layer, data):
        return self.post('layer/'+id_layer+'/annotation', data)

    def get_all_annotation_of_a_layer(self, id_layer, media=''):
        if media == '' :
            return self.get('layer/'+id_layer+'/annotation')
        else:
            return self.get('layer/'+id_layer+'/annotation?media='+media)

    def get_ACL_of_a_layer(self, id_layer):
        return self.get('layer/'+id_layer+'/ACL')

    def update_user_ACL_of_a_layer(self, id_layer, id_user, data):
        return self.put('layer/'+id_layer+'/user/'+id_user, data)

    def update_group_ACL_of_a_layer(self, id_layer, id_group, data):
        return self.put('layer/'+id_layer+'/group/'+id_group, data)

    def remove_user_from_ACL_of_a_layer(self, id_layer, id_user):
        return self.delete('layer/'+id_layer+'/user/'+id_user)

    def remove_group_from_ACL_of_a_layer(self, id_layer, id_group):
        return self.delete('layer/'+id_layer+'/group/'+id_group)

    ### annotation ###
    def get_all_annotation(self):
        return self.get('annotation')

    def get_annotation(self, id_annotation):
        return self.get('annotation/'+id_annotation)

    def update_annotation(self, id_annotation, data):
        return self.put('annotation/'+id_annotation, data)

    def delete_annotation(self, id_annotation):
        return self.delete('annotation/'+id_annotation)

    ### queue ###
    def create_queue(self, data):
        return self.post('queue', data)

    def get_all_queue(self):
        return self.get('queue')

    def get_queue(self, id_queue):
        return self.get('queue/'+id_queue)

    def update_queue(self, id_queue, data):
        return self.put('queue/'+id_queue, data)

    def push_into_a_queue(self, id_queue, data):
        return self.put('queue/'+id_queue+'/next', data)

    def pop_a_queue(self, id_queue):
        return self.get('queue/'+id_queue+'/next')

    def delete_queue(self, id_queue):
        return self.delete('queue/'+id_queue)

    def get_date(self):
        return self.get('date')