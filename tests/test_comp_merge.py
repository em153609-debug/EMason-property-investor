from services.comp_merge import merge_comp_rows

def test_new_comp_candidates_import():
    rows=merge_comp_rows([], [{'address':'A St','include':False},{'address':'B St','include':False}])
    assert len(rows)==2 and not rows[0]['include']

def test_existing_comp_edits_preserved_and_no_duplicates():
    rows=merge_comp_rows([{'address':'A St','include':True,'renovated':True}], [{'address':'a st','include':False},{'address':'B St','include':False}])
    assert len(rows)==2 and rows[0]['include'] and rows[0]['renovated']
