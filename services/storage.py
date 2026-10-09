"""Per-user deal storage using Supabase Auth JWT and RLS policies."""
from supabase import create_client

def client(url,key): return create_client(url,key)

def login(url,key,email,password):
    c=client(url,key)
    response=c.auth.sign_in_with_password({'email':email,'password':password})
    return response.session.access_token, response.user.id

def save_deal(url,key,token,user_id,title,payload):
    import requests
    response=requests.post(url.rstrip('/')+'/rest/v1/deals',headers={'apikey':key,'Authorization':'Bearer '+token,'Prefer':'return=representation','Content-Type':'application/json'},json={'user_id':user_id,'title':title,'payload':payload},timeout=12)
    response.raise_for_status()
    return response.json()

def list_deals(url,key,token):
    import requests
    response=requests.get(url.rstrip('/')+'/rest/v1/deals',params={'select':'id,title,created_at,payload','order':'created_at.desc','limit':100},headers={'apikey':key,'Authorization':'Bearer '+token},timeout=12)
    response.raise_for_status()
    return response.json()
