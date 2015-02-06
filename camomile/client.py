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

    def __init__(self, url, username=None, password=None, delay=None):
        super(Camomile, self).__init__()

        # internally rely on tortilla generic API wrapper
        # see http://github.com/redodo/tortilla
        self._api = tortilla.wrap(url, format='json')

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

    # def _check_error(self, resp):
    #     if 400 <= resp.status_code < 600:
    #         try:
    #             msg = '%s Error: %s - %s' % (
    #                 resp.status_code, resp.reason, resp.json()['message'])
    #         except:
    #             msg = '%s Error: %s' % (resp.status_code, resp.reason)
    #         raise requests.exceptions.HTTPError(msg, response=resp)

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

    def _media(self, medium=None):
        media = self._api.media
        if medium:
            media = media(medium)
        return media

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

    def login(self, username, password):
        """Login

        Parameters
        ----------
        username, password : str

        """
        data = {'username': username,
                'password': password}
        return self._api.login.post(data=data)

    def logout(self):
        """Logout"""
        return self._api.logout.post()

    def me(self, returns_id=False):
        """Get information about logged in user"""
        result = self._api.me.get()
        return self._id(result) if returns_id else result

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # USERS
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

    def deleteUser(self, user):
        """Delete existing user

        Parameters
        ----------
        user : str
            User ID.
        """
        return self._user(user).delete()

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

        result = self._group.post(data=data)
        return self._id(result) if returns_id else result

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

    def deleteGroup(self, group):
        """Delete existing group

        Parameters
        ----------
        group : str
            Group ID.
        """
        return self._group(group).delete()

    def addUserToGroup(self, user, group):
        return self._group(group).user(user).put()

    def removeUserFromGroup(self, user, group):
        return self._group(group).user(user).delete()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # CORPORA
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
        params = {'history': 'on' if history else 'off'}
        return self._corpus(corpus).get(params=params)

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
        params = {'history': 'on' if history else 'off'}
        if name:
            params['name'] = name

        result = self._corpus().get(params=params)
        return self._id(result) if returns_id else result

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
        result = self._corpus.post(data=data)
        return self._id(result) if returns_id else result

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
        params = {'history': 'on' if history else 'off'}
        return self._media(medium).get(params=params)

    def getMedia(self, corpus=None, name=None, returns_id=False):
        """Get media

        Parameters
        ----------
        corpus : str, optional
            Corpus ID. Get media for this corpus.
        name : str, optional
            Filter medium by name.
        returns_id : boolean, optional.
            Returns IDs rather than dictionaries.

        Returns
        -------
        media : list
            List of media
        """

        params = {'name': name} if name else None

        if corpus:
            result = self._corpus(corpus).media.get(params=params)
        else:
            result = self._media().get(params=params)

        return self._id(result) if returns_id else result

    def createMedium(self, corpus, name, url=None, description=None,
                     returns_id=False):
        """Add new medium to corpus

        Parameters
        ----------
        corpus : str
            Corpus ID.
        name : str
            Media name.
        description : object, optional
            Media description.  Must be JSON-serializable.
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

        result = self._corpus(corpus).media.post(data=medium)
        return self._id(result) if returns_id else result

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
        result = self._corpus(corpus).media.post(data=media)
        return self._id(result) if returns_id else result

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

        return self._media(medium).put(data=data)

    def deleteMedium(self, medium):
        """Delete existing medium

        Parameters
        ----------
        medium : str
            Medium ID
        """
        return self._media(medium).delete()

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

        return self._media(medium).get(format)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # LAYERS
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
        params = {'history': 'on' if history else 'off'}
        return self._layer(layer).get(params=params)

    def getLayers(self, corpus=None, name=None, returns_id=False):
        """Get layers

        Parameters
        ----------
        corpus : str, optional
            Corpus ID. Get layers for this corpus.
        name : str, optional
            Filter layer by name.
        returns_id : boolean, optional.
            Returns IDs rather than dictionaries.

        Returns
        -------
        layers : list
            List of layers in corpus.
        """

        params = {'name': name} if name else None

        if corpus:
            result = self._corpus(corpus).layer.get(params=params)
        else:
            result = self._layer().get(params=params)

        return self._id(result) if returns_id else result

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
        params = {'history': 'on' if history else 'off'}
        return self._annotation(annotation).get(params=params)

    def getAnnotations(self, layer=None, medium=None,
                       history=False, returns_id=False):
        """Get annotations

        Parameters
        ----------
        layer : str, optional
            Filter annotations by layer.
        medium : str, optional
            Filter annotations by medium.
        history : boolean, optional
            Whether to return history.  Defaults to False.
        returns_id : boolean, optional.
            Returns IDs rather than dictionaries.

        Returns
        -------
        annotations : list
            List of annotations.

        """

        params = {}
        if medium:
            params['media'] = medium
        params['history'] = 'on' if history else 'off'

        if layer:
            result = self._layer(layer).annotation.get(params=params)

        else:
            # admin user only
            result = self._annotation().get(params=params)

        return self._id(result) if returns_id else result

    def createAnnotation(self, layer, media=None, fragment=None, data=None,
                         returns_id=False):
        """
        returns_id : boolean, optional.
            Returns IDs rather than dictionaries.
        """
        annotation = {'id_media': media,
                      'fragment': fragment if fragment else {},
                      'data': data if data else {}}

        result = self._layer(layer).annotation.post(data=annotation)

        return self._id(result) if returns_id else result

    def createAnnotations(self, layer, annotations, returns_id=False):
        """
                returns_id : boolean, optional.
            Returns IDs rather than dictionaries.
        """
        result = self._layer(layer).annotation.post(data=annotations)
        return self._id(result) if returns_id else result

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
        data = {}

        if fragment is not None:
            data['fragment'] = fragment

        if data is not None:
            data['data'] = data

        return self._annotation(annotation).put(data=data)

    def deleteAnnotation(self, annotation):
        """Delete existing annotation

        Parameters
        ----------
        annotation : str
            Annotation ID
        """
        return self._annotation(annotation).delete()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # RIGHTS
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # on a corpus

    def getCorpusRights(self, corpus):
        """Get rights on existing corpus

        Parameters
        ----------
        corpus : str
            Corpus ID

        Returns
        -------
        rights : dict
            Rights on corpus.
        """
        return self._corpus(corpus).ACL.get()

    def setCorpusRights(self, corpus, right, user=None, group=None):
        """Update rights on a corpus

        Parameters
        ----------
        corpus : str
            Corpus ID
        user : str, optional
            User ID
        group : str, optional
            Group ID
        right : {'O', 'W', 'R'}
            Owner, writer or reader.

        Returns
        -------
        rights : dict
            Updated rights on the corpus.

        """
        if user is None and group is None:
            raise ValueError('')

        data = {'right': right}

        if user:
            self._corpus(corpus).user(user).put(data=data)

        if group:
            self._corpus(corpus).group(group).put(data=data)

        return self.getCorpusRights(corpus)

    def removeCorpusRights(self, corpus, user=None, group=None):
        """Remove rights on a corpus

        Parameters
        ----------
        corpus : str
            Corpus ID
        user : str, optional
            User ID
        group : str, optional
            Group ID
        right : {'O', 'W', 'R'}
            Owner, writer or reader.

        Returns
        -------
        rights : dict
            Updated rights on the corpus.
        """

        if user is None and group is None:
            raise ValueError('')

        if user:
            self._corpus(corpus).user(user).delete()

        if group:
            self._corpus(corpus).group(group).delete()

        return self.getCorpusRights(corpus)

    # on a layer

    def getLayerRights(self, layer):
        """Get rights on existing layer

        Parameters
        ----------
        layer : str
            Corpus ID

        Returns
        -------
        rights : dict
            Rights on layer.
        """
        return self._layer(layer).ACL.get()

    def setLayerRights(self, layer, right, user=None, group=None):
        """Update rights on a layer

        Parameters
        ----------
        layer : str
            Layer ID
        user : str, optional
            User ID
        group : str, optional
            Group ID
        right : {'O', 'W', 'R'}
            Owner, writer or reader.

        Returns
        -------
        rights : dict
            Updated rights on the layer.

        """
        if user is None and group is None:
            raise ValueError('')

        data = {'right': right}

        if user:
            self._layer(layer).user(user).put(data=data)

        if group:
            self._layer(layer).group(group).put(data=data)

        return self.getLayerRights(layer)

    def removeLayerRights(self, layer, user=None, group=None):
        """Remove rights on a layer

        Parameters
        ----------
        layer : str
            Layer ID
        user : str, optional
            User ID
        group : str, optional
            Group ID
        right : {'O', 'W', 'R'}
            Owner, writer or reader.

        Returns
        -------
        rights : dict
            Updated rights on the layer.
        """

        if user is None and group is None:
            raise ValueError('')

        if user:
            self._layer(layer).user(user).delete()

        if group:
            self._layer(layer).group(group).delete()

        return self.getLayerRights(layer)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # QUEUES
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

    def getQueues(self, returns_id=False):
        """Get queues

        Parameters
        ----------
        returns_id : boolean, optional.
            Returns IDs rather than dictionaries.

        Returns
        -------
        queues : list or dict
        """
        result = self._queue().get()
        return self._id(result) if returns_id else result

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
        result = self._queue.post(data=data)
        return self._id(result) if returns_id else result

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
        data = {'list': elements}

        return self._queue(queue).next.put(data=data)

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

    def deleteQueue(self, queue):
        """Delete existing queue

        Parameters
        ----------
        queue : str
            Queue ID
        """
        return self._queue(queue).delete()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # UTILS
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getDate(self):
        return self._api.date.get()
