import json,re,html,glob,sys,collections
FR={'½':.5,'¼':.25,'¾':.75,'⅛':.125,'⅜':.375,'⅝':.625,'⅞':.875,'⅓':1/3,'⅔':2/3}
def num(s):
    s=s.strip().replace('"','').replace('”','')
    m=re.fullmatch(r'(\d+(?:\.\d+)?)\s*([½¼¾⅛⅜⅝⅞⅓⅔])?|(\d+)\s+(\d+)/(\d+)',s)
    if not m: return None
    if m.group(3): return int(m.group(3))+int(m.group(4))/int(m.group(5))
    return float(m.group(1))+FR.get(m.group(2) or '',0)
SIZE=re.compile(r'^(XXS|XS|S|M|L|XL|XXL|2XL|XXXL|3XL|4XL|[0-9]{1,2})$',re.I)
def parse(b):
    out=[]
    for tb in re.findall(r'(?s)<table.*?</table>',b):
        rows=[[html.unescape(re.sub('<[^>]+>','',c)).strip() for c in re.findall(r'(?s)<t[dh][^>]*>(.*?)</t[dh]>',r)] for r in re.findall(r'(?s)<tr.*?</tr>',tb)]
        rows=[r for r in rows if r]
        if len(rows)<2: continue
        hdr=[h.upper() for h in rows[0]]
        sizes={}
        # orientation A: sizes down first column
        if any(SIZE.match(r[0]) for r in rows[1:]) and any(re.search('CHEST|WIDTH|PIT',h) for h in hdr):
            ci=next(i for i,h in enumerate(hdr) if re.search('CHEST|WIDTH|PIT',h))
            li=next((i for i,h in enumerate(hdr) if 'LENGTH' in h and 'SLEEVE' not in h),None)
            for r in rows[1:]:
                if SIZE.match(r[0]) and len(r)>ci:
                    c=num(r[ci]); l=num(r[li]) if li is not None and len(r)>li else None
                    if c: sizes[r[0].upper()]=(c,l)
        # orientation B: sizes across header
        elif sum(bool(SIZE.match(h)) for h in hdr)>=3:
            idx=[i for i,h in enumerate(hdr) if SIZE.match(h)]
            cr=next((r for r in rows[1:] if re.search('(?i)chest|width|pit',r[0])),None)
            lr=next((r for r in rows[1:] if re.search('(?i)length',r[0]) and not re.search('(?i)sleeve|inseam',r[0])),None)
            if cr:
                for i in idx:
                    c=num(cr[i]) if i<len(cr) else None
                    l=num(lr[i]) if lr and i<len(lr) else None
                    if c: sizes[hdr[i]]=(c,l)
        if sizes: out.append((hdr,sizes))
    return out
res=[]
for f in sorted(glob.glob(sys.argv[1]+'/*.json')):
    brand=f.split('/')[-1].rsplit('_',1)[0]
    for p in json.load(open(f))['products']:
        b=p.get('body_html') or ''
        t=html.unescape(re.sub(r'\s+',' ',re.sub('<[^>]+>',' ',b)))
        for hdr,s in parse(b):
            unit='cm' if re.search(r'(?i)centimet|\bcm\b',t) or max(v[0] for v in s.values())>40 else 'in'
            fit=re.search(r'(?i)[^.|]*(runs (small|large|big|true)|true to size|size (up|down)|oversized|boxy|relaxed fit|regular fit|slim fit|cropped)[^.|]*',t)
            res.append(dict(brand=brand,title=p['title'],type=p['product_type'],handle=p['handle'],unit=unit,sizes=s,fit=fit.group(0).strip() if fit else None,published=p.get('published_at','')[:10]))
json.dump(res,open(sys.argv[2],'w'),indent=1)
c=collections.Counter((r['brand'],r['type']) for r in res)
print(len(res)); [print(k,v) for k,v in sorted(c.items())]
