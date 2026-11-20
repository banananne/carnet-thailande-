import json, pdfplumber, sys
PDF="/mnt/user-data/uploads/Journal_de_bord.pdf"
pdf=pdfplumber.open(PDF)
raw=json.load(open("days_raw.json"))

def bullets(p):
    return sorted({round((c["top"]+c["bottom"])/2) for c in p.curves if 280<c["x0"]<340 and (c["x1"]-c["x0"])<10 and 4<(c["bottom"]-c["top"])<10})

def build(n):
    p=pdf.pages[n-1]
    bl=bullets(p)
    tl=raw[str(n)]["timeline"]
    # paragraphes : coupure si écart de lignes > 15 pt
    paras=[]; cur=[]
    for l in tl:
        if cur and l["top"]-cur[-1]["top"]>15:
            paras.append(cur); cur=[]
        cur.append(l)
    if cur: paras.append(cur)
    blocks={b:[] for b in bl}
    for para in paras:
        c=(para[0]["top"]+para[-1]["top"]+9)/2
        b=min(bl,key=lambda y:abs(y-c))
        # lignes : jointure si ligne pleine (x1>=450)
        ents=[]
        for i,l in enumerate(para):
            if ents and para[i-1]["x1"]>=450:
                ents[-1]+=" "+l["text"]
            else:
                ents.append(l["text"])
        blocks[b].append(ents)
    return [{"y":b,"paras":blocks[b]} for b in bl]

if __name__=="__main__":
    a=int(sys.argv[1]); b=int(sys.argv[2])
    for n in range(a,b+1):
        print("=== PAGE",n, raw[str(n)]["heads"])
        for bk in build(n):
            print(" •",bk["y"])
            for para in bk["paras"]:
                print("     ¶", " | ".join(para))
