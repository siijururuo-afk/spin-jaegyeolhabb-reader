"""Merge one translated public Spin capture while preserving existing accounts.

Usage: python scripts/add_account.py HANDLE --capture-dir /path/to/work/spin-HANDLE
Each translations-*.json maps public question ID to {q, a} Chinese text.
"""
import pathlib,json,datetime,html,re,sys,argparse,zipfile
ROOT=pathlib.Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser();parser.add_argument('handle');parser.add_argument('--capture-dir',type=pathlib.Path);parser.add_argument('--preview',action='store_true');args=parser.parse_args()
if not re.fullmatch(r'[A-Za-z0-9_-]+',args.handle):raise ValueError('Invalid handle')
folder=args.capture_dir or ROOT/'work'/('spin-'+args.handle)
raw=json.loads((folder/'all.json').read_text(encoding='utf8'));trs={}
for f in sorted(folder.glob('translations-*.json')):trs.update(json.loads(f.read_text(encoding='utf-8-sig')))
valid=[m for m in raw['replyInfo'] if m.get('reply')]
if len({m['id'] for m in valid})!=len(valid):
 raise RuntimeError('Duplicate answered IDs; audit pagination before publishing')
if len(valid)!=raw['counter']['replyCount'] and not args.preview:
 raise RuntimeError('Public counter mismatch; refresh count and audit pagination before publishing')
missing=[m['id'] for m in valid if m['id'] not in trs]
if missing and not args.preview:raise RuntimeError(f'{len(missing)} missing translations')
def clean(s):return html.unescape(re.sub('<[^>]*>','',re.sub(r'<br\s*/?>','\n',s or '',flags=re.I)))
tz=datetime.timezone(datetime.timedelta(hours=9));items=[]
for m in valid:
 if len(m['reply'])!=1:raise RuntimeError('Multiple replies need explicit handling: '+m['id'])
 r=m['reply'][0]
 if r.get('isSubscriberOnly'):raise RuntimeError('Subscriber-only content must not be exported')
 tr=trs.get(m['id'],{});q=clean(m.get('text'));a=clean(r.get('text'));qzh=tr.get('q','[翻译整理中]') if q else '';azh=tr.get('a','[翻译整理中]') if a else ''
 if not args.preview and ((q and not qzh.strip()) or (a and not azh.strip()) or '[翻译整理中]' in qzh+azh):
  raise RuntimeError('Incomplete translation: '+m['id'])
 if tr.get('reviewReason')=='minor_age':q=a=qzh=azh='[涉及未成年性描写，略去具体内容]'
 dt=datetime.datetime.fromisoformat(r['createdAt'].replace('Z','+00:00')).astimezone(tz)
 items.append({'id':m['id'],'seq':len(items)+1,'question':q,'answer':a,'questionZh':qzh,'answerZh':azh,'createdAt':r['createdAt'],'date':dt.strftime('%Y.%m.%d %H:%M'),'images':[{'url':u,'local':None} for u in r.get('imageList',[])]})
profile=raw['profile'];handle=profile['handle'];captured=raw.get('capturedAt','2026-10-28')[:10]
new={'handle':handle,'name':profile['nickname'],'bio':profile.get('bio') or '','profileImage':profile.get('profileImg') or '','source':'https://spin-spin.com/'+handle+'?tab=1','capturedAt':captured,'timezone':'Asia/Seoul','count':len(items),'items':items}
archives={};archive_dir=ROOT/'archives';archive_dir.mkdir(exist_ok=True)
for p in sorted(archive_dir.glob('*.json')):
 d=json.loads(p.read_text(encoding='utf8'));archives[d['handle']]=d
archives[handle]=new
(archive_dir/f'{handle}.json').write_text(json.dumps(new,ensure_ascii=False,indent=2),encoding='utf8')
md=[f'# {new["name"]} · @{handle}\n\n主页：{new["source"]}\n\n抓取：{captured} · {len(items)} 条公开问答 · 韩国时间UTC+9\n\n']
for m in items:
 md.append(f'## {m["seq"]:04} · {m["date"]}\n\n**提问（中文）**\n\n{m["questionZh"]}\n\n**回答（中文）**\n\n{m["answerZh"]}\n\n**提问（韩文）**\n\n{m["question"]}\n\n**回答（韩文）**\n\n{m["answer"]}\n\n')
 for im in m['images']:md.append(f'![图片回答]({im["url"]})\n\n')
(archive_dir/f'{handle}.md').write_text(''.join(md),encoding='utf-8-sig')
(ROOT/'accounts.js').write_text('window.SPIN_ARCHIVES = '+json.dumps(archives,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf8')
registry=json.loads((ROOT/'sources.json').read_text(encoding='utf8'));sources=registry['sources'];entry={'platform':'spin-spin','handle':handle,'name':new['name'],'homepage':'https://spin-spin.com/'+handle,'answersPage':new['source'],'publicBoxId':profile['id'],'capturedAt':captured,'publicAnswerCount':raw['counter']['replyCount'],'translatedAnswerCount':len(valid)-len(missing),'archiveJson':f'archives/{handle}.json','archiveMarkdown':f'archives/{handle}.md'}
registry['sources']=[s for s in sources if s['handle']!=handle]+[entry];(ROOT/'sources.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2),encoding='utf8')
report={'handle':handle,'publicCount':raw['counter']['replyCount'],'capturedRows':len(raw['replyInfo']),'capturedAnswered':len(valid),'omittedEmptyReplies':[m['id'] for m in raw['replyInfo'] if not m.get('reply')],'redactedItems':[{'id':m['id'],'reason':trs[m['id']]['reviewReason']} for m in valid if trs.get(m['id'],{}).get('reviewReason')],'uniqueAnswered':len({m['id'] for m in valid}),'pages':raw['pages'],'oldest':min((m['date'] for m in items),default=None),'newest':max((m['date'] for m in items),default=None),'nextPageEmpty':not raw['pages'][-1]['count'],'translationCount':len(valid)-len(missing),'missingTranslations':len(missing)}
(ROOT/f'capture-report-{handle}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
if not missing:
 with zipfile.ZipFile(ROOT.parent/'Spin提问箱合集_网站.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in ROOT.rglob('*'):
   if p.is_file() and 'work' not in p.relative_to(ROOT).parts and '__pycache__' not in p.parts:z.write(p,p.relative_to(ROOT))
print(json.dumps({'accounts':len(archives),'total':sum(d['count'] for d in archives.values()),'newAnswered':len(items),'missing':len(missing)},ensure_ascii=False))
