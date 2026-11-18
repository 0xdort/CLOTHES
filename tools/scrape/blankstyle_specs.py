import re,subprocess,sys,json,urllib.request,os
from fractions import Fraction
os.makedirs('pdf',exist_ok=True)
UA={'User-Agent':'Mozilla/5.0'}
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40).read()
def num(tok):
    tok=tok.strip()
    try:
        parts=tok.split()
        return float(sum(Fraction(p) for p in parts))
    except Exception: return None
SZ=['XS','S','M','L','XL','2XL','3XL','4XL','5XL']
out={}
for h in sys.argv[1:]:
    try:
        page=get('https://www.blankstyle.com/'+h).decode('utf8','ignore')
        m=re.search(r'/files/specs/\d+/SpecSheetMeasurements_[^"\']+\.pdf',page)
        if not m: print('NOSPEC',h); continue
        pdfp='pdf/'+h+'.pdf'; open(pdfp,'wb').write(get('https://www.blankstyle.com'+m.group(0)))
        txt=subprocess.run(['pdftotext','-layout',pdfp,'-'],capture_output=True,text=True).stdout
        i=txt.find('PRODUCT MEAS'); block=txt[i:i+3000]
        lines=block.split('\n')
        hdr=next(l for l in lines if re.search(r'\bM\b',l) and re.search(r'\bL\b',l))
        sizes=re.findall(r'\b(?:XS|S|M|L|XL|[2-5]XL|[2-5]X)\b',hdr)
        cols=[hdr.find(' '+s+' ') if hdr.find(' '+s+' ')>=0 else hdr.rfind(s) for s in sizes]
        def row(label):
            for j,l in enumerate(lines):
                if re.match(r'\s*'+label,l,re.I):
                    # value line: the label line, or the next line holding numbers
                    for l2 in lines[j:j+3]:
                        vals=re.findall(r'\d+(?: \d+/\d+)?(?:\.\d+)?',l2)
                        if len(vals)>=len(sizes)-1: return [num(v) for v in vals]
            return None
        title=re.search(r'MEASUREMENTS\s*\n(?:.*\n){0,3}?\s*(\S.*?\.\s*[A-Z0-9-]+)\s*\n',txt)
        L=row('Body') ; C=row('Chest')
        out[h]=dict(title=title.group(1).strip() if title else h,spec='https://www.blankstyle.com'+m.group(0),sizes=sizes,length=L,chest=C,
                    fit=[x for x in ['Relaxed fit','Classic fit','Oversized','Boxy','Original fit','Loose fit','Regular fit','Slim fit'] if x.lower() in txt.lower()])
        print('OK',h,sizes,'L',L,'C',C,out[h]['fit'])
    except Exception as e: print('ERR',h,e)
json.dump(out,open('crawl.json','w'),indent=1)
