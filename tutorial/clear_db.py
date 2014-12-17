import camomile.client
import json



if __name__ == '__main__':
	URL = "http://localhost:3000"
	root_client = camomile.client.CamomileClient('root', "camomile", URL, False)

	code, l_queue = root_client.get_all_queue()
	for ele in l_queue:
		root_client.delete_queue(ele["_id"])

	code, l_annotation = root_client.get_all_annotation()
	for ele in l_annotation:
		root_client.delete_annotation(ele["_id"])

	code, l_layer = root_client.get_all_layer()
	for ele in l_layer:
		root_client.delete_layer(ele["_id"])

	code, l_media = root_client.get_all_media()
	for ele in l_media:
		root_client.delete_media(ele["_id"])

	code, l_corpus = root_client.get_all_corpus()
	for ele in l_corpus:
		root_client.delete_corpus(ele["_id"])

	code, l_group = root_client.get_all_group()
	for ele in l_group:
		root_client.delete_group(ele["_id"])

	code, l_user = root_client.get_all_user()
	for ele in l_user:
		root_client.delete_user(ele["_id"])