import camomile.client
import json
from pyannote.parser import REPEREParser
import glob, time

if __name__ == '__main__':
    URL = "http://localhost:3000"
    root_client = camomile.client.CamomileClient('root', "camomile", URL, False)

    #URL = "https://flower.limsi.fr/api_v2"
    #root_client = camomile.client.CamomileClient('root', "camomilev2", URL, False)

    path = '/Users/poignant/Documents/Dev/REPERE/data/error_analysis/'
    
    
    code, l_corpus = root_client.get_all_corpus()
    for ele in l_corpus:
        root_client.delete_corpus(ele["_id"])
    
    code, l_annotation = root_client.get_all_annotation()
    for ele in l_annotation:
        root_client.delete_annotation(ele["_id"])

    code, l_layer = root_client.get_all_layer()
    for ele in l_layer:
        root_client.delete_layer(ele["_id"])

    code, l_media = root_client.get_all_media()
    for ele in l_media:
        root_client.delete_media(ele["_id"])


    code, corpus = root_client.create_corpus({"name":"REPERE_test2", "description":{"phase":"2", "set":"test"}})

    code, l_media = root_client.add_medias(corpus['_id'], {"media_list":[{"name":"m1"}, {"name":"m2"}]})
    print json.dumps(l_media, indent=2, sort_keys=True)



    data_layer = {"name":"l1", "fragment_type":"segment", "data_type":"name", 'annotations':[]}
    data_layer['annotations'].append({"media_name":"m1", "fragment":{"start":10 , "end":20}, "data":"truc1"})
    data_layer['annotations'].append({"media_name":"m1", "fragment":{"start":15 , "end":240}, "data":"truc2"})
    data_layer['annotations'].append({"media_name":"m1", "fragment":{"start":18 , "end":210}, "data":"truc3"})
    data_layer['annotations'].append({"media_name":"m2", "fragment":{"start":19 , "end":200}, "data":"truc4"})

    code, layer = root_client.add_layer(corpus['_id'], data_layer)
    print json.dumps(layer, indent=2, sort_keys=True)

    code, l_annotation = root_client.add_annotations(layer['_id'], {"annotation_list":[{"fragment":"a1", "id_media":l_media[0]['_id'], "data":"truc1"},
    																				   {"fragment":"a2", "id_media":l_media[1]['_id'], "data":"truc2"}]})
    print json.dumps(l_annotation, indent=2, sort_keys=True)


    '''
    for f in glob.glob(path+'*'):

        i=0

        print f
        data_layer = {"name":f.split('/')[-1], "fragment_type":"segment", "data_type":"name", 'annotations':[]}
        parser = REPEREParser().read(f)
        for show in parser.uris:
            print show
            code, media = root_client.add_media(corpus['_id'], {"name":show})
            time.sleep(0.5)

            code, media = root_client.add_media(corpus['_id'], {"name":show})
            annotation = parser(uri=show, modality="speaker")
            for segment, track, label in annotation.itertracks(label=True):
                data_layer['annotations'].append({"media_name":show, "fragment":{"start":segment.start , "end":segment.end}, "data":label})

            i+=1
            if i > 30:
                break
    
        code, layer = root_client.add_layer(corpus['_id'], data_layer)
        time.sleep(0.5)
    '''
    '''
    code, l_l = root_client.get_all_layer()
    id_groundtruth_speaker_id = ''
    for l in l_l:
        if l['name'] == 'speaker_id_multi_sup':
            id_groundtruth_speaker_id = l['_id']

    code, l_m = root_client.get_all_media()
    dic_m = {}
    for m in l_m:
        dic_m[m['_id']]=m['name']
        dic_m[m['name']]=m['_id']

    code, l_a = root_client.get_all_annotation_of_a_layer(id_groundtruth_speaker_id, dic_m['LCP_TopQuestions_2013-04-24_232600'])
    for a in l_a:
        print dic_m[a['id_media']], a['fragment']['start'], a['fragment']['end'], a['data']
    '''

    #print json.dumps(l_a, indent=2, sort_keys=True)

    







