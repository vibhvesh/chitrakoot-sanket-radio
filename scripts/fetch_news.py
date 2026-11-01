import json,re,html,os,urllib.request,urllib.parse,xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime,timezone,timedelta
from collections import Counter
B='https://news.google.com/rss/search?q='
Q=[('hi','चित्रकूट when:7d'),('hi','चित्रकूट कर्वी when:7d'),('hi','चित्रकूट धाम when:7d'),('hi','चित्रकूट पुलिस when:7d'),('hi','मानिकपुर चित्रकूट when:7d'),('hi','मझगवां सतना चित्रकूट when:7d'),('en','Chitrakoot when:7d'),('en','Karwi Chitrakoot when:7d')]
LOC={'hi':'&hl=hi&gl=IN&ceid=IN:hi','en':'&hl=en-IN&gl=IN&ceid=IN:en'}
OK=['jagran','amar ujala','amarujala','hindustan','livehindustan','navbharat','times of india','hindustan times','indian express','ndtv','abp','aaj tak','aajtak','zee','news18','pti','ani','patrika','bhaskar','the hindu','dd news','prasar bharati','.gov.in','etv bharat','india tv','jansatta','lalluram','free press journal','naidunia','tv9','republic','economic times','up tak','mp tak','dainik']
KEY=re.compile(r'chitrakoot|chitrakut|चित्रकूट|karwi|कर्वी|manikpur|मानिकपुर|mau\b|मऊ|rajapur|राजापुर|bargarh|बरगढ़|majhgawan|मझगवां|सतना|satna|kamadgiri|कामदगिरि|ramghat|रामघाट|pahari|पहाड़ी',re.I)
def strip(t):return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',t or ''))).strip()
out={}
for lang,q in Q:
  u=B+urllib.parse.quote(q)+LOC[lang]
  try:x=ET.fromstring(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=20).read())
  except Exception as e:print(u,e);continue
  for i in x.iter('item'):
    s=i.find('source');src=(s.text if s is not None else '') or '';surl=s.get('url','') if s is not None else ''
    if not any(k in (src+' '+surl).lower() for k in OK):continue
    t=re.sub(r'\s+-\s+[^-]+$','',i.findtext('title') or '').strip()
    if not KEY.search(t):continue
    k=re.sub(r'\W+','',t.lower())[:60]
    if not t or k in out:continue
    try:d=parsedate_to_datetime(i.findtext('pubDate')).astimezone(timezone.utc)
    except Exception:continue
    if d<datetime.now(timezone.utc)-timedelta(days=7):continue
    lg='hi' if re.search('[\u0900-\u097F]',t) else 'en'
    out[k]=dict(title=t,source=src,link=i.findtext('link'),pubDate=d.isoformat(),lang=lg)
it=sorted(out.values(),key=lambda a:a['pubDate'],reverse=True)
STOP=set('चित्रकूट chitrakoot के में की को से पर और ने का है एक हुए हुई गया गई लिए news in the of to and a for on with at by up mp news जिले जिला शुरू लाख करने बाद दिन साल रहे रही'.split())
c=Counter();ex={}
for a in it:
  for w in set(re.findall(r'[\w\u0900-\u097F]{3,}',a['title'].lower())):
    if w not in STOP and not w.isdigit():c[w]+=1;ex.setdefault(w,a)
tr=[];used=set()
for w,n in c.most_common(40):
  if n<2:break
  a=ex[w]
  if a['title'] in used:continue
  used.add(a['title']);tr.append(dict(topic=w,count=n,title=a['title'],source=a['source'],link=a['link'],pubDate=a['pubDate'],lang=a['lang']))
  if len(tr)>=8:break
if it:
  open('news.json','w').write(json.dumps(it[:80],ensure_ascii=False,indent=0))
  open('trending.json','w').write(json.dumps(tr,ensure_ascii=False,indent=0))
print(len(it),'items',len(tr),'trending')
