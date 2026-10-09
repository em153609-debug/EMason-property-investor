"""Combine new comp candidates without losing edits or duplicating addresses."""

def merge_comp_rows(existing, incoming):
    seen=set()
    out=[]
    for row in list(existing or [])+list(incoming or []):
        addr=str(row.get('address') or '').strip().casefold()
        if not addr or addr in seen:
            continue
        seen.add(addr)
        out.append(dict(row))
    return out
