"""Render editable faction content as cinematic, modular image sections."""
import argparse
import hashlib
import html
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'preview'
W = 1000
BG = '#08070d'
WHITE = '#f4edf8'
MUTED = '#c9bfd2'
PURPLE = '#c49be7'
FONTS = Path('/usr/share/fonts/truetype/dejavu')

def font(size, serif=False, bold=False):
    return ImageFont.truetype(str(FONTS / (('DejaVuSerif' if serif else 'DejaVuSans') + ('-Bold' if bold else '') + '.ttf')), size)

MEASURE = ImageDraw.Draw(Image.new('RGB', (1, 1)))
def lines(text, f, width):
    result=[]
    for para in text.split('\n'):
        line=''
        for word in para.split():
            if MEASURE.textlength(word,font=f)>width: raise ValueError('Word too wide: '+word)
            candidate=(line+' '+word).strip()
            if MEASURE.textlength(candidate,font=f)>width:
                result.append(line);line=word
            else:line=candidate
        result.append(line)
    return result

def block_height(text,size,width):return len(lines(text,font(size),width))*round(size*1.4)

class Panel:
    def __init__(self,ornate=False):
        self.im=Image.new('RGB',(W,6000),BG);self.d=ImageDraw.Draw(self.im);self.y=0;self.ornate=ornate
    def text(self,t,size=29,color=MUTED,x=70,y=None,width=860,center=False,serif=False,bold=False,gap=20):
        start=self.y if y is None else y
        f=font(size,serif,bold)
        for line in lines(t,f,width):
            px=x+(width-self.d.textlength(line,font=f))/2 if center else x
            self.d.text((px,start),line,font=f,fill=color)
            start+=round(size*1.4)
        if y is None:self.y=start+gap
        return start+gap
    def rule(self):
        self.y+=16;self.d.line((70,self.y,930,self.y),fill='#50365d',width=2);self.y+=30
    def label(self,t):self.text(t,20,PURPLE,center=True,bold=True,gap=12)
    def heading(self,t,size=49):self.text(t,size,WHITE,center=True,serif=True,gap=20)
    def scene(self,filename,title=None,eyebrow=None):
        art=Image.open(ROOT/'assets'/filename).convert('RGB')
        h=round(art.height*W/art.width);art=art.resize((W,h),Image.Resampling.LANCZOS)
        # Typesetting scrim: protect contrast and join the image to the text canvas.
        mask=Image.new('RGBA',(W,h),(0,0,0,0));md=ImageDraw.Draw(mask)
        for row in range(h):
            v=max(0,(row/h-.65)/.35)
            if v:md.line((0,row,W,row),fill=(8,7,13,round(min(1,v)*255)))
        art=Image.alpha_composite(art.convert('RGBA'),mask).convert('RGB')
        self.im.paste(art,(0,self.y));top=self.y;self.y+=h
        if title:
            self.y=top+h-125
            if eyebrow:self.label(eyebrow)
            self.heading(title,46)
            self.y=max(self.y,top+h+10)
    def names(self,names):
        self.text('  ·  '.join(names),22,PURPLE,center=True,gap=24)
    def grid(self,items,cols=2,size=27,numbered=False):
        gutter=34;width=(860-gutter*(cols-1))//cols
        for row in range(0,len(items),cols):
            bottom=self.y
            for col,(title,body) in enumerate(items[row:row+cols]):
                x=70+col*(width+gutter);y=self.y
                if numbered:
                    self.d.text((x,y),f'{row+col+1:02}',font=font(48,True),fill='#79538e');y+=65
                self.d.line((x,y,x+width,y),fill='#50365d',width=2);y+=16
                y=self.text(title,27,WHITE,x=x,y=y,width=width,bold=True,gap=10)
                y=self.text(body,size,MUTED,x=x,y=y,width=width,gap=30)
                bottom=max(bottom,y)
            self.y=bottom+10
    def metrics(self,items):
        gutter=24;width=(860-gutter)//2
        for r in range(0,len(items),2):
            bottom=self.y
            for j,(value,label) in enumerate(items[r:r+2]):
                x=70+j*(width+gutter)
                self.d.rectangle((x,self.y,x+width,self.y+150),fill='#15101e',outline='#51335f',width=2)
                y=self.text(value,57,WHITE,x=x,y=self.y+12,width=width,center=True,serif=True,gap=0)
                y=self.text(label,24,PURPLE,x=x+14,y=y,width=width-28,center=True,gap=20)
                bottom=max(bottom,y,self.y+170)
            self.y=bottom
    def render(self):
        assert self.y+40<6000,'Panel exceeds canvas'
        im=self.im.crop((0,0,W,self.y+40))
        if self.ornate:
            backdrop=Image.open(ROOT/'assets'/'panel-background.jpg').convert('RGB').resize(im.size,Image.Resampling.LANCZOS)
            backdrop=ImageEnhance.Brightness(backdrop).enhance(0.55)
            ink=ImageChops.difference(im,Image.new('RGB',im.size,BG)).convert('L').point(lambda v:255 if v else 0)
            backdrop.paste(im,(0,0),ink);im=backdrop
            # Slender metallic rules frame the Code without repeating a full border.
            d=ImageDraw.Draw(im)
            for x in [28,36,964,972]:d.line((x,30,x,im.height-25),fill='#60466c',width=1)
            for y in [30,im.height-25]:
                d.line((28,y,972,y),fill='#60466c',width=1)
                d.polygon([(486,y),(500,y-7),(514,y),(500,y+7)],fill=PURPLE)
        return im

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    c=json.loads((ROOT/'content.json').read_text());panels=[]
    def save(name,p,alt):
        im=p.render();im.save(OUT/(name+'.png'));panels.append((name,im,alt))
    p=Panel();p.scene('cover.jpg');p.label(c['tagline'].upper());p.rule()
    s=c['origin'];p.label(s['eyebrow']);p.heading(s['title'])
    for t in s['paragraphs']:p.text(t,29,center=True)
    save('01-origin',p,'Rogue Assembly. '+' '.join(s['paragraphs']))
    s=c['culture'];p=Panel();p.scene('clubhouse.jpg',s['title'],s['eyebrow']);p.names(c['scene_cast']['clubhouse'])
    for t in s['paragraphs'][:2]:p.text(t,29,center=True)
    p.rule();p.label(c['inclusion_heading']);p.text(s['paragraphs'][2],29,center=True)
    save('02-culture',p,s['title']+'. '+', '.join(c['scene_cast']['clubhouse'])+'. '+' '.join(s['paragraphs']))
    for name,title,art in [('leadership','The Assembly’s Leadership','leadership.jpg'),('vips','VIP Rogues','vips.jpg')]:
        p=Panel();p.scene(art,title,'THE PEOPLE WHO HELP US RISE')
        if name=='leadership':p.text(c['leadership_intro'],28,center=True)
        p.grid(c[name],cols=2 if name=='leadership' else 3,size=25)
        save('03-leadership' if name=='leadership' else '04-vips',p,title+'. '+'. '.join(n+': '+r for n,r in c[name]))
    s=c['activities'];p=Panel();p.scene('rooftop.jpg',s['title'],s['eyebrow']);p.names(c['scene_cast']['rooftop']);p.grid(s['items'])
    save('05-activities',p,s['title']+'. '+', '.join(c['scene_cast']['rooftop'])+'. '+'. '.join(t+': '+b for t,b in s['items']))
    s=c['benefits'];p=Panel();p.scene('armory.jpg',s['title'],s['eyebrow']);p.names(c['scene_cast']['armory'])
    p.text(s['items'][0][1],29,center=True);p.rule();p.label(c['metrics_heading']);p.metrics(c['metrics']);p.text(s['note'],24,PURPLE,center=True)
    save('06-benefits',p,s['title']+'. '+', '.join(c['scene_cast']['armory'])+'. '+s['items'][0][1]+'. '+'. '.join(v+' '+l for v,l in c['metrics'])+'. '+s['note'])
    s=c['code'];p=Panel(ornate=True);p.y=65;p.label(s['eyebrow']);p.heading(s['title'],60);p.text(c['code_intro'],29,center=True);p.grid(s['items'],numbered=True)
    save('07-code',p,s['title']+'. '+'. '.join(t+': '+b for t,b in s['items']))
    s=c['join'];p=Panel();p.y=45;p.label(s['eyebrow']);p.heading(s['title'],57)
    for t in s['paragraphs']:p.text(t,29,center=True)
    p.rule();p.text(c['join_cta'],32,WHITE,center=True,bold=True);p.label(c['origin']['paragraphs'][-1])
    save('08-join',p,s['title']+'. '+' '.join(s['paragraphs']))
    full=Image.new('RGB',(W,sum(im.height for _,im,_ in panels)),BG);y=0
    for _,im,_ in panels:full.paste(im,(0,y));y+=im.height
    full.save(OUT/'full-preview.png')
    esc=html.escape;body=''
    for name,im,alt in panels:
        digest=hashlib.sha256((OUT/(name+'.png')).read_bytes()).hexdigest()[:10]
        img=f'<img src="{name}.png?v={digest}" width="{W}" height="{im.height}" alt="{esc(alt,quote=True)}">'
        body+=f'<a href="{esc(c["links"]["apply"],quote=True)}">{img}</a>' if name=='08-join' else img
    body+='<nav>'+ ' · '.join(f'<a href="{esc(url,quote=True)}">{esc(label)}</a>' for label,url in c['links'].items())+'</nav>'
    (OUT/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Rogue Assembly — cinematic draft v2</title><style>body{margin:0;background:#08070d;color:#eee7f2;font:18px sans-serif}main{max-width:1000px;margin:auto}img{display:block;width:100%;height:auto}a{color:#bb8ddd}nav{text-align:center;padding:30px}</style><main>'+body+'</main></html>')
    print('Built',len(panels),'panels;',full.size,'full preview')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=OUT)
    OUT=parser.parse_args().output.resolve();main()
