import requests
BASE='https://api.rentcast.io/v1'

def request(endpoint,address,key):
    if not key: raise ValueError('RentCast key is not configured.')
    response=requests.get(BASE+endpoint,params={'address':address},headers={'X-Api-Key':key,'accept':'application/json'},timeout=18)
    response.raise_for_status()
    return response.json()

def fetch(address,key,include_valuations=False):
    data={'property':request('/properties',address,key)}
    if include_valuations:
        data['value']=request('/avm/value',address,key)
        data['rent']=request('/avm/rent/long-term',address,key)
    return data
