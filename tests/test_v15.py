from core.engine import Deal,analyze
from core.insights import build_insights
from services.market_search import query_params,sale_row,rental_row,search_nearby


def test_insight_output():
    d=Deal(); out=build_insights(d,analyze(d))
    assert set(out)=={'strengths','risks','verifications'}
    assert out['strengths'] or out['risks']
    assert out['verifications']


def test_params_use_real_radius_and_sale_age():
    s,r=query_params('123 Main St, Lakewood, OH',2.0,6)
    assert s['radius']==r['radius']==2.0
    assert 180 <= s['saleDateRange'] <= 184
    assert r['status']=='Active'


def test_malformed_or_incomplete_records_excluded():
    assert sale_row({'lastSalePrice':1000}) is None
    assert rental_row({'price':2000}) is None
    s=sale_row({'formattedAddress':'A','lastSalePrice':200000,'lastSaleDate':'2026-01-01'})
    assert s['include'] is False and s['renovated'] is False


def test_search_calls_two_endpoints_and_filters_subject():
    class Resp:
        def __init__(self,data):self.data=data
        def raise_for_status(self):pass
        def json(self):return self.data
    class Client:
        def __init__(self):self.paths=[]
        def get(self,url,**kwargs):
            self.paths.append(url)
            if url.endswith('/properties'):
                return Resp([{'formattedAddress':'Neighbor','lastSalePrice':150000,'lastSaleDate':'2026-04-01'},
                             {'formattedAddress':'Subject','lastSalePrice':150000,'lastSaleDate':'2026-04-01'}])
            return Resp([{'formattedAddress':'Rent A','price':1700,'lastSeenDate':'2026-09-01'}])
    c=Client();data=search_nearby('Subject','abc',2.0,6,session=c)
    assert len(c.paths)==2
    assert len(data['sale'])==1 and len(data['rent'])==1
    assert not data['sale'][0]['include']
