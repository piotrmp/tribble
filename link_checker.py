import requests

def check_link(title,origin_wiki, session):
    #title = 'Tolosa'
    #origin_wiki = 'oc'
    url = 'https://' + origin_wiki + '.wikipedia.org/w/api.php?action=query&titles=' + requests.utils.quote(
        title) + '&prop=langlinks&lllimit=max&format=json'
    response = session.get(url)
    
    response_json = response.json()
    if response.status_code != 200:
        raise RuntimeError("Denied API request with code: " + str(response.status_code))
    
    destination_wiki = 'es'
    linked_title = None
    assert('query' in response_json)
    assert('pages' in response_json['query'])
    assert(len(response_json['query']['pages'])==1)
    if 'langlinks' in list(response_json['query']['pages'].values())[0]:
        for langitem in list(response_json['query']['pages'].values())[0]['langlinks']:
            if langitem['lang'] == destination_wiki:
                linked_title = langitem['*']
                break
    return linked_title
