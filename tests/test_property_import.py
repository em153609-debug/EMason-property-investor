from core.engine import Deal
from core.property_import import import_property_results,apply_new_subject,infer_kind,money


def sample():
    return {'property':[{'propertyType':'Single Family','lastSalePrice':180000,'squareFootage':1700}], 'value':{'price':300000},'rent':{'rent':2200}}

def test_past_sale_is_not_asking_price():
    a=import_property_results(sample())
    assert a.asking_price is None
    assert a.value_estimate==300000
    assert a.rent_estimate==2200

def test_new_address_resets_property_numbers_but_not_financing():
    d=Deal(price=150000,arv=240000,rent=2100,arv_confidence='Verified comps', rent_confidence='Verified comps')
    d.refi_ltv=.7
    apply_new_subject(d,import_property_results(sample()))
    assert d.price==0 and d.arv==0 and d.rent==2200
    assert d.rent_confidence=='Unverified' and d.arv_confidence=='Unverified'
    assert d.refi_ltv==.7

def test_explicit_asking_price_import():
    s=sample();s['property'][0]['listingPrice']=215000
    d=Deal()
    apply_new_subject(d,import_property_results(s))
    assert d.price==215000 and d.arv==0

def test_missing_estimates_do_not_fabricate():
    p=import_property_results({'property':[{'propertyType':'Residential'}]})
    assert p.asking_price is None and p.rent_estimate is None and p.value_estimate is None
    assert p.property_type is None

def test_duplex_detection():
    assert infer_kind({'propertyType':'Duplex'})=='Duplex'
    assert infer_kind({'units':3})=='Triplex'
    assert infer_kind({'propertyType':'fourplex'})=='Fourplex'

def test_reject_invalid_money():
    assert money(None) is None and money(-1) is None and money(True) is None

def test_missing_property_record():
    assert import_property_results({}).property_type is None
