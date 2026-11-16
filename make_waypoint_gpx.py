import re,math,bisect,sys
from xml.sax.saxutils import escape
src,out=sys.argv[1],sys.argv[2]
s=open(src).read()
raw=re.findall(r'<trkpt lat="([^"]+)" lon="([^"]+)">\s*<ele>([^<]+)</ele>\s*<time>([^<]+)</time>',s)
pts=[(float(a),float(b),float(e)) for a,b,e,_ in raw]
def hav(p,q):
    R=6371000;la1,lo1,la2,lo2=map(math.radians,(p[0],p[1],q[0],q[1]))
    a=math.sin((la2-la1)/2)**2+math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*R*math.asin(math.sqrt(a))
d=[0]
for i in range(1,len(pts)): d.append(d[-1]+hav(pts[i-1],pts[i]))
def at(m): return max(0,min(bisect.bisect_left(d,m),len(d)-1))
def brg(p,q):
    la1,lo1,la2,lo2=map(math.radians,(p[0],p[1],q[0],q[1]))
    y=math.sin(lo2-lo1)*math.cos(la2);x=math.cos(la1)*math.sin(la2)-math.sin(la1)*math.cos(la2)*math.cos(lo2-lo1)
    return (math.degrees(math.atan2(y,x))+360)%360
COMP=['N','NE','E','SE','S','SW','W','NW']
def comp(b): return COMP[int((b+22.5)//45)%8]
def rel(a): return (a+540)%360-180   # -180..180, + = right

def junction(i,j,w=120):
    """i = this pass's index at junction, j = index on the other pass at the same spot.
    Returns cue text based on the branch taken vs the branch not taken."""
    node=pts[i]
    inc=brg(pts[at(d[i]-w)],node)                 # direction of travel arriving
    out=brg(node,pts[at(d[i]+w)])
    cands=[brg(node,pts[at(d[j]-w)]),brg(node,pts[at(d[j]+w)])]
    # the other pass's two arms: one coincides with our in or out arm; the other is the branch not taken
    def diff(a,b): return abs(rel(a-b))
    other=max(cands,key=lambda c:min(diff(c,(inc+180)%360),diff(c,out)))
    t_out=rel(out-inc); t_oth=rel(other-inc)
    side='RIGHT' if t_out>t_oth else 'LEFT'
    if abs(t_out)<35: verb=f'continue straight (bear {side.lower()})'
    else: verb=f'turn {side}'
    return side,f'{verb}, heading {comp(out)} ({out:.0f}°); other branch goes {comp(other)}'

def ele_gain(a,b):
    u=dn=0
    for k in range(a+1,b+1):
        x=pts[k][2]-pts[k-1][2]; u+=max(x,0); dn+=min(x,0)
    return u,dn

# idx: anchor index into the GPX track; tbl: (km, ele, cut) from distancetable.txt
Z=lambda km:at(km*1000)
i_summit=max(range(len(pts)),key=lambda k:pts[k][2])
i_wujie=min(range(Z(84),Z(89)),key=lambda k:pts[k][2])
i_trail=min(range(Z(52.5),Z(56)),key=lambda k:pts[k][2])
WP=[ # name, idx, table km, table ele, sym, type, note, (junction pair idx or None)
 ('START',0,0.0,530,'Flag, Green','Generic','Start 04:00. Out on shared trunk.',None),
 ('J1 Fork',Z(3.54),None,None,None,None,'Fork: return route rejoins here at km ~99.3.',Z(99.32)),
 ('X out',Z(10.49),10.5,1640,None,None,'Junction X (1st pass) – start of out-and-back to cpA / turn point.',Z(25.45)),
 ('cpA-1',Z(13.40),13.4,1520,'Food','Food','Aid station cpA (outbound). CUTOFF 08:15 or DNF.',None),
 ('TURN',Z(18.10),18.1,1535,'U-Turn','U-Turn','Turn point ↶ U-TURN, return the same way to cpA.',None),
 ('cpA-2',Z(22.70),22.8,1520,'Food','Food','Aid station cpA (return). CUTOFF 10:15 or DNF.',None),
 ('X ret',Z(25.45),25.6,1640,None,None,'Junction X (2nd pass) – leave out-and-back, new trail toward Y.',Z(10.49)),
 ('Y out',Z(31.55),31.9,1550,None,None,'Junction Y (1st pass). Y–cpB shared with km 89–91.',Z(91.34)),
 ('cpB-1',Z(34.09),34.2,1310,'Food','Food','Aid station cpB (1st). CUTOFF 14:00 or DNF.',Z(88.81)),
 ('Z out',Z(39.50),40.0,1470,None,None,'Junction Z (1st pass). Z–W shared with km 71–76.',Z(76.19)),
 ('W/cpC',Z(44.44),44.6,1410,None,None,'W – intersection near cpC (104K does NOT detour to cpC1). 14:00(14:30) 104→75K; 16:00 104K/75K→DNF.',Z(71.31)),
 ('cpD Bag',Z(49.78),50.0,710,'Food','Food','cpD Zhong Zheng – DROP BAG. CUTOFF 15:30 (must leave before) or DNF.',None),
 ('TrailHead',i_trail,54.3,645,'Trail Head','Generic','Trail entry – start of big climb to Dajianshan (+1420 m in 7.2 km).',None),
 ('Dajianshan',i_summit,61.5,2017,'Summit','Summit','大尖山 2017 m – high point of course.',None),
 ('cpC2',Z(71.31),71.8,1410,'Food','Food','Aid station cpC2 at W intersection. CUTOFF 22:00 104K→DNF.',Z(44.44)),
 ('Z ret',Z(76.19),76.6,1470,None,None,'Junction Z (2nd pass) – leave shared section, new trail toward Wujie.',Z(39.50)),
 ('Wujie',i_wujie,86.4,760,'Valley','Valley','Wujie (武界) – low point, then +550 m climb to cpB2.',None),
 ('cpB-2',Z(88.81),89.6,1310,'Food','Food','Aid station cpB2. CUTOFF 04:00 104K→DNF.',Z(34.09)),
 ('Y ret',Z(91.34),91.9,1550,None,None,'Junction Y (2nd pass) – leave shared section, final descent.',Z(31.55)),
 ('J1 Merge',Z(99.32),None,None,None,None,'Rejoin start trunk – same road as the first 3.5 km.',Z(3.54)),
 ('FINISH',len(pts)-1,103.5,530,'Flag, Checkered','Generic','Finish. Cutoff 08:00 (28 h).',None),
]
WP.sort(key=lambda w:w[1])
wpts=[];rows=[]
for n,(name,i,km,tele,sym,typ,note,pair) in enumerate(WP):
    desc=[note]
    if pair is not None:
        side,cue=junction(i,pair)
        desc.append('DIRECTION: '+cue+'.')
        if sym is None: sym=typ=('Right' if side=='RIGHT' else 'Left')
    elif n<len(WP)-1:
        nb=brg(pts[i],pts[at(d[i]+150)]);desc.append(f'Leave heading {comp(nb)} ({nb:.0f}°).')
    if n<len(WP)-1:
        nx=WP[n+1];u,dn=ele_gain(i,nx[1])
        desc.append(f'NEXT: {nx[0]} in {(d[nx[1]]-d[i])/1000:.1f} km, +{u:.0f}/{dn:.0f} m.')
    kmtxt=f'{km:.1f} km (official)' if km is not None else ''
    desc.insert(0,f'{kmtxt}{" / " if kmtxt else ""}{d[i]/1000:.1f} km on GPX, {pts[i][2]:.0f} m.')
    label=f'{name} {km:.1f}' if km is not None else name
    wpts.append((pts[i],label,' '.join(desc),sym,typ))
    rows.append((label,d[i]/1000,km,pts[i][2],tele,sym))

o=['<?xml version="1.0" encoding="UTF-8"?>',
'<gpx version="1.1" creator="ft104gpx regen (from GpsPrune export + official distance table)" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">',
' <metadata><name>Formosa Trail 2025 - 104km (waypoints)</name><desc>Official FT104 track + checkpoints, cutoffs and junction direction cues.</desc></metadata>']
for p,label,desc,sym,typ in wpts:
    o.append(f' <wpt lat="{p[0]}" lon="{p[1]}"><ele>{p[2]:.0f}</ele><name>{escape(label)}</name><cmt>{escape(desc)}</cmt><desc>{escape(desc)}</desc><sym>{escape(sym)}</sym><type>{escape(typ)}</type></wpt>')
o.append(' <trk><name>Formosa Trail 2025 - 104km</name><trkseg>')
for (a,b,e,t) in raw: o.append(f'  <trkpt lat="{a}" lon="{b}"><ele>{e}</ele><time>{t}</time></trkpt>')
o.append(' </trkseg></trk>\n</gpx>')
open(out,'w').write('\n'.join(o))
print(f"{'name':18}{'gpx km':>8}{'tbl km':>8}{'gpx m':>7}{'tbl m':>7}  sym")
for r in rows: print(f"{r[0]:18}{r[1]:8.2f}{(r[2] if r[2] is not None else float('nan')):8.1f}{r[3]:7.0f}{(r[4] or 0):7}  {r[5]}")
for p,label,desc,sym,typ in wpts: print('-',label,'|',desc)
