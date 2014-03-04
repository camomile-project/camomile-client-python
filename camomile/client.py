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

import logging
import requests
import json
from six.moves.urllib_parse import urljoin


class CMMLMixinAdmin():

    ROLE_ADMIN = 'admin'
    ROLE_USER = 'user'

    def create_user(
        self, username, password, affiliation, role=ROLE_USER
    ):
        route = 'signup'
        data = {
            'username': username, 'password': password,
            'affiliation': affiliation,
            'role': role
        }
        return self.post(route, data, returns_json=False)


class CamomileClient(object):

    def __init__(self, username, password, url):

        super(CamomileClient, self).__init__()

        # add trailing slash if missing
        self.url = url + ('/' if url[-1] != '/' else '')

        self.session = requests.Session()
        self.login(username, password)

    def get(self, route, returns_json=True):
        url = urljoin(self.url, route)
        r = self.session.get(url)
        if returns_json:
            return r.json()
        else:
            return r

    def delete(self, route, returns_json=True):
        url = urljoin(self.url, route)
        r = self.session.delete(url)
        if returns_json:
            return r.json()
        else:
            return r

    def post(self, route, data, returns_json=True):
        url = urljoin(self.url, route)
        r = self.session.post(
            url,
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )
        if returns_json:
            return r.json()
        else:
            return r

    def put(self, route, data, returns_json=True):
        url = urljoin(self.url, route)
        r = self.session.put(
            url,
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )
        if returns_json:
            return r.json()
        else:
            return r

    def login(self, username, password):
        return self.post(
            'login',
            {'username': username, 'password': password},
            returns_json=False
        )

    def logout(self):
        return self.get('logout')


class CMMLMixinData():

    def corpus(self):
        route = 'corpus'
        results = self.get(route)
        return [CMMLCorpus(r, client=self, corpus=r['_id']) for r in results]

    def corpusByName(self, name):
        for c in self.corpus():
            if c.document['name'] == name:
                return c
        return None

    def new_corpus(self, name):
        route = 'corpus'
        data = {'name': name}
        r = self.post(route, data)
        return CMMLCorpus(r, client=self, corpus=r['_id'])


class CMMLCorpus(object):

    def __init__(self, document, client=None, corpus=None):
        super(CMMLCorpus, self).__init__()
        self.document = document
        self.client = client
        self.corpus = corpus

    def media(self):
        route = 'corpus/%s/media' % self.corpus
        results = self.client.get(route)
        return [
            CMMLMedia(r, client=self.client, corpus=self.corpus, media=r['_id'])
            for r in results
        ]

    def mediaByName(self, name):
        for m in self.media():
            if m.document['name'] == name:
                return m
        return None

    def new_media(self, name, url):
        route = 'corpus/%s/media' % self.corpus
        data = {'name': name, 'url': url}
        r = self.client.post(route, data)
        logging.info(r)
        return CMMLMedia(r,
            client=self.client, corpus=self.corpus, media=r['_id'])

    def set_acl(self, username, userright):
        route = 'corpus/%s/acl' % self.corpus
        data = {'username': username, 'userright': userright}
        r = self.client.put(route, data)
        return r

class CMMLMedia(object):

    def __init__(self, document, client=None, corpus=None, media=None):
        super(CMMLMedia, self).__init__()
        self.document = document
        self.client = client
        self.corpus = corpus
        self.media = media

    def layer(self):
        route = 'corpus/%s/media/%s/layer' % (self.corpus, self.media)
        results = self.client.get(route)
        return [
            CMMLLayer(r,
                client=self.client,
                corpus=self.corpus, media=self.media, layer=r['_id']
            ) for r in results
        ]

    def layerByName(self, name):
        for l in self.layer():
            if l.document['layer_type'] == name:
                return l
        return None

    def new_layer_with(
        self, layer_type, fragment_type, data_type, source, annotations
    ):
        route = 'corpus/%s/media/%s/layerAll' % (self.corpus, self.media)
        data = {
            'layer_type': layer_type,
            'fragment_type': fragment_type,
            'data_type': data_type,
            'source': source,
            'annotation': annotations
        }
        r = self.client.post(route, data)
        return CMMLLayer(
            r,
            client=self.client,
            corpus=self.corpus, media=self.media, layer=r['id_layer']
        )

    def new_layer(
        self, layer_type, fragment_type, data_type, source
    ):

        route = 'corpus/%s/media/%s/layer' % (self.corpus, self.media)

        data = {
            'layer_type': layer_type,
            'fragment_type': fragment_type,
            'data_type': data_type,
            'source': source,
        }

        r = self.client.post(route, data)
        return CMMLLayer(
            r,
            client=self.client,
            corpus=self.corpus, media=self.media, layer=r['_id']
        )

    def set_acl(self, username, userright):
        route = 'corpus/%s/media/%s/acl' % (self.corpus, self.media)
        data = {'username': username, 'userright': userright}
        r = self.client.put(route, data)
        return r


class CMMLLayer(object):

    def __init__(self, document, client=None, corpus=None, media=None, layer=None):
        super(CMMLLayer, self).__init__()
        self.document = document
        self.client = client
        self.corpus = corpus
        self.media = media
        self.layer = layer

    def delete(self):
        route = 'corpus/%s/media/%s/layer/%s' % (
            self.corpus, self.media, self.layer)
        return self.client.delete(route, returns_json=False)

    def annotation(self):
        route = 'corpus/%s/media/%s/layer/%s/annotation' % (
            self.corpus, self.media, self.layer)
        results = self.client.get(route)
        return [
            CMMLAnnotation(
                r,
                client=self.client,
                corpus=self.corpus, media=self.media,
                layer=self.layer, annotation=r['_id']
            ) for r in results
        ]

    def new_annotation(self, fragment, data):
        route = 'corpus/%s/media/%s/layer/%s/annotation' % (
            self.corpus, self.media, self.layer)
        data = {
            'fragment': fragment,
            'data': data,
            'history': ''   # will be removed when API is fixed
        }
        r = self.client.post(route, data)
        return CMMLLayer(
            r,
            client=self.client,
            corpus=self.corpus, media=self.media, layer=r['_id']
        )

    def set_acl(self, username, userright):
        route = 'corpus/%s/media/%s/layer/%s/acl' % (
            self.corpus, self.media, self.layer)
        data = {'username': username, 'userright': userright}
        r = self.client.put(route, data)
        return r


class CMMLAnnotation(object):

    def __init__(
        self, document, client=None,
        corpus=None, media=None, layer=None, annotation=None
    ):
        super(CMMLAnnotation, self).__init__()
        self.document = document
        self.client = client
        self.corpus = corpus
        self.media = media
        self.layer = layer
        self.annotation = annotation


class FullFeaturedCamomileClient(CamomileClient, CMMLMixinAdmin, CMMLMixinData):
    pass
