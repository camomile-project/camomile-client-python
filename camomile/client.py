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
            if elapsed < self.delay:
                time.sleep(self.delay - elapsed)
            self.previous_call = current_time

    def check_error(self, resp):
        if 400 <= resp.status_code < 600:
            try:    
                msg = '%s Error: %s - %s' % (
                    resp.status_code, resp.reason, resp.json()['message'])
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

    def post(self, route, data=None):
        self.pause()
        url = urljoin(self.url, route)
        r = self.session.post(url,
                              data=json.dumps(data),
                              headers={'Content-Type': 'application/json'})
        self.check_error(r)
        return r.json()

    def put(self, route, data=None):
        self.pause()
        url = urljoin(self.url, route)
        r = self.session.put(url,
                             data=json.dumps(data),
                             headers={'Content-Type': 'application/json'})
        self.check_error(r)
        return r.json()

    ### authenticate ###
    def login(self, username, password):
        return self.post('login', {'username': username, 'password': password})

    def logout(self):
        return self.post('logout', {})

    def me(self):
        return self.get('me')

    ### user ###
    def create_user(self, username, password, description=None, role='user'):
        data = {}
        data['username'] = username
        data['password'] = password
        data['role'] = role
        if description:
            data['description'] = description
        return self.post('user', data)

    def get_all_user(self):
        return self.get('user')

    def get_user(self, id_user):
        return self.get('user/' + id_user)

    def update_user(self, id_user, username=None, password=None, description=None, role=None):
        data = {}        
        if username:
            data['username'] = username
        if password:
            data['password'] = password
        if role:
            data['role'] = role
        if description:
            data['description'] = description
        return self.put('user/' + id_user, data)

    def delete_user(self, id_user):
        return self.delete('user/' + id_user)

    def get_all_group_of_a_user(self, id_user):
        return self.get('user/' + id_user + '/group')

    ### group ###
    def create_group(self, name, description=None):
        data = {}        
        data['name'] = name
        if description:
            data['description'] = description        
        return self.post('group', data)

    def get_all_group(self):
        return self.get('group')

    def get_group(self, id_group):
        return self.get('group/' + id_group)

    def update_group(self, id_group, name=None, description=None):
        data = {}        
        if name:
            data['name'] = name
        if description:
            data['description'] = description         
        return self.put('group/' + id_group, data)

    def delete_group(self, id_group):
        return self.delete('group/' + id_group)

    def add_user_to_a_group(self, id_group, id_user):
        return self.put('group/' + id_group + '/user/' + id_user, {})

    def remove_user_to_a_group(self, id_group, id_user):
        return self.delete('group/' + id_group + '/user/' + id_user)

    ### corpus ###
    def create_corpus(self, name, description=None):
        data = {}        
        data['name'] = name
        if description:
            data['description'] = description 
        return self.post('corpus', data)

    def get_all_corpus(self, history=False, name=None):
        param = '?'
        if history:
            param+='history=ON&'
        if name:
            param+='name='+name+'&'            
        return self.get('corpus'+param[:-1])

    def get_corpus(self, id_corpus, history=False):
        param = '?'
        if history:
            param+='history=ON&'
        return self.get('corpus/' + id_corpus+ param[:-1])    
        
    def update_corpus(self, id_corpus, name=None, description=None):
        data = {}        
        if name:
            data['name'] = name
        if description:
            data['description'] = description 
        return self.put('corpus/' + id_corpus, data)

    def delete_corpus(self, id_corpus):
        return self.delete('corpus/' + id_corpus)

    def add_media(self, id_corpus, name, url=None, description=None):
        data = {}        
        data['name'] = name
        if url:
            data['url'] = url         
        if description:
            data['description'] = description 
        return self.post('corpus/' + id_corpus + '/media', data)

    def add_layer(self, id_corpus, name, fragment_type, data_type, description=None, annotations=None):
        data = {}        
        data['name'] = name
        data['fragment_type'] = fragment_type
        data['data_type'] = data_type
        if description:
            data['description'] = description 
        if annotations:
            data['annotations'] = annotations
        print data        
        return self.post('corpus/' + id_corpus + '/layer', data)

    def get_all_media_of_a_corpus(self, id_corpus, history=False, name=None):
        param = '?'
        if history:
            param+='history=ON&'
        if name:
            param+='name='+name+'&'    
        return self.get('corpus/' + id_corpus + '/media'+param[:-1])

    def get_all_layer_of_a_corpus(self, id_corpus, history=False, name=None, fragment_type=None, data_type=None):
        param = '?'
        if history:
            param+='history=ON&'
        if name:
            param+='name='+name+'&'             
        if fragment_type:
            param+='fragment_type='+fragment_type+'&' 
        if data_type:
            param+='data_type='+data_type+'&'
        return self.get('corpus/' + id_corpus + '/layer'+param[:-1])

    def get_ACL_of_a_corpus(self, id_corpus):
        return self.get('corpus/' + id_corpus + '/ACL')

    def update_user_ACL_of_a_corpus(self, id_corpus, id_user, right):
        return self.put('corpus/' + id_corpus + '/user/' + id_user, {"right":right})

    def update_group_ACL_of_a_corpus(self, id_corpus, id_group, right):
        return self.put('corpus/' + id_corpus + '/group/' + id_group, {"right":right})

    def remove_user_from_ACL_of_a_corpus(self, id_corpus, id_user):
        return self.delete('corpus/' + id_corpus + '/user/' + id_user)

    def remove_group_from_ACL_of_a_corpus(self, id_corpus, id_group):
        return self.delete('corpus/' + id_corpus + '/group/' + id_group)

    ### media ###
    def get_all_media(self, history=False, name=None):
        param = '?'
        if history:
            param+='history=ON&'
        if name:
            param+='name='+name+'&' 
        return self.get('media'+param[:-1])

    def get_media(self, id_media, history=False):
        param = '?'
        if history:
            param+='history=ON&'
        return self.get('media/' + id_media+param[:-1])

    def update_media(self, id_media, name=None, url=None, description=None):
        data = {}        
        if name:
            data['name'] = name
        if url:
            data['url'] = url         
        if description:
            data['description'] = description 
        return self.put('media/' + id_media, data)

    def delete_media(self, id_media):
        return self.delete('media/' + id_media)

    def get_media_video_stream(self, id_media):
        return self.get('media/' + id_media + '/video')

    def get_media_webm_stream(self, id_media):
        return self.get('media/' + id_media + '/webm')

    def get_media_mp4_stream(self, id_media):
        return self.get('media/' + id_media + '/mp4')

    def get_media_ogv_stream(self, id_media):
        return self.get('media/' + id_media + '/ogv')

    ### layer ###
    def get_all_layer(self, history=False, name=None, fragment_type=None, data_type=None):
        param = '?'
        if history:
            param+='history=ON&'
        if name:
            param+='name='+name+'&'             
        if fragment_type:
            param+='fragment_type='+fragment_type+'&' 
        if data_type:
            param+='data_type='+data_type+'&'
        return self.get('layer'+param[:-1])

    def get_layer(self, id_layer, history=False):
        param = '?'
        if history:
            param+='history=ON&' 
        return self.get('layer/' + param[:-1])

    def update_layer(self, id_layer, name=None, fragment_type=None, data_type=None, description=None):
        data = {}        
        if name:
            data['name'] = name
        if fragment_type:
            data['fragment_type'] = fragment_type         
        if data_type:
            data['data_type'] = data_type      
        if description:
            data['description'] = description
        return self.put('layer/' + id_layer, data)

    def delete_layer(self, id_layer):
        return self.delete('layer/' + id_layer)

    def add_annotation(self, id_layer, fragment, data, id_media=None):
        data_send = {}        
        data_send['fragment'] = fragment
        data_send['data'] = data         
        if id_media:
            data_send['id_media'] = id_media
        return self.post('layer/' + id_layer + '/annotation', data_send)

    def get_all_annotation_of_a_layer(self, id_layer, history=False, id_media=None, fragment=None, data=None):
        param = '?'
        if history:
            param+='history=ON&'
        if id_media:
            param+='id_media=' + id_media + '&'
        if fragment:
            param+='fragment=' + fragment + '&'
        if data:
            param+='data=' + data + '&'            
        return self.get('layer/' + id_layer + '/annotation'+param[:-1])

    def get_ACL_of_a_layer(self, id_layer):
        return self.get('layer/' + id_layer + '/ACL')

    def update_user_ACL_of_a_layer(self, id_layer, id_user, right):
        return self.put('layer/' + id_layer + '/user/' + id_user, {"right":right})

    def update_group_ACL_of_a_layer(self, id_layer, id_group, right):
        return self.put('layer/' + id_layer + '/group/' + id_group, {"right":right})

    def remove_user_from_ACL_of_a_layer(self, id_layer, id_user):
        return self.delete('layer/' + id_layer + '/user/' + id_user)

    def remove_group_from_ACL_of_a_layer(self, id_layer, id_group):
        return self.delete('layer/' + id_layer + '/group/' + id_group)

    ### annotation ###
    def get_all_annotation(self, history=False, id_layer=None, id_media=None, fragment=None, data=None):
        param = '?'
        if history:
            param+='history=ON&'  
        if id_layer:
            param+='id_layer=' + id_layer + '&'
        if id_media:
            param+='id_media=' + id_media + '&'
        if fragment:
            param+='fragment=' + fragment + '&'
        if data:
            param+='data=' + data + '&'                   
        return self.get('annotation'+param[:-1])

    def get_annotation(self, id_annotation, history=False):
        param = '?'
        if history:
            param+='history=ON&'        
        return self.get('annotation/' + id_annotation+param[:-1])

    def update_annotation(self, id_annotation, fragment=None, data=None, id_media=None):
        data_send = {}        
        if fragment:
            data_send['fragment'] = fragment
        if data:
            data_send['data'] = data         
        if id_media:
            data_send['id_media'] = id_media
        return self.put('annotation/' + id_annotation, data_send)

    def delete_annotation(self, id_annotation):
        return self.delete('annotation/' + id_annotation)

    ### queue ###
    def create_queue(self, data=None):
        return self.post('queue', data)

    def get_all_queue(self):
        return self.get('queue')

    def get_queue(self, id_queue):
        return self.get('queue/' + id_queue)

    def update_queue(self, id_queue, data=None):
        return self.put('queue/' + id_queue, data)

    def push_into_a_queue(self, id_queue, data=None):
        return self.put('queue/' + id_queue + '/next', data)

    def pop_a_queue(self, id_queue):
        return self.get('queue/' + id_queue + '/next')

    def delete_queue(self, id_queue):
        return self.delete('queue/' + id_queue)

    def get_date(self):
        return self.get('date')
