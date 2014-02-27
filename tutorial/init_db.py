import camomile.client

URL = 'https://server/'
ROOT_PASSWORD = 'h0lyMo1y'

# connect as root
root_client = camomile.client.FullFeaturedCamomileClient(
    'root', ROOT_PASSWORD, URL)

# create admin user
ADMIN_USER_LOGIN = 'user1'
ADMIN_USER_PASSWORD = 's3cr37'
ADMIN_USER_AFFILIATION = 'NSA'

root_client.create_user(
    ADMIN_USER_LOGIN, ADMIN_USER_PASSWORD,
    ADMIN_USER_AFFILIATION,
    role=root_client.ROLE_ADMIN
)

# connect as admin
admin_client = camomile.client.FullFeaturedCamomileClient(
    ADMIN_USER_LOGIN, ADMIN_USER_PASSWORD, URL)

# create basic user
BASIC_USER_LOGIN = 'user2'
BASIC_USER_PASSWORD = 'p4ssw0rd'
BASIC_USER_AFFILIATION = 'DGA'

admin_client.create_user(
    BASIC_USER_LOGIN, BASIC_USER_PASSWORD,
    BASIC_USER_AFFILIATION, role=admin_client.ROLE_USER
)

# create another basic user
LIMITED_USER_LOGIN = 'user3'
LIMITED_USER_PASSWORD = 'l33t'
LIMITED_USER_AFFILITATION = 'Self-employed'

admin_client.create_user(
    LIMITED_USER_LOGIN, LIMITED_USER_PASSWORD, LIMITED_USER_AFFILITATION,
    role=admin_client.ROLE_USER)

# create corpus
CORPUS_NAME = 'REPERE phase2 test'
corpus = admin_client.new_corpus(CORPUS_NAME)

# add media to corpus
MEDIA_NAME = 'BFMTV_BFMStory_2012-07-24_175800'
MEDIA_PATH = 'REPERE/phase2/test/BFMTV_BFMStory_2012-07-24_175800'
media = corpus.new_media(MEDIA_NAME, MEDIA_PATH)

# add reference layer to corpus
REF_LAYER_TYPE = 'Reference'
REF_LAYER_FRAGMENT_TYPE = 'segment'
REF_LAYER_DATA_TYPE = 'label'
REF_LAYER_SOURCE = 'Edward Snowden'

ref_layer = media.new_layer(
    REF_LAYER_TYPE,
    REF_LAYER_FRAGMENT_TYPE, REF_LAYER_DATA_TYPE,
    REF_LAYER_SOURCE
)

# add a few annotations to reference and hypothesis layers
ref_layer.new_annotation({'start': 0, 'end': 10}, 'Angela_MERKEL')
ref_layer.new_annotation({'start': 10, 'end': 30}, 'Francois_HOLLANDE')

# add hypothesis layer to corpus
HYP_LAYER_TYPE = 'Hypothesis'
HYP_LAYER_FRAGMENT_TYPE = 'segment'
HYP_LAYER_DATA_TYPE = 'label'
HYP_LAYER_SOURCE = 'Julian Assange'

hyp_layer = media.new_layer_with(
    HYP_LAYER_TYPE,
    HYP_LAYER_FRAGMENT_TYPE, HYP_LAYER_DATA_TYPE,
    HYP_LAYER_SOURCE,
    annotations=[
        {'fragment': {'start': 0, 'end': 20}, 'data': 'Angela_MERKEL'},
        {'fragment': {'start': 15, 'end': 30}, 'data': 'Vladimir_POUTINE'},
    ]
)

# give read access to basic user for the whole corpus
corpus.set_acl(BASIC_USER_LOGIN, 'R')

# give write access to limited user for one hypothesis layer
# hyp_layer.set_acl(LIMITED_USER_LOGIN, 'E')
