"""Actual radius search, sold property records + asking rental listings.
All imported candidates are unverified and unselected by design.
"""
from datetime import date
import requests
from services.rentcast import BASE


def sale_row(record):
    if not isinstance(record,dict): return None
    price=record.get('lastSalePrice')
    when=record.get('lastSaleDate')
    if not price or not when: return None
    return {
        'include':False,'address':str(record.get('formattedAddress') or ''),
        'amount':float(price),'sqft':float(record.get('squareFootage') or 0),
        'bedrooms':record.get('bedrooms'), 'date':str(when)[:10],
        'renovated':False, 'source':'RentCast property record (unverified sale)',
        'date_type':'reported last sale date — verify county closing',
        'latitude':record.get('latitude'),'longitude':record.get('longitude'),
        'status':'Reported prior sale',
    }


def rental_row(record):
    if not isinstance(record,dict): return None
    price=record.get('price')
    if not price or not (record.get('listedDate') or record.get('lastSeenDate')):return None
    return {
        'include':False,'address':str(record.get('formattedAddress') or ''),
        'amount':float(price),'sqft':float(record.get('squareFootage') or 0),
        'bedrooms':record.get('bedrooms'),
        'date':str(record.get('lastSeenDate') or record.get('listedDate'))[:10],
        'renovated':False,'source':'RentCast rental listing (asking rent)',
        'date_type':'listing activity — not signed lease',
        'latitude':record.get('latitude'),'longitude':record.get('longitude'),
        'status':record.get('status','Unknown'),
    }


def query_params(address,radius,age_months,kind='Single Family'):
    if not address.strip():raise ValueError('A complete subject address is required.')
    if radius not in (0.5,1.0,2.0,3.0,5.0,10.0):raise ValueError('Unsupported radius.')
    if age_months not in (3,6,9,12,18,24):raise ValueError('Unsupported age window.')
    ptype='Single Family' if kind=='Single Family' else 'Multi-Family'
    p={'address':address.strip(),'radius':radius,'propertyType':ptype,'limit':30}
    return dict(p,saleDateRange=int(age_months*30.44)),dict(p,status='Active')


def search_nearby(address,key,radius,age_months,kind='Single Family', session=None):
    if not key:raise ValueError('Missing RentCast key')
    sold_params,rent_params=query_params(address,radius,age_months,kind)
    get=(session or requests).get
    responses=[]
    for endpoint,params in [('/properties',sold_params),('/listings/rental/long-term',rent_params)]:
        r=get(BASE+endpoint,params=params,headers={'X-Api-Key':key,'accept':'application/json'},timeout=20)
        r.raise_for_status()
        payload=r.json()
        if not isinstance(payload,list):raise ValueError('Unexpected provider response')
        responses.append(payload)
    subject=address.strip().casefold()
    def normalize(records,parser):
        rows=[]; seen=set()
        for record in records:
            row=parser(record)
            if not row or not row['address'] or row['address'].casefold()==subject:continue
            if row['address'].casefold() in seen:continue
            seen.add(row['address'].casefold());rows.append(row)
        return rows
    return {'sale':normalize(responses[0],sale_row),'rent':normalize(responses[1],rental_row)}
