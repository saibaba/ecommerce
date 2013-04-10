from urlparse import urlparse

def sanitize(obj):

    if 'lastUpdateDate' in obj:
        obj['lastUpdateDate'] = obj['lastUpdateDate'].isoformat()
    if 'creationDate' in obj:
        obj['creationDate'] = obj['creationDate'].isoformat()
    if '_id' in obj:
        obj['_id'] = str(obj['_id'])

    return obj

def url_to_objloc(url):
    o = urlparse(url)
    p = o.path.split("/") 
    if len(p) > 1:
        c = p[-2]
        id = p[-1]
        return(c, id)
    else:
        return None
