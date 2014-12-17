import camomile.client
import json

if __name__ == '__main__':
    URL = "http://localhost:3000"
    root_client = camomile.client.CamomileClient('root', "camomile", URL, False)

    # print information on user logged in
    code, user = root_client.me()
    print json.dumps(user, indent=2, sort_keys=True)

    # create a user
    data = {"username":"u1", "password":"pwd_u1", "role":"user"}
    code, user1 = root_client.create_user(data)
    print json.dumps(user1, indent=2, sort_keys=True)

    # loggin as u1
    user1_client = camomile.client.CamomileClient('u1', "pwd_u1", URL, False)
    code, user1 = user1_client.me()
    print json.dumps(user1, indent=2, sort_keys=True)

    # get all user
    code, mes = root_client.get_all_user()
    print json.dumps(mes, indent=2, sort_keys=True) 

    # update user
    data = {"role":"admin"}
    code, user1 = root_client.update_user(user1['_id'], data)
    print json.dumps(user1, indent=2, sort_keys=True)    

    # create group
    data = {"name":"g1"}
    code, group1 = root_client.create_group(data)
    print json.dumps(group1, indent=2, sort_keys=True)    

    # add_user_to_a_group
    code, group1 = root_client.add_user_to_a_group(group1['_id'], user1['_id'])
    print json.dumps(group1, indent=2, sort_keys=True)      

    # get_all_group_of_a_user
    code, l_group = root_client.get_all_group_of_a_user(user1['_id'])
    print json.dumps(l_group, indent=2, sort_keys=True)       

   	# delete_group
    code, mes = root_client.delete_group(group1['_id'])
    print json.dumps(mes, indent=2, sort_keys=True)  

   	# delete_user
    code, mes = root_client.delete_user(user1['_id'])
    print json.dumps(mes, indent=2, sort_keys=True)    

   	# logout
    code, mes = user1_client.logout()
    print json.dumps(mes, indent=2, sort_keys=True)
    code, mes = root_client.logout()
    print json.dumps(mes, indent=2, sort_keys=True)      	 	