"""Check public image CDN URLs used by Spin's own frontend before building.

Usage: python scripts/resolve_media.py work/spin-HANDLE
Preserves source S3 URLs; the builder uses verified CDN URLs for display.
"""
import concurrent.futures,json,pathlib,sys,urllib.request
folder=pathlib.Path(sys.argv[1]);raw=json.loads((folder/'all.json').read_text(encoding='utf8'))
urls=list(dict.fromkeys(u for m in raw['replyInfo'] for r in m.get('reply',[]) for u in r.get('imageList',[])))
def check(url):
 cdn=url.replace('https://catcher-test2.s3.ap-northeast-2.amazonaws.com/','https://d320v6c020sgby.cloudfront.net/').replace('https://spinspin-media.s3.ap-northeast-2.amazonaws.com/','https://media.spin-spin.com/')
 result={'url':url,'cdn':cdn}
 try:
  with urllib.request.urlopen(urllib.request.Request(cdn,method='HEAD'),timeout=30) as response:
   result.update(status=response.status,type=response.headers.get('Content-Type'))
 except Exception as error:result['error']=str(error)
 return result
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:result=list(pool.map(check,urls))
(folder/'image-cdn-status.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'images':len(result),'accessible':sum(x.get('status')==200 for x in result)}))
