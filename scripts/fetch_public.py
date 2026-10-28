import pathlib,json,re,urllib.request,time,sys,datetime
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parent.parent
handle=sys.argv[1];folder=ROOT/'work'/('spin-'+handle);folder.mkdir(exist_ok=True)
def read(url):
 for attempt in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=90) as r:return r.read().decode('utf8')
  except Exception:
   if attempt==3:raise
   time.sleep(2**attempt)
class NextData(HTMLParser):
 def __init__(self):super().__init__();self.active=False;self.text=''
 def handle_starttag(self,t,a):
  if t=='script' and dict(a).get('id')=='__NEXT_DATA__':self.active=True
 def handle_endtag(self,t):
  if t=='script':self.active=False
 def handle_data(self,s):
  if self.active:self.text+=s
page=read('https://spin-spin.com/'+handle+'?tab=1');(folder/'page.html').write_text(page,encoding='utf8');parser=NextData();parser.feed(page)
profile=json.loads(parser.text)['props']['pageProps']['boxData'];(folder/'profile.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2),encoding='utf8');box=profile['id']
counter=json.loads(read(f'https://web-api.spin-spin.com/api/requestbox/replyCounter?id={box}'));print(json.dumps({'handle':handle,'profile':profile,'counter':counter},ensure_ascii=True),flush=True)
(folder/'counter.json').write_text(json.dumps(counter),encoding='utf8');items={};pages=[];offset=0
while True:
 d=json.loads(read(f'https://web-api.spin-spin.com/api/requestbox/getRepliedLetters?boxId={box}&page={offset}&limit=100&filterType=all'))
 (folder/f'page-{offset}.json').write_text(json.dumps(d,ensure_ascii=False),encoding='utf8');rows=d.get('replyInfo',[])
 for row in rows:items[row['id']]=row
 pages.append({'page':offset,'count':len(rows),'isLast':d.get('isLast'),'next':d.get('next')});print(json.dumps({'page':offset,'count':len(rows),'unique':len(items),'isLast':d.get('isLast'),'next':d.get('next')}),flush=True)
 if not rows:break
 offset+=1
 time.sleep(.15)
payload={'profile':profile,'counter':counter,'pages':pages,'replyInfo':list(items.values()),'capturedAt':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()}
(folder/'all.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'done':True,'count':len(items),'expected':counter.get('replyCount')}),flush=True)
