"""Self-contained Excel XLSX exporter; no extra spreadsheet package required on hosting."""
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from xml.sax.saxutils import escape


def _cell(row, col, value):
    letters=''; col+=1
    while col:
        col,rem=divmod(col-1,26);letters=chr(65+rem)+letters
    ref=f'{letters}{row}'
    if isinstance(value,(int,float)) and not isinstance(value,bool):
        return f'<c r="{ref}"><v>{value}</v></c>'
    return f'<c r="{ref}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'


def _sheet(rows):
    xml=['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
         '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>']
    for i,values in enumerate(rows,1):
        xml.append(f'<row r="{i}">'+''.join(_cell(i,j,v) for j,v in enumerate(values))+'</row>')
    xml.append('</sheetData></worksheet>')
    return ''.join(xml)


def excel_report(deal,result):
    rows1=[['DEAL INPUT','VALUE']]+[[k,v] for k,v in vars(deal).items()]
    r=result
    rows2=[['METRIC','VALUE'],['BRRRR score',r['brrrr']['score']],['BRRRR verdict',r['brrrr']['verdict']],['Monthly cash flow',r['brrrr']['monthly_cashflow']],['DSCR',r['brrrr']['dscr']],['Capital recovered',r['brrrr']['recovery']],['Cash remaining',r['brrrr']['cash_left']],['Refinance loan',r['brrrr']['refi_loan']],['Flip score',r['flip']['score']],['Flip verdict',r['flip']['verdict']],['Flip profit',r['flip']['profit']],['Flip ROI',r['flip']['roi']],['Break-even sale price',r['flip']['break_even_sale']],['Cash invested',r['shared']['cash_required']],['All-in cost',r['shared']['all_in']]]
    rows3=[['STRATEGY','CATEGORY','SCORE','MAX','STATUS','EXPLANATION','ACTION']]
    for strategy in ['brrrr','flip']:
        rows3 += [[strategy.upper(),p['name'],p['score'],p['max'],p['status'],p['why'],p['action']] for p in result[strategy]['items']]
    data=[('Deal Inputs',rows1),('Investment Results',rows2),('Score Explanations',rows3)]
    ctype='application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml'
    types=['<?xml version="1.0" encoding="UTF-8"?>','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
           '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
           '<Default Extension="xml" ContentType="application/xml"/>',
           '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>']
    types += [f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="{ctype}"/>' for i in range(1,4)]
    types.append('</Types>')
    sheets=''.join(f'<sheet name="{escape(n)}" sheetId="{i}" r:id="rId{i}"/>' for i,(n,_) in enumerate(data,1))
    wb=f'<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>{sheets}</sheets></workbook>'
    rels=''.join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1,4))
    top_rels='<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'
    io=BytesIO()
    with ZipFile(io,'w',ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml',''.join(types))
        z.writestr('_rels/.rels',top_rels)
        z.writestr('xl/workbook.xml',wb)
        z.writestr('xl/_rels/workbook.xml.rels',f'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{rels}</Relationships>')
        for i,(_,rows) in enumerate(data,1): z.writestr(f'xl/worksheets/sheet{i}.xml',_sheet(rows))
    return io.getvalue()
