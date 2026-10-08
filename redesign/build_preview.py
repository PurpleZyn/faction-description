"""Build the isolated redesign preview. Does not touch docs or production config."""
import argparse
import html
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'preview'
W = 1000
BG = '#08070d'
WHITE = '#eee7f2'
MUTED = '#c8bed2'
PURPLE = '#bb8ddd'
FONTS = Path('/usr/share/fonts/truetype/dejavu')

def font(size, serif=False, bold=False):
    stem = 'DejaVuSerif' if serif else 'DejaVuSans'
    return ImageFont.truetype(str(FONTS / (stem + ('-Bold' if bold else '') + '.ttf')), size)

MEASURE = ImageDraw.Draw(Image.new('RGB', (1,1)))
def lines(text, f, width):
    result = []
    for para in text.split('\n'):
        line = ''
        for word in para.split():
            if MEASURE.textlength(word, font=f) > width:
                raise ValueError('Unbreakable word too wide: ' + word)
            candidate = (line + ' ' + word).strip()
            if MEASURE.textlength(candidate, font=f) > width:
                result.append(line)
                line = word
            else:
                line = candidate
        result.append(line)
    return result

class Panel:
    def __init__(self):
        self.y = 48
        self.ops = []
    def text(self, value, size=29, color=MUTED, center=False, serif=False, bold=False, gap=22):
        f = font(size, serif, bold)
        for line in lines(value, f, W-240):
            x = (W-MEASURE.textlength(line, font=f))/2 if center else 120
            self.ops.append(('text', (x,self.y), line, f, color))
            self.y += int(size*1.48)
        self.y += gap
    def heading(self, eyebrow, title):
        self.text(eyebrow,20,PURPLE,True,bold=True,gap=16)
        self.text(title,46,WHITE,True,serif=True,gap=30)
    def art(self, filename):
        im=Image.open(ROOT/'assets'/filename).convert('RGB')
        im=im.resize((W,round(im.height*W/im.width)),Image.Resampling.LANCZOS)
        self.ops.append(('image', im, self.y))
        self.y += im.height + 28
    def render(self):
        im=Image.open(ROOT/'assets'/'panel-background.jpg').convert('RGB').resize((W,self.y+24),Image.Resampling.LANCZOS)
        d=ImageDraw.Draw(im)
        d.line((72,16,W-72,16),fill='#493055',width=2)
        d.polygon([(494,16),(500,10),(506,16),(500,22)],fill=PURPLE)
        for op in self.ops:
            if op[0]=='image': im.paste(op[1],(0,op[2]))
            else: d.text(op[1],op[2],font=op[3],fill=op[4])
        return im

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    c=json.loads((ROOT/'content.json').read_text())
    panels=[]
    def save(name,p,alt):
        im=p.render();im.save(OUT/(name+'.png'));panels.append((name,im,alt))
    p=Panel();p.y=0;p.art('cover.jpg');p.text(c['tagline'],28,WHITE,True,serif=True)
    s=c['origin'];p.heading(s['eyebrow'],s['title'])
    for t in s['paragraphs']:p.text(t,29,center=True)
    save('01-origin',p,'Rogue Assembly: '+ ' '.join(s['paragraphs']))
    s=c['culture'];p=Panel();p.heading(s['eyebrow'],s['title'])
    for t in s['paragraphs']:p.text(t)
    save('02-culture',p,s['title']+'. '+' '.join(s['paragraphs']))
    for name,title,art in [('leadership','The Assembly’s Leadership','leadership.jpg'),('vips','VIP Rogues','vips.jpg')]:
        p=Panel();p.heading('THE PEOPLE WHO HELP US RISE',title);p.art(art)
        if name=='leadership':p.text('The members are Rogue Assembly. Leadership exists to help them succeed.',27,center=True)
        for member,role in c[name]:
            p.text(member.upper(),24,PURPLE,bold=True,gap=0)
            p.text(role,27,gap=16)
        save('03-leadership' if name=='leadership' else '04-vips',p,title+'. '+ '. '.join(n+': '+r for n,r in c[name]))
    for name,order in [('activities','05'),('benefits','06'),('code','07')]:
        s=c[name];p=Panel();p.heading(s['eyebrow'],s['title'])
        for i,(title,body) in enumerate(s['items'],1):
            p.text(f'{i:02d}  {title}',29,WHITE,bold=True,gap=8)
            p.text(body,28,gap=30)
        if 'note' in s:p.text(s['note'],23,PURPLE)
        save(order+'-'+name,p,s['title']+'. '+'. '.join(t+': '+b for t,b in s['items'])+(' '+s['note'] if 'note' in s else ''))
    s=c['join'];p=Panel();p.heading(s['eyebrow'],s['title'])
    for t in s['paragraphs']:p.text(t,29,center=True)
    p.text('MEET THE ROGUES & APPLY',30,PURPLE,True,bold=True)
    save('08-join',p,s['title']+'. '+' '.join(s['paragraphs']))
    full=Image.new('RGB',(W,sum(im.height for _,im,_ in panels)),BG);y=0
    for _,im,_ in panels:full.paste(im,(0,y));y+=im.height
    full.save(OUT/'full-preview.png')
    esc=html.escape
    body=''
    for name,im,alt in panels:
        img=f'<img src="{name}.png" width="{W}" height="{im.height}" alt="{esc(alt,quote=True)}">'
        body+=f'<a href="{esc(c["links"]["apply"],quote=True)}">{img}</a>' if name=='08-join' else img
    body+='<nav>'+ ' · '.join(f'<a href="{esc(url,quote=True)}">{esc(label)}</a>' for label,url in c['links'].items())+'</nav>'
    (OUT/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Rogue Assembly — redesign draft</title><style>body{margin:0;background:#08070d;color:#eee7f2;font:18px sans-serif}main{max-width:1000px;margin:auto}img{display:block;width:100%;height:auto}a{color:#bb8ddd}nav{text-align:center;padding:30px}</style><main>'+body+'</main></html>')
    print('Built',len(panels),'panels;',full.size,'full preview')

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=OUT)
    OUT = parser.parse_args().output.resolve()
    main()
