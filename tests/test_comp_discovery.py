from services.comp_discovery import normalize_avm_candidates, candidate_summary


def test_sales_import_unverified_and_unselected():
    data = {'comparables':[{'formattedAddress':'101 Main St','price':220000,'squareFootage':1400,
                            'bedrooms':3,'lastSeenDate':'2026-09-01T00:00:00Z','status':'Inactive'}]}
    rows=normalize_avm_candidates(data,'sale','999 Elsewhere St')
    assert len(rows)==1
    assert rows[0]['amount']==220000
    assert rows[0]['include'] is False
    assert rows[0]['renovated'] is False
    assert rows[0]['date']=='2026-09-01'
    assert 'not verified' in candidate_summary(rows,'sale')['notes']


def test_rent_skips_bad_and_subject_duplicates():
    data={'comparables':[{'formattedAddress':'Me St','price':1500},
                         {'formattedAddress':'Neighbor St','price':2100},
                         {'formattedAddress':'Neighbor St','price':2100},
                         {'formattedAddress':'Bad St','price':None}]}
    rows=normalize_avm_candidates(data,'rent','Me St')
    assert len(rows)==1 and rows[0]['amount']==2100
    assert rows[0]['include'] is False


def test_blank_and_wrong_type():
    assert normalize_avm_candidates(None,'rent')==[]
    try:
        normalize_avm_candidates({},'commercial')
        assert False
    except ValueError:
        pass
