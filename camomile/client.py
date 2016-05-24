#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2014-2015 CNRS

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

# AUTHORS
# Hervé BREDIN (http://herve.niderb.fr/)
# Johann POIGNANT
# Claude BARRAS


import tortilla
import requests
import os
import threading
import json

from getpass import getpass
from sseclient import SSEClient


# Decorator catching HTTPErrors and replacing the generic error message
# with the Camomile error field found in the response data.
def catchCamomileError(func):
    def decoratedFunc(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except requests.exceptions.HTTPError as e:

            try:
                json = e.response.json()
                error = json.get('error', None)
            except Exception as e:
                error = None

            if error:
                if e.response.status_code < 500:
                    fmt = '%s Camomile Client Error: %s'
                else:
                    fmt = '%s Camomile Server Error: %s'
                e.message = fmt % (e.response.status_code, error)

            # it may happen that server does not respond at all.
            if hasattr(e, 'response'):
                response = e.response
            else:
                response = None

            raise requests.exceptions.HTTPError(e.message, response=response)

    # keep name and docstring of the initial function
    decoratedFunc.__name__ = func.__name__
    decoratedFunc.__doc__ = func.__doc__
    return decoratedFunc


class Camomile(object):
    """Client for Camomile REST API

    Parameters
    ----------
    url : str
        Base URL of Camomile API.
    username, password : str, optional
        If provided, an attempt is made to log in.
    delay : float, optional
        If provided, make sure at least `delay` seconds pass between
        each request to the Camomile API.  Defaults to no delay.

    Example
    -------
    >>> url = 'http://camomile.fr'
    >>> client = Camomile(url)
    >>> client.login(username='root', password='password')
    >>> corpora = client.getCorpora(returns_id=True)
    >>> corpus = corpora[0]
    >>> layers = client.getLayers(corpus=corpus)
    >>> media = client.getMedia(corpus=corpus)
    >>> client.logout()
    """

    ADMIN = 3
    WRITE = 2
    READ = 1

    def __init__(self, url, username=None, password=None, delay=0.,
                 debug=False):
        super(Camomile, self).__init__()

        # internally rely on tortilla generic API wrapper
        # see http://github.com/redodo/tortilla
        self._api = tortilla.wrap(url, format='json', delay=delay, debug=debug)
        self._url = url;
        self._listenerCallbacks = {}
        self._thread = None

        # log in if `username` is provided
        if username:
            self.login(username, password)

    def __enter__(self):
        """
        Example
        -------
        >>> url = 'http://camomile.fr'
        >>> with Camomile(url, username='root', password='password') as client:
        >>>     corpora = client.corpus()
        """
        return self

    def __exit__(self, type, value, traceback):
        self.logout()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # HELPER FUNCTIONS
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _user(self, id_user=None):
        user = self._api.user
        if id_user:
            user = user(id_user)
        return user

    def _group(self, id_group=None):
        group = self._api.group
        if id_group:
            group = group(id_group)
        return group

    def _corpus(self, id_corpus=None):
        corpus = self._api.corpus
        if id_corpus:
            corpus = corpus(id_corpus)
        return corpus

    def _medium(self, id_medium=None):
        medium = self._api.medium
        if id_medium:
            medium = medium(id_medium)
        return medium

    def _layer(self, id_layer=None):
        layer = self._api.layer
        if id_layer:
            layer = layer(id_layer)
        return layer

    def _annotation(self, id_annotation=None):
        annotation = self._api.annotation
        if id_annotation:
            annotation = annotation(id_annotation)
        return annotation

    def _queue(self, id_queue=None):
        queue = self._api.queue
        if id_queue:
            queue = queue(id_queue)
        return queue

    def _id(self, result):
        if isinstance(result, list):
            return [r._id for r in result]
        return result._id

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # AUTHENTICATION
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @catchCamomileError
    def login(self, username, password=None):
        """Login

        Parameters
        ----------
        username, password : str

        """

        if password is None:
            password = getpass()

        data = {'username': username,
                'password': password}
        
        return self._api.login.post(data=data)

    @catchCamomileError
    def logout(self):
        """Logout"""
        
        if self._thread:
           self._thread.isRun = False
           self._thread = None
            
        return self._api.logout.post()

    @catchCamomileError
    def me(self, returns_id=False):
        """Get information about logged in user"""
        result = self._api.me.get()
        return self._id(result) if returns_id else result

    @catchCamomileError
    def getMyGroups(self):
        """Get groups the logged in user belongs to"""
        return self._api.me.group.get()

    @catchCamomileError
    def update_password(self, new_password=None):
        """Update password"""

        if new_password is None:
            new_password = getpass('New password: ')

        return self._api.me.put(data={'password': new_password})

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # USERS
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @catchCamomileError
    def getUser(self, user):
        """Get user by ID

        Parameters
        ----------
        user : str
            User ID.

        Returns
        -------
        user : dict

        """
        return self._user(user).get()

    @catchCamomileError
    def getUsers(self, username=None, returns_id=False):
        """Get user(s)

        Parameters
        ----------
        username : str, optional
            Filter by username.
        returns_id : boolean, optional.
            Returns IDs rather than user dictionaries.

        Returns
        -------
        users : list
            List of users
        """
        params = {'username': username} if username else None
        result = self._user().get(params=params)
        return self._id(result) if returns_id else result

    @catchCamomileError
    def createUser(self,
                   username, password,
                   description=None, role='user',
                   returns_id=False):
        """Create new user

        Parameters
        ----------
        username, password : str, optional
        description : object, optional
            Must be JSON serializable.
        role : {'user', 'admin'}, optional
            Defaults to 'user'.
        returns_id : boolean, optional.
            Returns IDs rather than user dictionaries.

        Returns
        -------
        user : dict
            Newly created user.
        """

        data = {'username': username,
                'password': password,
                'description': description if description else {},
                'role': role}

        result = self._user().post(data=data)
        return self._id(result) if returns_id else result

    @catchCamomileError
    def updateUser(self, user, password=None, description=None, role=None):
        """Update existing user

        Parameters
        ----------
        user : str
            User ID.
        password : str, optional
            Set new password.
        description : object, optional
            Set new description. Must be JSON serializable.
        role : {'user', 'admin'}, optional
            Set new role.

        Returns
        -------
        user : dict
            Updated user.
        """
        data = {}

        if password is not None:
            data['password'] = password

        if description is not None:
            data['description'] = description

        if role is not None:
            data['role'] = role

        return self._user(user).put(data=data)

    @catchCamomileError
    def deleteUser(self, user):
        """Delete existing user

        Parameters
        ----------
        user : str
            User ID.
        """
        return self._user(user).delete()

    @catchCamomileError
    def getUserGroups(self, user):
        """Get groups of existing user

        Parameters
        ----------
        user : str

        Returns
        -------
        groups : list
            List of user's groups
        """
        return self._user(user).group.get()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # GROUPS
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @catchCamomileError
    def getGroup(self, group):
        """Get group by ID

        Parameters
        ----------
        group : str
            Group ID.

        Returns
        -------
        group : dict

        """
        return self._group(group).get()

    @catchCamomileError
    def getGroups(self, name=None, returns_id=False):
        """Get group(s)

        Parameters
        ----------
        name : str, optional
            Filter groups by name.
        returns_id : boolean, optional.
            Returns IDs rather than dictionaries.

        Returns
        -------
        groups : list
            List of groups
        """
        params = {'name': name} if name else None
        result = self._group().get(params=params)
        return self._id(result) if returns_id else result

    @catchCamomileError
    def createGroup(self, name, description=None, returns_id=False):
        """Create new group

        Parameters
        ----------
        name : str
            Group name.
        description : object, optional
            Group description. Must be JSON serializable.
        returns_id : boolean, optional.
            Returns IDs rather than dictionaries.

        Returns
        -------
        group : dict
            Newly created group.

        Example
        -------
        >>> description = {'country': 'France',
        ...                'town': 'Orsay'}
        >>> client.create_group('LIMSI', description=description)

        """
        data = {'name': name,
                'description': description if description else {}}

        result = self._group().post(data=data)
        return self._id(result) if returns_id else result

    @catchCamomileError
    def updateGroup(self, group, description=None):
        """Update existing group

        Parameters
        ----------
        group : str
            Group ID.
        description : object, optional

        Returns
        -------
        group : dict
            Updated group.
        """
        data = {'description': description}
        return self._group(group).put(data=data)

    @catchCamomileError
    def deleteGroup(self, group):
        """Delete existing group

        Parameters
        ----------
        group : str
            Group ID.
        """
        return self._group(group).delete()

    @catchCamomileError
    def addUserToGroup(self, user, group):
        return self._group(group).user(user).put()

    @catchCamomileError
    def removeUserFromGroup(self, user, group):
        return self._group(group).user(user).delete()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # CORPORA
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @catchCamomileError
    def getCorpus(self, corpus, history=False):
        """Get corpus by ID

        Parameters
        ----------
        corpus : str
            Corpus ID.
        history : boolean, optional
            Whether to return history.  Defaults to False.

        Returns
        -------
        corpus : dict

        """
        params = {'history': 'on'} if history else {}
        return self._corpus(corpus).get(params=params)

    @catchCamomileError
    def getCorpora(self, name=None, history=False, returns_id=False):
        """Get corpora

        Parameters
        ----------
        name : str, optional
            Get corpus by name.
        history : boolean, optional
            Whether to return history.  Defaults to False.
        returns_id : boolean, optional.
            Returns IDs rather than dictionaries.

        Returns
        -------
        corpora : list
            List of corpora.

        """
        params = {'history': 'on'} if history else {}
        if name:
            params['name'] = name

        result = self._corpus().get(params=params)
        return self._id(result) if returns_id else result

    @catchCamomileError
    def createCorpus(self, name, description=None, returns_id=False):
        """Create new corpus

        Parameters
        ----------
        name : str
            Corpus name.
        description : object, optional
            Corpus description. Must be JSON-serializable.
        returns_id : boolean, optional.
            Returns IDs rather than dictionaries.

        Returns
        -------
        corpus : dict
            Newly created corpus.
        """
        data = {'name': name,
                'description': description if description else {}}
        result = self._corpus().post(data=data)
        return self._id(result) if returns_id else result

    @catchCamomileError
    def updateCorpus(self, corpus, name=None, description=None):
        """Update corpus

        Parameters
        ----------
        corpus : str
            Corpus ID

        Returns
        -------
        corpus : dict
            Updated corpus.

        """
        data = {}

        if name:
            data['name'] = name

        if description:
            data['description'] = description

        return self._corpus(corpus).put(data=data)

    @catchCamomileError
    def deleteCorpus(self, corpus):
        """Delete corpus

        Parameters
        ----------
        corpus : str
            Corpus ID
        """
        return self._corpus(corpus).delete()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # MEDIA
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @catchCamomileError
    def getMedium(self, medium, history=False):
        """Get medium by ID

        Parameters
        ----------
        medium : str
            Medium ID.
        history : boolean, optional
            Whether to return history.  Defaults to False.

        Returns
        -------
        medium : dict

        """
        params = {'history': 'on'} if history else {}
        return self._medium(medium).get(params=params)

    @catchCamomileError
    def getMedia(self, corpus=None, name=None, history=False,
                 returns_id=False, returns_count=False):
        """Get media

        Parameters
        ----------
        corpus : str, optional
            Corpus ID. Get media for this corpus.
        name : str, optional
            Filter medium by name.
        history : boolean, optional
            Whether to return history.  Defaults to False.
        returns_id : boolean, optional.
            Returns IDs rather than dictionaries.
        returns_count : boolean, optional.
            Returns count of media instead of media.

        Returns
        -------
        media : list
            List of media
        """

        params = {'history': 'on'} if history else {}
        if name:
            params['name'] = name

        if corpus:
            # /corpus/:id_corpus/medium
            route = self._corpus(corpus).medium
            if returns_count:
                # /corpus/:id_corpus/medium/count
                route = route.count
            result = route.get(params=params)
        else:
            # /medium/count does not exist
            if returns_count:
                raise ValueError('returns_count needs a corpus.')
            result = self._medium().get(params=params)

        return (self._id(result)
                if (returns_id and not returns_count)
                else result)

    @catchCamomileError
    def createMedium(self, corpus, name, url=None, description=None,
                     returns_id=False):
        """Add new medium to corpus

        Parameters
        ----------
        corpus : str
            Corpus ID.
        name : str
            Medium name.
        url : str, optional
            Relative path to medium files.
        description : object, optional
            Medium description.  Must be JSON-serializable.
        returns_id : boolean, optional.
            Returns IDs rather than dictionaries.

        Returns
        -------
        medium : dict
            Newly created medium.
        """
        medium = {'name': name,
                  'url': url if url else '',
                  'description': description if description else {}}

        result = self._corpus(corpus).medium.post(data=medium)
        return self._id(result) if returns_id else result

    @catchCamomileError
    def createMedia(self, corpus, media, returns_id=False):
        """Add several media to corpus

        Parameters
        ----------
        corpus : str
            Corpus ID.
        media : list
            List of media.
        returns_id : boolean, optional.
            Returns IDs rather than dictionaries.

        Returns
        -------
        media : list
            List of new media.
        """
        result = self._corpus(corpus).medium.post(data=media)
        return self._id(result) if returns_id else result

    @catchCamomileError
    def updateMedium(self, medium, name=None, url=None, description=None):
        """Update existing medium

        Parameters
        ----------
        medium : str
            Medium ID
        name : str, optional
        url : str, optional
        description : object, optional
            Must be JSON-serializable.

        Returns
        -------
        medium : dict
            Updated medium.
        """
        data = {}

        if name is not None:
            data['name'] = name

        if url is not None:
            data['url'] = url

        if description is not None:
            data['description'] = description

        return self._medium(medium).put(data=data)

    @catchCamomileError
    def deleteMedium(self, medium):
        """Delete existing medium

        Parameters
        ----------
        medium : str
            Medium ID
        """
        return self._medium(medium).delete()

    @catchCamomileError
    def streamMedium(self, medium, format=None):
        """Stream medium

        Parameters
        ----------
        medium : str
            Medium ID
        format : {'webm', 'mp4', 'ogv', 'mp3', 'wav'}, optional
            Streaming format.
        """

        if format is None:
            format = 'video'

        return self._medium(medium).get(format)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # LAYERS
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @catchCamomileError
    def getLayer(self, layer, history=False):
        """Get layer by ID

        Parameters
        ----------
        layer : str
            Layer ID.
        history : boolean, optional
            Whether to return history.  Defaults to False.

        Returns
        -------
        layer : dict

        """
        params = {'history': 'on'} if history else {}
        return self._layer(layer).get(params=params)

    @catchCamomileError
    def getLayers(self, corpus=None, name=None,
                  fragment_type=None, data_type=None,
                  history=False, returns_id=False):
        """Get layers

        Parameters
        ----------
        corpus : str, optional
            Corpus ID. Get layers for this corpus.
        name : str, optional
            Filter layer by name.
        fragment_type : str, optional
            Filter layer by fragment type.
        data_type : str, optional
            Filter layer by data type.
        history : boolean, optional
            Whether to return history.  Defaults to False.
        returns_id : boolean, optional.
            Returns IDs rather than dictionaries.

        Returns
        -------
        layers : list
            List of layers in corpus.
        """

        params = {'history': 'on'} if history else {}

        if name:
            params['name'] = name

        if fragment_type:
            params['fragment_type'] = fragment_type

        if data_type:
            params['data_type'] = data_type

        if corpus:
            result = self._corpus(corpus).layer.get(params=params)
        else:
            result = self._layer().get(params=params)

        return self._id(result) if returns_id else result

    @catchCamomileError
    def createLayer(self, corpus,
                    name, description=None,
                    fragment_type=None, data_type=None,
                    annotations=None, returns_id=False):
        """Add new layer to corpus

        Parameters
        ----------
        corpus : str
            Corpus ID.
        name : str
            Layer name.
        description : object, optional
            Layer description.  Must be JSON-serializable.
        fragment_type : object, optional
            Layer fragment type.  Must be JSON-serializable.
        data_type : object, optional
            Layer data type.  Must be JSON-serializable.
        annotations : list, optional
            List of annotations.
        returns_id : boolean, optional.
            Returns IDs rather than dictionaries.

        Returns
        -------
        layer : dict
            Newly created layer.
        """
        layer = {'name': name,
                 'fragment_type': fragment_type if fragment_type else {},
                 'data_type': data_type if data_type else {},
                 'description': description if description else {},
                 'annotations': annotations if annotations else []}

        result = self._corpus(corpus).layer.post(data=layer)

        return self._id(result) if returns_id else result

    @catchCamomileError
    def updateLayer(self, layer,
                    name=None, description=None,
                    fragment_type=None, data_type=None):
        """Update existing layer

        Parameters
        ----------
        layer : str
            Layer ID
        name : str, optional
        description : object, optional
            Must be JSON-serializable.
        fragment_type : str, optional
        data_type : str, optional

        Returns
        -------
        layer : dict
            Updated layer.
        """
        data = {}

        if name is not None:
            data['name'] = name

        if description is not None:
            data['description'] = description

        if fragment_type is not None:
            data['fragment_type'] = fragment_type

        if data_type is not None:
            data['data_type'] = data_type

        return self._layer(layer).put(data=data)

    @catchCamomileError
    def deleteLayer(self, layer):
        """Delete layer

        Parameters
        ----------
        layer : str
            Layer ID
        """
        return self._layer(layer).delete()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ANNOTATIONS
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @catchCamomileError
    def getAnnotation(self, annotation, history=False):
        """Get annotation by ID

        Parameters
        ----------
        annotation : str
            Annotation ID.
        history : boolean, optional
            Whether to return history.  Defaults to False.

        Returns
        -------
        annotation : dict

        """
        params = {'history': 'on'} if history else {}
        return self._annotation(annotation).get(params=params)

    @catchCamomileError
    def getAnnotations(self, layer=None, medium=None,
                       fragment=None, data=None,
                       history=False, returns_id=False,
                       returns_count=False):
        """Get annotations

        Parameters
        ----------
        layer : str, optional
            Filter annotations by layer.
        medium : str, optional
            Filter annotations by medium.
        fragment : optional
            Filter annotations by fragment.
        data : optional
            Filter annotations by data.
        history : boolean, optional
            Whether to return history.  Defaults to False.
        returns_id : boolean, optional.
            Returns IDs rather than dictionaries.
        returns_count : boolean, optional.
            Returns number of annotations instead of annotations

        Returns
        -------
        annotations : list
            List of annotations.

        """

        params = {'history': 'on'} if history else {}
        if medium:
            params['id_medium'] = medium
        if fragment:
            params['fragment'] = fragment
        if data:
            params['data'] = data

        if layer:
            # /layer/:id_layer/annotation
            route = self._layer(layer).annotation
            if returns_count:
                # /layer/:id_layer/annotation/count
                route = route.count
            result = route.get(params=params)

        else:
            # admin user only
            if returns_count:
                # /annotatoin/count does not exist
                raise ValueError('returns_count needs a layer')
            result = self._annotation().get(params=params)

        return (self._id(result)
                if (returns_id and not returns_count)
                else result)

    @catchCamomileError
    def createAnnotation(self, layer, medium=None, fragment=None, data=None,
                         returns_id=False):
        """Create new annotation

        Parameters
        ----------
        layer : str
        medium : str, optional
        fragment :
        data :
        returns_id : boolean, optional.
            Returns IDs rather than dictionaries.
        """
        annotation = {'id_medium': medium,
                      'fragment': fragment if fragment else {},
                      'data': data if data else {}}

        result = self._layer(layer).annotation.post(data=annotation)

        return self._id(result) if returns_id else result

    @catchCamomileError
    def createAnnotations(self, layer, annotations, returns_id=False):
        """
                returns_id : boolean, optional.
            Returns IDs rather than dictionaries.
        """
        result = self._layer(layer).annotation.post(data=annotations)
        return self._id(result) if returns_id else result

    @catchCamomileError
    def updateAnnotation(self, annotation, fragment=None, data=None):
        """Update existing annotation

        Parameters
        ----------
        annotation : str
            Annotation ID
        fragment, data : object, optional

        Returns
        -------
        annotation : dict
            Updated annotation.
        """
        _data = {}

        if fragment is not None:
            _data['fragment'] = fragment

        if data is not None:
            _data['data'] = data

        return self._annotation(annotation).put(data=_data)

    @catchCamomileError
    def deleteAnnotation(self, annotation):
        """Delete existing annotation

        Parameters
        ----------
        annotation : str
            Annotation ID
        """
        return self._annotation(annotation).delete()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # QUEUES
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @catchCamomileError
    def getQueue(self, queue):
        """Get queue by ID

        Parameters
        ----------
        queue : str
            Queue ID.

        Returns
        -------
        queue : dict

        """
        return self._queue(queue).get()

    @catchCamomileError
    def getQueues(self, name=None, returns_id=False):
        """Get queues

        Parameters
        ----------
        name : str, optional
            Filter queues by name.
        returns_id : boolean, optional.
            Returns IDs rather than dictionaries.

        Returns
        -------
        queues : list or dict
        """

        params = {'name': name} if name else {}

        result = self._queue().get(params=params)
        return self._id(result) if returns_id else result

    @catchCamomileError
    def createQueue(self, name, description=None, returns_id=False):
        """Create queue

        Parameters
        ----------
        id_queue : str
            Queue ID
        returns_id : boolean, optional.
            Returns IDs rather than dictionaries.

        Returns
        -------
        queue : dict
            Newly created queue.
        """
        data = {'name': name, 'description': description}
        result = self._queue().post(data=data)
        return self._id(result) if returns_id else result

    @catchCamomileError
    def updateQueue(self, queue, name=None, description=None, elements=None):
        """Update queue

        Parameters
        ----------
        queue : str
            Queue ID

        Returns
        -------
        queue : dict
            Updated queue.
        """
        data = {}

        if name is not None:
            data['name'] = name

        if description is not None:
            data['description'] = description

        if elements is not None:
            data['list'] = elements

        return self._queue(queue).put(data=data)

    @catchCamomileError
    def enqueue(self, queue, elements):
        """Enqueue elements

        Parameters
        ----------
        queue : str
            Queue ID
        elements : list
            List of elements.

        Returns
        -------
        queue : dict
            Updated queue.
        """

        if not isinstance(elements, list):
            elements = [elements]

        return self._queue(queue).next.put(data=elements)

    @catchCamomileError
    def dequeue(self, queue):
        """Dequeue element

        Parameters
        ----------
        queue : str
            Queue ID

        Returns
        -------
        element : object
            Popped element from queue.
        """
        return self._queue(queue).next.get()

    @catchCamomileError
    def pick(self, queue):
        """(Non-destructively) pick first element of queue"""
        return self._queue(queue).first.get()

    @catchCamomileError
    def pickAll(self, queue):
        """(Non-destructively) pick all elements of queue"""
        return self._queue(queue).all.get()

    @catchCamomileError
    def pickLength(self, queue):
        """(Non-destructively) get number of elements in queue"""
        return self._queue(queue).length.get()

    @catchCamomileError
    def deleteQueue(self, queue):
        """Delete existing queue

        Parameters
        ----------
        queue : str
            Queue ID
        """
        return self._queue(queue).delete()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # RIGHTS
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # on a corpus

    @catchCamomileError
    def getCorpusPermissions(self, corpus):
        """Get permissions on existing corpus

        Parameters
        ----------
        corpus : str
            Corpus ID

        Returns
        -------
        permissions : dict
            Permissions on corpus.
        """
        return self._corpus(corpus).permissions.get()

    @catchCamomileError
    def setCorpusPermissions(self, corpus, permission, user=None, group=None):
        """Update permissions on a corpus

        Parameters
        ----------
        corpus : str
            Corpus ID
        user : str, optional
            User ID
        group : str, optional
            Group ID
        permission : 1 (READ), 2 (WRITE) or 3 (ADMIN)
            Read, Write or Admin privileges.

        Returns
        -------
        permissions : dict
            Updated permissions on the corpus.

        """
        if user is None and group is None:
            raise ValueError('')

        data = {'right': permission}

        if user:
            self._corpus(corpus).user(user).put(data=data)

        if group:
            self._corpus(corpus).group(group).put(data=data)

        return self.getCorpusPermissions(corpus)

    @catchCamomileError
    def removeCorpusPermissions(self, corpus, user=None, group=None):
        """Remove permissions on a corpus

        Parameters
        ----------
        corpus : str
            Corpus ID
        user : str, optional
            User ID
        group : str, optional
            Group ID

        Returns
        -------
        permissions : dict
            Updated permissions on the corpus.
        """

        if user is None and group is None:
            raise ValueError('')

        if user:
            self._corpus(corpus).user(user).delete()

        if group:
            self._corpus(corpus).group(group).delete()

        return self.getCorpusPermissions(corpus)

    # on a layer

    @catchCamomileError
    def getLayerPermissions(self, layer):
        """Get permissions on existing layer

        Parameters
        ----------
        layer : str
            Layer ID

        Returns
        -------
        permissions : dict
            Permissions on layer.
        """
        return self._layer(layer).permissions.get()

    @catchCamomileError
    def setLayerPermissions(self, layer, permission, user=None, group=None):
        """Update rights on a layer

        Parameters
        ----------
        layer : str
            Layer ID
        user : str, optional
            User ID
        group : str, optional
            Group ID
        permission : 1 (READ), 2 (WRITE) or 3 (ADMIN)
            Read, Write or Admin privileges.

        Returns
        -------
        permissions : dict
            Updated permissions on the layer.

        """
        if user is None and group is None:
            raise ValueError('')

        data = {'right': permission}

        if user:
            self._layer(layer).user(user).put(data=data)

        if group:
            self._layer(layer).group(group).put(data=data)

        return self.getLayerPermissions(layer)

    @catchCamomileError
    def removeLayerPermissions(self, layer, user=None, group=None):
        """Remove permissions on a layer

        Parameters
        ----------
        layer : str
            Layer ID
        user : str, optional
            User ID
        group : str, optional
            Group ID

        Returns
        -------
        permissions : dict
            Updated permissions on the layer.
        """

        if user is None and group is None:
            raise ValueError('')

        if user:
            self._layer(layer).user(user).delete()

        if group:
            self._layer(layer).group(group).delete()

        return self.getLayerPermissions(layer)

    # on a queue

    @catchCamomileError
    def getQueuePermissions(self, queue):
        """Get permissions on existing queue

        Parameters
        ----------
        queue : str
            Queue ID

        Returns
        -------
        permissions : dict
            Permissions on queue.
        """
        return self._queue(queue).permissions.get()

    @catchCamomileError
    def setQueuePermissions(self, queue, permission, user=None, group=None):
        """Update permissions on a queue

        Parameters
        ----------
        queue : str
            Queue ID
        user : str, optional
            User ID
        group : str, optional
            Group ID
        permission : 1 (READ), 2 (WRITE) or 3 (ADMIN)
            Read, Write or Admin privileges.

        Returns
        -------
        permissions : dict
            Updated permissions on the queue.

        """
        if user is None and group is None:
            raise ValueError('')

        data = {'right': permission}

        if user:
            self._queue(queue).user(user).put(data=data)

        if group:
            self._queue(queue).group(group).put(data=data)

        return self.getQueuePermissions(queue)

    @catchCamomileError
    def removeQueuePermissions(self, queue, user=None, group=None):
        """Remove permissions on a queue

        Parameters
        ----------
        queue : str
            Queue ID
        user : str, optional
            User ID
        group : str, optional
            Group ID

        Returns
        -------
        permissions : dict
            Updated permissions on the queue.
        """

        if user is None and group is None:
            raise ValueError('')

        if user:
            self._queue(queue).user(user).delete()

        if group:
            self._queue(queue).group(group).delete()

        return self.getQueuePermissions(queue)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # METADATA (Corpus, Layer, Medium)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    #
    # CORPUS
    
    @catchCamomileError
    def getCorpusMetadata(self, corpus, path=None):
        """Get Corpus metadatas

        Parameters
        ----------
        corpus : str
            corpus ID
        path : str, optional
            metadata path

        Returns
        -------
        metadatas : dict
            Coprus metadatas
        """
        return self.__getMetadata(self._corpus(corpus), path)
        
    @catchCamomileError
    def getCorpusMetadataKeys(self, corpus, path=None):
        """Get Corpus metadatas first level keys

        Parameters
        ----------
        corpus : str
            corpus ID
        path : str, optional
            metadata path

        Returns
        -------
        keys : List
            Corpus metadatas first level keys
        """
        return self.__getMetadataKeys(self._corpus(corpus), path)
        
    @catchCamomileError
    def setCorpusMetadata(self, corpus, datas, path=None):
        """Set Corpus metadatas

        Parameters
        ----------
        corpus : str
            corpus ID
        datas : dict
            metadatas
        """
        return self.__setMetadata(self._corpus(corpus), datas, path)
        
    @catchCamomileError
    def sendCorpusMetadataFile(self, corpus, path, filepath):
        """Send corpus metadata file

        Parameters
        ----------
        corpus : str
            corpus ID
        path : str
            metadata path
        filepath : str
            metadata filepath
        """
        return self.__sendMetadataFile(self._corpus(corpus), path, filepath)
    
    @catchCamomileError
    def deleteCorpusMetadata(self, corpus, path):
        """Delete Corpus metadatas

        Parameters
        ----------
        corpus : str
            corpus ID
        path : str
            delete path
        """
        return self.__deleteMetadata(self._corpus(corpus), path)
    
    #
    # LAYER
    @catchCamomileError
    def getLayerMetadata(self, layer, path=None):
        """Get Layer metadatas

        Parameters
        ----------
        layer : str
            layer ID
        path : str, optional
            metadata path

        Returns
        -------
        metadatas : dict
            Layer metadatas
        """
        return self.__getMetadata(self._layer(layer), path)
        
    @catchCamomileError
    def getLayerMetadataKeys(self, layer, path=None):
        """Get Layer metadatas first level keys

        Parameters
        ----------
        layer : str
            layer ID
        path : str, optional
            metadata path

        Returns
        -------
        keys : List
            Layer metadatas first level keys
        """
        return self.__getMetadataKeys(self._layer(layer), path)
        
    @catchCamomileError
    def setLayerMetadata(self, layer, datas, path=None):
        """Set Layer metadatas

        Parameters
        ----------
        layer : str
            layer ID
        datas : dict
            metadatas
        """
        return self.__setMetadata(self._layer(layer), datas, path)
        
    @catchCamomileError
    def sendLayerMetadataFile(self, layer, path, filepath):
        """Send layer metadata file

        Parameters
        ----------
        layer : str
            layer ID
        path : str
            metadata path
        filepath : str
            metadata filepath
        """
        return self.__sendMetadataFile(self._layer(layer), path, filepath)
    
    @catchCamomileError
    def deleteLayerMetadata(self, layer, path):
        """Delete Layer metadatas

        Parameters
        ----------
        layer : str
            layer ID
        path : str
            delete path
        """
        return self.__deleteMetadata(self._layer(layer), path)
    
    #
    # MEDIUM
    @catchCamomileError
    def getMediumMetadata(self, medium, path=None):
        """Get Medium metadatas

        Parameters
        ----------
        medium : str
            medium ID
        path : str, optional
            metadata path

        Returns
        -------
        metadatas : dict
            Medium metadatas
        """
        return self.__getMetadata(self._medium(medium), path)
    
    @catchCamomileError     
    def getMediumMetadataKeys(self, medium, path=None):
        """Get Medium metadatas first level keys

        Parameters
        ----------
        medium : str
            medium ID
        path : str, optional
            metadata path

        Returns
        -------
        keys : List
            Medium metadatas first level keys
        """
        return self.__getMetadataKeys(self._medium(medium), path)
       
    @catchCamomileError 
    def setMediumMetadata(self, medium, datas, path=None):
        """Set Medium metadatas

        Parameters
        ----------
        medium : str
            medium ID
        datas : dict
            metadatas
        path : str, optional
            metadata path
        """
        return self.__setMetadata(self._medium(medium), datas, path)
       
    @catchCamomileError 
    def sendMediumMetadataFile(self, medium, path, filepath):
        """Send medium metadata file

        Parameters
        ----------
        medium : str
            medium ID
        path : str
            metadata path
        filepath : str
            metadata filepath
        """
        return self.__sendMetadataFile(self._medium(medium), path, filepath)
    
    @catchCamomileError
    def deleteMediumMetadata(self, medium, path):
        """Delete Medium metadatas

        Parameters
        ----------
        medium : str
            medium ID
        path : str
            delete path
        """
        return self.__deleteMetadata(self._medium(medium), path)

    #
    # PRIVATE METHODS
    def __getMetadata(self, resource,path=None):
        if path is None: 
            return resource.metadata().get()
        
        return resource.metadata(path).get()
        
    def __getMetadataKeys(self, resource, path=None):
        if path is None: 
            return resource.metadata().get()
        
        return resource.metadata(path + '.').get()
        
    def __setMetadata(self, resource, datas, path=None):
        if path != None:
            paths = path.split('.')
            newDatas = {}
            accessor = newDatas
            for i in xrange(len(paths)):
                accessor[paths[i]] = {}
                if i == len(paths) -1:
                    accessor[paths[i]] = datas
                else:
                    accessor = accessor[paths[i]]
            datas = newDatas;
        
        return resource.metadata().post(data=datas)
    
    def __sendMetadataFile(self, resource, path, filepath):
        with open(filepath, "rb") as f:
            data = f.read()
            b64 = data.encode("base64")
            paths = path.split('.')
            datas = {}
            accessor = datas
            for i in xrange(len(paths)):
                accessor[paths[i]] = {}
                if i == len(paths) -1:
                    accessor[paths[i]] = {
                        'type': 'file',
                        'filename': os.path.basename(filepath),
                        'data': b64
                    }
                else:
                    accessor = accessor[paths[i]]
            
        return resource.metadata().post(data=datas)
    
    def __deleteMetadata(self, resource, path):
        return resource.metadata(path).delete()
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # SSE
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @catchCamomileError
    def __startListener(self):
        if self._thread == None:
            datas = self._api.listen.post();
            self._channel_id = datas.channel_id
            self._sseClient = SSEClient("%s/listen/%s" % (self._url, self._channel_id))
            self._thread = threading.Thread(target=self.__listener, name="SSEClient")
            self._thread.isRun = True
            self._thread.daemon = True
            self._thread.start()
        pass
        

    def __listener(self):
        t = threading.currentThread()
        for msg in self._sseClient:
          if not t.isRun:
              break;
          
          if msg.event in self._listenerCallbacks:
              self._listenerCallbacks[msg.event](json.loads(msg.data)['event'])
        pass
    
    @catchCamomileError
    def watchCorpus(self, corpus_id, callback):
        """ Watch corpus for: 
        
        - Add and Remove medium `{'corpus': {:corpus}, 'event': {'add_medium': {:medium}}}`
        - Add and Remove layer `{'corpus': {:corpus}, 'event': {'add_layer': {:layer}}}` 
        - Update corpus attributes `{'corpus': {:corpus}, 'event': {'update': ['description', 'name']}}}`
        
        Parameters
        ----------
        corpus_id : str
            corpus ID
        callback : function
            callback function
        """
        self.__startListener()
        result = self._api.listen(self._channel_id).corpus(corpus_id).put()
        if 'event' in result:
            self._listenerCallbacks['corpus:' + corpus_id] = callback
        return result
    
    @catchCamomileError
    def unwatchCorpus(self, corpus_id):
        """ UnWatch corpus
        
        Parameters
        ----------
        corpus_id : str
            corpus ID
        """  
        result = self._api.listen(self._channel_id).corpus(corpus_id).delete()
        if 'success' in result:
            del self._listenerCallbacks['corpus:' + corpus_id]
        return result
    
    @catchCamomileError
    def watchLayer(self, layer_id, callback):
        """ Watch layer for: 
        
        - Add and Remove annotation `{'layer': {:layer}, 'event': {'add_annotation': {:annotation}}}` 
        - Update layer attributes `{'layer': {:layer}, 'event': {'update': ['name']}}}`
        
        Parameters
        ----------
        layer_id : str
            layer ID
        callback : function
            callback function
        """        
        self.__startListener()
        result = self._api.listen(self._channel_id).layer(layer_id).put()
        if 'event' in result:
            self._listenerCallbacks['layer:' + layer_id] = callback
        return result
    
    @catchCamomileError
    def unwatchLayer(self, layer_id):
        """ UnWatch layer
        
        Parameters
        ----------
        layer_id : str
            layer ID
        """  
        result = self._api.listen(self._channel_id).layer(layer_id).delete()
        if 'success' in result:
            del self._listenerCallbacks['layer:' + layer_id]
        return result
    
    @catchCamomileError
    def watchMedium(self, medium_id, callback):
        """ Watch medium for: 

        - Update medium attributes `{'medium': {:medium}, 'event': {'update': ['url']}}}`
        
        Parameters
        ----------
        medium_id : str
            medium ID
        callback : function
            callback function
        """ 
        self.__startListener()
        result = self._api.listen(self._channel_id).medium(medium_id).put()
        if 'event' in result:
            self._listenerCallbacks['medium:' + medium_id] = callback
        return result
    
    @catchCamomileError
    def unwatchMedium(self, medium_id):
        """ UnWatch medium
        
        Parameters
        ----------
        medium_id : str
            medium ID
        """  
        result = self._api.listen(self._channel_id).medium(medium_id).delete()
        if 'success' in result:
            del self._listenerCallbacks['medium:' + medium_id]
        return result
    
    
    @catchCamomileError
    def watchQueue(self, queue_id, callback):
        """ Watch queue for: 

        - Push item in queue `{'queue': {:queue}, 'event': {'push_item': <new_number_of_items_in_queue>}}` 
        - Pop item in queue `{'queue': {:queue}, 'event': {'pop_item': <new_number_of_items_in_queue>}}`
        
        Parameters
        ----------
        queue_id : str
            queue ID
        callback : function
            callback function
        """
        self.__startListener()
        result = self._api.listen(self._channel_id).queue(queue_id).put()
        if 'event' in result:
            self._listenerCallbacks['queue:' + queue_id] = callback
        return result
    
    @catchCamomileError
    def unwatchQueue(self, queue_id):
        """ UnWatch queue
        
        Parameters
        ----------
        queue_id : str
            queue ID
        """
        result = self._api.listen(self._channel_id).queue(queue_id).delete()
        if 'success' in result:
            del self._listenerCallbacks['queue:' + queue_id]
        return result


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # UTILS
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @catchCamomileError
    def getDate(self):
        return self._api.date.get()
