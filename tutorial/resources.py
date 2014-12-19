import camomile.client
import json
from pyannote.parser import REPEREParser

if __name__ == '__main__':
    URL = "http://localhost:3000"
    root_client = camomile.client.CamomileClient('root', "camomile", URL, 0.0)

    # create corpus
    corpus1 = root_client.create_corpus(name='c1', 
                                        description={"phase":"2", "set":"test"})
    print json.dumps(corpus1, indent=2, sort_keys=True)

    # add layer
    layer1 = root_client.add_layer(corpus1['_id'], 
                                   name="speaker_id_multi_sup", 
                                   fragment_type="segment", 
                                   data_type="name")
    print json.dumps(layer1, indent=2, sort_keys=True) 

    # add media
    l_id_media=[]
    for i in range(10):
        media = root_client.add_media(corpus1['_id'], 
                                      name="media"+str(i), 
                                      url="http://media"+str(i))
        l_id_media.append(media['_id'])
    
    # get_all_media_of_a_corpus
    l_media = root_client.get_all_media_of_a_corpus(corpus1['_id'])
    print json.dumps(l_media, indent=2, sort_keys=True) 

    # add annotation
    for id_media in l_id_media:
        for i in range(3):
            annotation = root_client.add_annotation(layer1['_id'], 
                                                    id_media=id_media, 
                                                    data="name_"+str(i), 
                                                    fragment={"start":i*2, "end":i*2+3})

    # get_all_annotation_of_a_layer
    l_annotation = root_client.get_all_annotation_of_a_layer(layer1['_id'])
    print json.dumps(l_annotation, indent=2, sort_keys=True) 

    # get_all_annotation_of_a_layer
    l_annotation = root_client.get_all_annotation_of_a_layer(layer1['_id'], l_id_media[0])
    print json.dumps(l_annotation, indent=2, sort_keys=True)

    # update_annotation
    l_annotation[0]['_id']
    annotation = root_client.update_annotation(l_annotation[0]['_id'],  
                                               id_media=id_media, 
                                               data="name_"+str(i), 
                                               fragment={"start":30, "end":56})
    print json.dumps(annotation, indent=2, sort_keys=True)

    # create layer with annotations in 1 request
    l_anno = []
    parser = REPEREParser().read("sample.repere")
    l_id_media = []
    for show in parser.uris:
        media = root_client.add_media(corpus1['_id'], name=show)
        l_id_media.append((show, media['_id']))
        annotation = parser(uri=show, modality="speaker")
        for segment, track, label in annotation.itertracks(label=True):
            l_anno.append({"id_media":media['_id'], "fragment":{"start":segment.start , "end":segment.end}, "data":label})

    l_speaker_id_multi_sup = root_client.add_layer(corpus1['_id'], 
                                                   name="speaker_id_multi_sup2", 
                                                   fragment_type="segment", 
                                                   data_type="name", 
                                                   annotations=l_anno)

    l_a = root_client.get_all_annotation_of_a_layer(l_speaker_id_multi_sup['_id'], l_id_media[0][1])
    for a in l_a:
        print l_id_media[0][0], a['fragment']['start'], a['fragment']['end'], a['data']

