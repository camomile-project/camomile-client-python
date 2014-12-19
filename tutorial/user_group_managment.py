import camomile.client
import json

if __name__ == '__main__':
    URL = "http://localhost:3000"
    root_client = camomile.client.CamomileClient('root', "camomile", URL, 0.0)

    # print information on user logged in
    user = root_client.me()
    print json.dumps(user, indent=2, sort_keys=True)

    # create a user
    user1 = root_client.create_user(username="u1", password="pwd_u1", role="user")
    print json.dumps(user1, indent=2, sort_keys=True)

    # loggin as u1
    user1_client = camomile.client.CamomileClient('u1', "pwd_u1", URL, 0.0)
    user1 = user1_client.me()
    print json.dumps(user1, indent=2, sort_keys=True)

    # get all user
    mes = root_client.get_all_user()
    print json.dumps(mes, indent=2, sort_keys=True) 

    # update user
    user1 = root_client.update_user(user1['_id'], role="admin")
    print json.dumps(user1, indent=2, sort_keys=True)    

    # create group
    group1 = root_client.create_group(name="g1")
    print json.dumps(group1, indent=2, sort_keys=True)    

    # add_user_to_a_group
    group1 = root_client.add_user_to_a_group(group1['_id'], user1['_id'])
    print json.dumps(group1, indent=2, sort_keys=True)      

    # get_all_group_of_a_user
    l_group = root_client.get_all_group_of_a_user(user1['_id'])
    print json.dumps(l_group, indent=2, sort_keys=True)       

   	# delete_group
    mes = root_client.delete_group(group1['_id'])
    print json.dumps(mes, indent=2, sort_keys=True)  

   	# delete_user
    mes = root_client.delete_user(user1['_id'])
    print json.dumps(mes, indent=2, sort_keys=True)    

   	# logout
    mes = user1_client.logout()
    print json.dumps(mes, indent=2, sort_keys=True)
    mes = root_client.logout()
    print json.dumps(mes, indent=2, sort_keys=True)      	 	