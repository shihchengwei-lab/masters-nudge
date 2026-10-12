"""Render a side-by-side chat replay from actual A/B records; no model calls."""
from pathlib import Path
import argparse,hashlib,json,subprocess,tempfile
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'docs/examples/element-live-recording'
OUT=ROOT/'docs/images';OUT.mkdir(exist_ok=True)
SOURCE=DATA/'chat-replay-source.json'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--language',choices=['zh-TW','en'],default='zh-TW')
language=parser.parse_args().language
suffix='.en' if language=='en' else ''
s=json.loads(SOURCE.read_text(encoding='utf-8'))
display=s['display_en'] if language=='en' else s['display']

for name,digest in s['source_sha256'].items():
 assert hashlib.sha256((DATA/name).read_bytes()).hexdigest()==digest,name
assert s['actor_messages'][0]['timestamp']<s['nudge']['timestamp']<s['next_edit']['timestamp']<s['actor_messages'][1]['timestamp']
assert len(s['baseline_actor_messages'])==2
LABELS={'AI 的訊息 · 中文節譯': 'AI message · paraphrased', '它實際改了什麼 · 修改紀錄摘要': 'What changed · edit summary', '同樣做完功能，差別在哪裡？': 'Same feature. What changed?', '任務：勾選幾台裝置，一次登出。': 'Task: select devices and sign them out together.', '真實紀錄重建 · 14 秒': 'Real records · 14 seconds', '原話節譯／修改摘要': 'Paraphrased messages / edit summaries', '沒有提醒': 'Without a nudge', '有 Masters’ Nudge 提醒': 'With Masters’ Nudge', '繼續實作與檢查': 'Implementation and checks continue', '中間過程略過': 'Intervening work omitted', '中途收到的提醒 · 白話轉述': 'Feedback received · paraphrased', 'AI 的後續訊息 · 中文節譯': 'Later AI message · paraphrased', '兩邊是真實獨立執行；按各自紀錄節錄，省略等待。': 'Two real, independent runs. Each timeline is condensed; waiting is omitted.', '兩邊都過關；右邊加上約束，避免「畫面看一份，點選卻改另一份」。': 'Both passed. The nudge led to a constraint: screen and clicks must share one record.', '依真實聊天與修改紀錄重建 · 非原始錄影 · 完整來源見案例連結': 'Reconstructed from real messages and edits · Not original footage · Full evidence linked'}
def label(zh):return LABELS[zh] if language=='en' else zh
font_path='C:/Windows/Fonts/msjh.ttc'
def font(size):return ImageFont.truetype(font_path,size)
def text(d,x,y,v,size=28,fill='#edf1f5'):
 d.text((x,y),v,font=font(size),fill=fill,spacing=13)
def chat(d,x,y,message):
 d.rounded_rectangle((x+38,y,x+656,y+138),radius=20,fill='#23344b')
 text(d,x+58,y+15,label('AI 的訊息 · 中文節譯'),19,'#b1c9ec')
 text(d,x+58,y+53,message,27)
def edit(d,x,y,message,color):
 d.rounded_rectangle((x+18,y,x+656,y+158),radius=10,fill='#172c2b',outline=color,width=2)
 text(d,x+38,y+16,label('它實際改了什麼 · 修改紀錄摘要'),20,color)
 text(d,x+38,y+57,message,28)

def frame(t):
 im=Image.new('RGB',(1440,980),'#101722');d=ImageDraw.Draw(im)
 text(d,32,18,label('同樣做完功能，差別在哪裡？'),40)
 text(d,32,80,label('任務：勾選幾台裝置，一次登出。'),28,'#b4c1d3')
 text(d,1000,27,label('真實紀錄重建 · 14 秒'),25,'#f6c36b')
 text(d,1000,74,label('原話節譯／修改摘要'),21,'#97a9bf')
 for x,title,color in [(24,label('沒有提醒'),'#b1c9ec'),(740,label('有 Masters’ Nudge 提醒'),'#80d9b1')]:
  d.rounded_rectangle((x,139,x+676,857),radius=22,fill='#182231')
  text(d,x+24,158,title,31,color)
  chat(d,x,220,display['A_before_translation'] if x==24 else display['B_before_translation'])
 stage=0 if t<2 else 1 if t<6 else 2 if t<11 else 3
 if stage>=1:
  text(d,66,414,label('繼續實作與檢查'),27,'#a2b0c3')
  text(d,66,460,label('中間過程略過'),21,'#7f91a9')
  d.rounded_rectangle((758,380,1396,562),radius=20,fill='#3b2e1b',outline='#f6c36b',width=2)
  text(d,778,394,label('中途收到的提醒 · 白話轉述'),20,'#f6c36b')
  text(d,778,434,display['nudge_paraphrase'],27,'#ffe8c2')
 if stage>=2:
  edit(d,24,582,display['A_edit_summary'],'#b1c9ec')
  edit(d,740,582,display['B_edit_summary'],'#80d9b1')
 if stage>=3:
  # The source of each message is kept distinct from the edit summaries above.
  for x,key in [(24,'A_after_translation'),(740,'B_after_translation')]:
   d.rounded_rectangle((x+38,759,x+656,841),radius=16,fill='#23344b')
   text(d,x+58,767,label('AI 的後續訊息 · 中文節譯'),17,'#b1c9ec')
   text(d,x+58,797,display[key],22)
 if stage<2:
  text(d,32,890,label('兩邊是真實獨立執行；按各自紀錄節錄，省略等待。'),24,'#a4b5cb')
 else:
  text(d,32,882,label('兩邊都過關；右邊加上約束，避免「畫面看一份，點選卻改另一份」。'),28,'#80d9b1')
 text(d,32,931,label('依真實聊天與修改紀錄重建 · 非原始錄影 · 完整來源見案例連結'),19,'#879ab2')
 d.rectangle((32,964,1408,970),fill='#2b394e')
 d.rectangle((32,964,32+1376*min(1,t/14),970),fill='#f6c36b')
 return im
movie=OUT/f'element-chat-replay{suffix}.mp4';gif=OUT/f'element-chat-replay{suffix}.gif'
with tempfile.TemporaryDirectory(prefix='mn-chat-replay-') as tmp:
 tmp=Path(tmp)
 for i in range(140):frame(i/10).save(tmp/f'{i:04}.png')
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-framerate','10','-i',str(tmp/'%04d.png'),'-an','-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart','-y',str(movie)],check=True)
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(movie),'-filter_complex','fps=10,scale=1280:-2:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer','-loop','0','-y',str(gif)],check=True)
manifest={'language':language,'duration_seconds':14,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'media_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [movie,gif]},'display':'Side-by-side chat reconstruction of real A/B records. Actual AI message excerpts and delivered Nudge are paraphrased into the selected display language; saved edit summaries are explicitly separate from speech. Independently condensed timelines, no invented dialogue.'}
(DATA/f'chat-replay-integrity{suffix}.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Rendered 14-second side-by-side chat replay.')
