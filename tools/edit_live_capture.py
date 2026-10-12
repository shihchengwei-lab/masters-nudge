"""Edit saved screen recordings only; no Actor or Provider invocation.
Usage: python tools/edit_live_capture.py RECORDING_ROOT
Requires ffmpeg and Windows Microsoft JhengHei.
"""
import sys
from pathlib import Path
import json,subprocess,datetime,re,shutil,hashlib
if len(sys.argv)!=2: raise SystemExit('Usage: python tools/edit_live_capture.py RECORDING_ROOT')
ROOT=Path(sys.argv[1]).resolve()
OUT=ROOT/'edited';OUT.mkdir(exist_ok=True)
shutil.copyfile('C:/Windows/Fonts/msjh.ttc',OUT/'font.ttc')
def run(args):
 p=subprocess.run(args,cwd=OUT,capture_output=True)
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-2500:])
 return p.stdout

def epoch(timestamp):return datetime.datetime.fromisoformat(timestamp.replace('Z','+00:00')).timestamp()
def duration(path):return float(run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(path)]))
def material(arm):
 root=ROOT/arm;video=root/'raw-screen.mkv'
 events=[json.loads(x) for x in (root/'screen-events.jsonl').read_text(encoding='utf-8').splitlines()]
 origin=json.loads((root/'recording.json').read_text())['started_wall']
 start=next(x['wall_time'] for x in events if x['kind']=='recording')-origin
 finish=next(x['wall_time'] for x in events if x['kind']=='finished')-origin
 return root,video,events,origin,start,finish

def clip(arm,index,video,start,end,speed=1,hold=0,heading='',caption=''):
 assert end>start and speed>=1 and hold>=0
 name=f'{arm}-{index:02}'
 (OUT/f'{name}-title.txt').write_text(heading,encoding='utf-8',newline='\n')
 (OUT/f'{name}-caption.txt').write_text(caption,encoding='utf-8',newline='\n')
 filters=[f'setpts=(PTS-STARTPTS)/{speed}', 'fps=12','scale=960:576',
          'pad=960:896:0:70:color=0x111823',
          f'drawtext=fontfile=font.ttc:textfile={name}-title.txt:fontsize=25:fontcolor=white:x=18:y=19']
 for line_index,line in enumerate(caption.splitlines()):
  line_name=f'{name}-line-{line_index}.txt'
  (OUT/line_name).write_text(line,encoding='utf-8',newline='\n')
  filters.append(f'drawtext=fontfile=font.ttc:textfile={line_name}:fontsize=22:fontcolor=white:x=18:y={669+34*line_index}')
 if hold:filters.append(f'tpad=stop_mode=clone:stop_duration={hold}')
 output=OUT/f'{name}.mp4'
 run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(max(0,start)),'-t',str(end-start),'-i',str(video),'-an','-vf',','.join(filters),'-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p','-y',str(output)])
 return {'source':str(video),'start':start,'end':end,'speed':speed,'hold':hold,'heading':heading,'caption':caption,'file':output.name}

Aroot,Avideo,Aevents,Aorigin,Astart,Aend=material('A')
A=[clip('A',0,Avideo,Astart,Astart+3,heading='本次 A｜沒有 Nudge｜真實 CLI 錄影',caption='相同任務：多裝置勾選、取消、批次登出。\nSol medium Actor；無 Provider。'),
   clip('A',1,Avideo,Astart+3,Aend-5,speed=max(1,(Aend-Astart-8)/10),heading='本次 A｜實作與驗證快轉',caption='實際操作快轉；沒有補寫 Actor 發言或重演程式碼。'),
   clip('A',2,Avideo,Aend-5,min(duration(Avideo),Aend+2),hold=4,heading='本次 A｜最後交付',caption='本次固定驗收：通過（107 項測試記錄）。\n選取清單與更新方法仍各自可選。')]
Broot,Bvideo,Bevents,Borigin,Bstart,Bend=material('B')
rows=[]
for path in (Broot/'codex-home/sessions').rglob('*.jsonl'):
 rows.extend(json.loads(line) for line in path.read_text(encoding='utf-8').splitlines())
contexts=[]
for row in rows:
 p=row.get('payload',{})
 if p.get('role')=='developer':
  text='\n'.join(x.get('text','') for x in p.get('content',[]) if isinstance(x,dict))
  if 'OBSERVED: FilteredDeviceList:' in text:
   fields=[line for line in text.splitlines() if line.startswith(('OBSERVED:','WHY:','STRUCTURE:','REQUIRED:'))]
   later=next(r for r in rows if epoch(r['timestamp'])>epoch(row['timestamp']) and r.get('payload',{}).get('type')=='custom_tool_call' and 'apply_patch' in str(r['payload'].get('input','')) and 'src/components' in str(r['payload'].get('input','')))
   contexts.append({'context_time':row['timestamp'],'raw_context':text,'caption_fields':fields,'context_video_time':epoch(row['timestamp'])-Borigin,'next_edit_time':later['timestamp'],'next_edit_video_time':epoch(later['timestamp'])-Borigin,'next_edit_call':later['payload']})
assert len(contexts)==2
fixed=json.loads((Broot/'fixed-checks/evidence.json').read_text(encoding='utf-8'))
assert fixed['checks']=={'reserved':'pass'},fixed['checks']
B=[]
def add(start,end,**kw):B.append(clip('B',len(B),Bvideo,start,end,**kw))
add(Bstart,Bstart+3,heading='本次 B｜有 Nudge｜真實 CLI 錄影',caption='相同任務、Actor、基底；Provider 為 Sol medium。\n提醒字幕直接取自 Actor 實際收到的上下文。')
cursor=Bstart+3
for i,c in enumerate(contexts):
 t=c['context_video_time'];change=c['next_edit_video_time']
 if t-.6>cursor:
  add(cursor,t-.6,speed=max(1,(t-.6-cursor)/6),heading='本次 B｜實作／等待快轉',caption='時間各自壓縮，不可用左右影片長度比較耗時。')
 # Original footage continues; the subtitle is the actual hidden Hook context, not invented dialogue.
 add(t-.6,t+.4,hold=7,heading=f'本次 B｜第 {i+1} 則 Nudge 真正送達｜原文字幕',caption='\n'.join(c['caption_fields'])+'\n字幕譯意：'+('清單與更新方法要成對，讀寫由同一份資料負責。' if i==0 else '先確定 Props 的種類，再取出清單與更新方法。'))
 if change-.5>t+.4:
  add(t+.4,change-.5,speed=max(1,(change-.5-t-.4)/2),heading='本次 B｜收到提醒後，Actor 繼續實作',caption='沒有另加提示；接著播放它的實際下一次產品修改。')
 meaning='Actor 改為成對型別，並用同一個判斷選擇讀寫來源。' if i==0 else 'Actor 先收窄 Props，再解構選取清單與更新方法。'
 add(change-.5,change+2.5,hold=3,heading='本次 B｜Actor 的實際下一次修改',caption=meaning+'\n原始 apply_patch 呼叫與完整 Patch 另附；畫面未重新繪製。')
 cursor=change+2.5
if Bend-5>cursor:
 add(cursor,Bend-5,speed=max(1,(Bend-5-cursor)/8),heading='本次 B｜其餘實作與驗證快轉',caption='本次共 2 則已送達提醒、2 次沉默。\n保留真實結果，沒有為畫面或品味重抽。')
add(Bend-5,min(duration(Bvideo),Bend+2),hold=4,heading='本次 B｜最後交付',caption='本次固定驗收：通過（107 項測試記錄）。\n第一則 Nudge 後的成對約束保留在最後 Patch。')
for arm,items in [('A',A),('B',B)]:
 listing=OUT/f'{arm}-concat.txt';listing.write_text(''.join("file '"+x['file']+"'\n" for x in items),encoding='utf-8')
 run(['ffmpeg','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(listing),'-c','copy','-y',str(OUT/f'{arm}-edited.mp4')])
Da=duration(OUT/'A-edited.mp4');Db=duration(OUT/'B-edited.mp4')
# Each path is independently edited; hold the completed side rather than imply synchronized timing.
filtergraph=f'[0:v]tpad=stop_mode=clone:stop_duration={max(0,Db-Da)+1}[a];[1:v]tpad=stop_mode=clone:stop_duration={max(0,Da-Db)+1}[b];[a][b]hstack=inputs=2:shortest=1[v]'
movie=OUT/'element-live-comparison.mp4'
run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(OUT/'A-edited.mp4'),'-i',str(OUT/'B-edited.mp4'),'-filter_complex',filtergraph,'-map','[v]','-an','-c:v','libx264','-preset','veryfast','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart','-y',str(movie)])
# A compact screen-recording GIF is the README preview; full video retains readable resolution.
gif=OUT/'element-live-comparison.gif'
run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(movie),'-filter_complex','fps=2,scale=1280:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=48:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=3','-loop','0','-y',str(gif)])
manifest={'method':'Actual classic-console screen capture; implementation / waiting sped up, real frames held, Nudge subtitle copied from actual developer context. No code illustration or reenactment.','arms':{'A':A,'B':B},'contexts':contexts,'runtime_comparison':False,'movie_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'gif_sha256':hashlib.sha256(gif.read_bytes()).hexdigest(),'duration_seconds':duration(movie),'raw_sources':{a:hashlib.sha256((ROOT/a/'raw-screen.mkv').read_bytes()).hexdigest() for a in ['A','B']}}
(OUT/'edit-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'movie':str(movie),'gif':str(gif),'seconds':manifest['duration_seconds'],'gif_bytes':gif.stat().st_size},ensure_ascii=False),flush=True)