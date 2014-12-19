import camomile.client
import json

if __name__ == '__main__':
    URL = "http://localhost:3000"
    root_client = camomile.client.CamomileClient('root', "camomile", URL, 0.0)

    # create user & group
    user1 = root_client.create_user(username="u1", password="pwd_u1", role="user")
    user1_client = camomile.client.CamomileClient('u1', "pwd_u1", URL, 0.0)
    user2 = root_client.create_user(username="u2", password="pwd_u2", role="admin")
    user2_client = camomile.client.CamomileClient('u2', "pwd_u2", URL, 0.0)
    group1 = root_client.create_group(name="g2")
    group1 = root_client.add_user_to_a_group(group1['_id'], user2['_id'])

    # create corpus
    corpus1 = root_client.create_corpus(name="c1", description={"phase":"2", "set":"train"})
    corpus2 = root_client.create_corpus(name="c2", description={"phase":"2", "set":"test"})

    # get ACL of a corpus
    ACL = root_client.get_ACL_of_a_corpus(corpus1['_id'])
    print json.dumps(ACL['ACL'], indent=2, sort_keys=True)

    # update ACL corpus
    mes = root_client.update_user_ACL_of_a_corpus(corpus1['_id'], user1['_id'], right="W")
    print json.dumps(mes, indent=2, sort_keys=True)
    mes = root_client.update_group_ACL_of_a_corpus(corpus1['_id'], group1['_id'], right="R")
    print json.dumps(mes, indent=2, sort_keys=True)


