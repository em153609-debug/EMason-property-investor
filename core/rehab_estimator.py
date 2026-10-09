"""Editable scope-of-work pricing. Sample rate templates are NOT local quotes."""
from math import isfinite

def template():
    # ZERO quantities prevent an example from silently becoming an underwriting number.
    # Users must customize material/labor rates and quantities from their own bids.
    return [
        dict(scope='Kitchen',item='Kitchen refresh',unit='project',quantity=0.0,materials_per_unit=6500.0,contractor_labor_per_unit=5500.0,diy_labor_hours_per_unit=80.0,method='Contractor'),
        dict(scope='Bathrooms',item='Bathroom refresh',unit='bathroom',quantity=0.0,materials_per_unit=3400.0,contractor_labor_per_unit=4100.0,diy_labor_hours_per_unit=60.0,method='Contractor'),
        dict(scope='Flooring',item='Flooring replacement',unit='sq ft',quantity=0.0,materials_per_unit=2.75,contractor_labor_per_unit=2.50,diy_labor_hours_per_unit=0.09,method='Contractor'),
        dict(scope='Painting',item='Interior painting',unit='sq ft',quantity=0.0,materials_per_unit=0.65,contractor_labor_per_unit=1.60,diy_labor_hours_per_unit=0.06,method='DIY'),
        dict(scope='Exterior',item='Roof replacement',unit='sq ft',quantity=0.0,materials_per_unit=3.75,contractor_labor_per_unit=3.25,diy_labor_hours_per_unit=0.0,method='Contractor'),
        dict(scope='Systems',item='HVAC allowance',unit='system',quantity=0.0,materials_per_unit=4200.0,contractor_labor_per_unit=2800.0,diy_labor_hours_per_unit=0.0,method='Contractor'),
        dict(scope='Systems',item='Electrical / plumbing allowance',unit='project',quantity=0.0,materials_per_unit=2500.0,contractor_labor_per_unit=4500.0,diy_labor_hours_per_unit=0.0,method='Contractor'),
        dict(scope='Other',item='Other / miscellaneous',unit='project',quantity=0.0,materials_per_unit=1000.0,contractor_labor_per_unit=1000.0,diy_labor_hours_per_unit=12.0,method='Contractor')]

def _number(v, name):
    try: x=float(v)
    except (TypeError,ValueError): raise ValueError(f'{name} must be numeric')
    if not isfinite(x) or x<0: raise ValueError(f'{name} must be finite and nonnegative')
    return x

def estimate_scope(rows, diy_hourly_value=25.0, labor_overrun=0.0):
    """Cash cost includes materials + outsourced labor; DIY hours are opportunity cost ONLY."""
    hourly=_number(diy_hourly_value,'DIY hourly value')
    bump=_number(labor_overrun,'labor overrun')
    if bump>2: raise ValueError('Labor overrun must be <=200%')
    details=[]
    for row in rows:
        qty=_number(row.get('quantity',0),'Quantity')
        material=qty*_number(row.get('materials_per_unit',0),'Materials rate')
        professional=qty*_number(row.get('contractor_labor_per_unit',0),'Contractor labor rate')*(1+bump)
        hours=qty*_number(row.get('diy_labor_hours_per_unit',0),'DIY hours')
        method=str(row.get('method') or 'Contractor')
        if method not in ('DIY','Contractor'):
            raise ValueError('Method must be DIY or Contractor')
        cash=material+(professional if method=='Contractor' else 0)
        details.append({'item':str(row.get('item') or 'Untitled'), 'scope':str(row.get('scope') or 'Other'),
            'cash':cash,'materials':material,'contractor_labor':professional if method=='Contractor' else 0,
            'diy_hours':hours if method=='DIY' else 0})
    cash_total=sum(d['cash'] for d in details)
    hours_total=sum(d['diy_hours'] for d in details)
    return {'cash_total':cash_total,'diy_hours':hours_total,
        'diy_time_value':hours_total*hourly,'economic_cost':cash_total+hours_total*hourly,
        'items':details}
