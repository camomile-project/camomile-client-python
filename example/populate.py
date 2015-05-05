# The MIT License (MIT)

# Copyright (c) 2014-2015 CNRS

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# === EDIT ====================================================================

SERVER = 'http://localhost:12345'
ROOT_PASSWORD = 'password'

# admin usernname and password
ADMIN = 'administrator'
ADMIN_PASSWORD = 'password'

# template of path to video files (relative to /media)
URL = 'REPERE/phase2/test/{name}'

# =============================================================================

from camomile import Camomile

client = Camomile(SERVER)

# login as root
client.login('root', ROOT_PASSWORD)

# create new admin user
admin = client.createUser(ADMIN, ADMIN_PASSWORD, role='admin', returns_id=True)

# login as admin
client.login(ADMIN, ADMIN_PASSWORD)

# create new corpus
corpus = client.createCorpus('REPERE', returns_id=True)

# add media to corpus and keep track of their IDs
mediaID = {}
with open('media.lst', 'r') as f:
    for medium in f:

        # remove trailing "\n"
        name = medium.strip()

        # create medium
        mediaID[name] = client.createMedium(
            corpus, name, url=URL.format(name=name), returns_id=True)


# parse sample annotation files
def parse(path, mediaID):

    annotations = []

    with open(path, 'r') as f:

        for line in f:

            # remove trailing "\n" and split on spaces
            tokens = line.strip().split()

            # get medium ID
            mediumName = tokens[0]
            id_medium = mediaID[mediumName]

            # get fragment start and end times
            startTime = float(tokens[1])
            endTime = float(tokens[2])

            # get data
            label = tokens[4]

            annotation = {'fragment': {'start': startTime, 'end': endTime},
                          'data': label,
                          'id_medium': id_medium}

            # append annotations to the list
            annotations.append(annotation)

    return annotations


# create reference layer
annotations = parse('reference.repere', mediaID)
reference = client.createLayer(
    corpus, 'reference',
    fragment_type='segment',
    data_type='label',
    annotations=annotations,
    returns_id=True)

# create hypothesis layers
for i in [2]:
    path = 'hypothesis{i}.repere'.format(i=i)
    annotations = parse(path, mediaID)
    hypothesis = client.createLayer(
        corpus,
        'hypothesis {i}'.format(i=i),
        fragment_type='segment',
        data_type='label',
        annotations=annotations,
        returns_id=True)
