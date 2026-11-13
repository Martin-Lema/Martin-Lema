"""Original pixel geometry. No fonts, images, network dependencies or SVG scripts.

World geometry uses a four-unit grid. Sprites use one-unit bitmaps enlarged
by integer transforms. Pixel lettering is original 5x7 path geometry.
"""
from html import escape
import random

P = {}

def palette(values):
    global P
    P = values

def color(value):
    return P.get(value, value)

def rect(x, y, w, h, fill, extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color(fill)}" {extra}/>'

def path(d, fill, extra=''):
    return f'<path d="{d}" fill="{color(fill)}" {extra}/>'

def text(x, y, content, size=20, fill='ink', anchor='start', extra=''):
    return (f'<text x="{x}" y="{y}" fill="{color(fill)}" font-size="{size}" '
            f'text-anchor="{anchor}" {extra}>{escape(str(content))}</text>')

def group(content, x=0, y=0, scale=1, extra=''):
    return f'<g transform="translate({x} {y}) scale({scale})" {extra}>{content}</g>'

FONT = dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-/\' ', [
 '01110/10001/10001/11111/10001/10001/10001','11110/10001/10001/11110/10001/10001/11110',
 '01111/10000/10000/10000/10000/10000/01111','11110/10001/10001/10001/10001/10001/11110',
 '11111/10000/10000/11110/10000/10000/11111','11111/10000/10000/11110/10000/10000/10000',
 '01111/10000/10000/10111/10001/10001/01111','10001/10001/10001/11111/10001/10001/10001',
 '11111/00100/00100/00100/00100/00100/11111','00111/00010/00010/00010/10010/10010/01100',
 '10001/10010/10100/11000/10100/10010/10001','10000/10000/10000/10000/10000/10000/11111',
 '10001/11011/10101/10101/10001/10001/10001','10001/11001/11001/10101/10011/10011/10001',
 '01110/10001/10001/10001/10001/10001/01110','11110/10001/10001/11110/10000/10000/10000',
 '01110/10001/10001/10001/10101/10010/01101','11110/10001/10001/11110/10100/10010/10001',
 '01111/10000/10000/01110/00001/00001/11110','11111/00100/00100/00100/00100/00100/00100',
 '10001/10001/10001/10001/10001/10001/01110','10001/10001/10001/10001/10001/01010/00100',
 '10001/10001/10001/10101/10101/10101/01010','10001/10001/01010/00100/01010/10001/10001',
 '10001/10001/01010/00100/00100/00100/00100','11111/00001/00010/00100/01000/10000/11111',
 '01110/10001/10011/10101/11001/10001/01110','00100/01100/00100/00100/00100/00100/01110',
 '01110/10001/00001/00010/00100/01000/11111','11110/00001/00001/01110/00001/00001/11110',
 '00010/00110/01010/10010/11111/00010/00010','11111/10000/10000/11110/00001/00001/11110',
 '01110/10000/10000/11110/10001/10001/01110','11111/00001/00010/00100/01000/01000/01000',
 '01110/10001/10001/01110/10001/10001/01110','01110/10001/10001/01111/00001/00001/01110',
 '00000/00000/00000/00000/00000/00100/00100','00000/00000/00000/11111/00000/00000/00000',
 '00001/00001/00010/00100/01000/10000/10000','00100/00100/00000/00000/00000/00000/00000',
 '000/000/000/000/000/000/000']))

def pixel_text(label, x, y, unit=4, fill='ink', center=False):
    label = label.upper()
    glyphs = [FONT.get(c, FONT[' ']).split('/') for c in label]
    width = sum(len(g[0]) + 1 for g in glyphs) - 1
    cursor = x - width * unit / 2 if center else x
    bits = []
    for glyph in glyphs:
        for row, line in enumerate(glyph):
            for col, bit in enumerate(line):
                if bit == '1':
                    bits.append(f'M{cursor+col*unit:g} {y+row*unit:g}h{unit}v{unit}h-{unit}z')
        cursor += (len(glyph[0])+1)*unit
    return path(''.join(bits), fill)

# Each species has its own anatomy and feather map; dots are transparent.
SPRITES = {
 'kingfisher': [
 '...........BBBBB............', '.........BBbbbbBB..........',
 '........BBbbBBbBBB.........', '........BbbWIKBBBDDDDDDDDD.',
 '........BBBBBBWWBDDDDD.....', '.......BBBBOWWOOO.........',
 '......BBBbBOOOOOO.........', '.....BBBbbBGOOOOG.........',
 '....BBBbbBBOOOGGG.........', '...BBBBbbBBOOOGGG.........',
 '..BB.BBbbBBOOGGG..........', '.BB..BBBBBBOOGGG..........',
 'BB...BBBBBOOGGG...........', '.....BBBBBOOGG............',
 '......BBBBOOG.............', '.......BBOOG..............',
 '........OOO...............', '........D.D...............',
 '.......DD.DD..............'],
 'robin': [
 '..........RRRR............', '........RRrrrrRR..........',
 '.......RrrrrrOORR.........', '.......RrrrrOOIKRD........',
 '.......RrrrOOOOORDDD......', '......RRrrOOOOOOR.........',
 '.....RRrrrOOOOOGR.........', '....RRrrrrrOOOGGR.........',
 '..RRRrrrrrRRWGGGR.........', 'RRR.RrrrrRRWWWGGR.........',
 'RR..RrrrRRWWWWWGR.........', '....RRRRRWWWWWGR..........',
 '.....RRRWWWWWGR...........', '......RRWWWWGR............',
 '........RRRR..............', '.........D.D..............',
 '........DD.DD.............'],
 'owl': [
 '....RR........RR....', '....RrR......RrR....', '....RrrRRRRRRrrR....',
 '...RrrrrrrrrrrrrR...', '..RrrGGGrrrGGGrrrR..', '..RrGWWWGrGWWWGrrR..',
 '..RrGWIKGrGWIKGrrR..', '..RrGWWWGrGWWWGrrR..', '...RrGGGrOrGGGrrR...',
 '...RrrrrrOrrrrrrR...', '..RRrrrGrrrGrrrrRR..', '..RrRrGGrGrGGrRrrR..',
 '..RrRrrGrGrGrrRrrR..', '..RrRrGGrGrGGrRrrR..', '..RrRrrGrGrGrrRrrR..',
 '...RRrGGrGrGGrRRR...', '....RrrrrrrrrrrR....', '.....RRrrrrrrRR.....',
 '.......RRRRRR.......', '.......DD..DD.......'],
 'hummingbird': [
 '...........SSSS.................', '..........SssssS................',
 '..........SssIKSDDDDDDDDDDDDD...', '.........SSssssS................',
 '........SSsPPPS.................', '.......SSssPPPS.................',
 '......SSsssGGS..................', '.....SSssssGS...................',
 '....SSssssSS....................', '...SSsssSS......................',
 '..SSssSS........................', '.SSsSS..........................',
 'SSSS............................', 'SS..............................'],
 'gull-body': [
 '................WWWW...........', '...............WwwwWW..........',
 '...............WwIKWWGGG.......', '..............WWwwWWWGG........',
 '..KK..........WWwwWWW..........', '...KKKWWWWWWWWWWwwWW...........',
 '.....KwwwwwwwwwwwwWW...........', '......WWWWWWWWWWWWW............',
 '..........DD.DD................'],
 'wing-up': [
 '..KK................', '...KK...............', '...Kww..............',
 '....Kww.............', '.....Kww............', '.....Kwww...........',
 '......Kwww..........', '.......Kwwww........', '........Kwwww.......',
 '.........Kwwww......', '..........WWWWW.....', '...........WWWWW....'],
 'wing-mid': [
 '....................', '....................', '....................',
 '....................', '....................', '....................',
 '..KKKKKK............', '....Kwwwwwwww.......', '......Kwwwwwwww.....',
 '........WWWWWWWW....', '..........WWWWW.....', '...........WWWW.....'],
 'wing-down': [
 '....................', '....................', '....................',
 '....................', '....................', '....................',
 '....................', '....................', '....................',
 '....................', '...........WWWW.....', '..........Wwww......',
 '.........Wwww.......', '........Wwww........', '.......Wwww.........',
 '......Www...........', '.....Kww............', '....KK..............'],
}

SPRITE_COLORS = {'D':'ink','K':'deep','I':'deep','W':'cream','w':'mist',
 'B':'cobalt','b':'blue','O':'orange','G':'gold','R':'brown','r':'sand',
 'S':'forest','s':'sage','P':'rose'}

def bitmap(rows):
    by_color = {}
    for y, line in enumerate(rows):
        x = 0
        while x < len(line):
            ch = line[x]
            end = x + 1
            while end < len(line) and line[end] == ch:
                end += 1
            if ch != '.':
                by_color.setdefault(ch, []).append(f'M{x} {y}h{end-x}v1h-{end-x}z')
            x = end
    return ''.join(path(''.join(bits), SPRITE_COLORS[ch]) for ch,bits in by_color.items())

CSS = '''
text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace}
@keyframes breeze{0%,100%{transform:translateX(0)}50%{transform:translateX(24px)}}
@keyframes tide{0%,100%{transform:translateX(-8px)}50%{transform:translateX(8px)}}
@keyframes flight{from{transform:translateX(-220px)}to{transform:translateX(1420px)}}
@keyframes hover{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}
@keyframes hop{0%,70%,100%{transform:translate(0,0)}74%{transform:translate(2px,-3px)}78%,88%{transform:translate(4px,0)}92%{transform:translate(2px,-3px)}}
@keyframes look{0%,60%,100%{transform:rotate(0deg)}65%,75%{transform:rotate(3deg)}}
@keyframes blink{0%,93%,97%,100%{opacity:0}94%,96%{opacity:1}}
@keyframes wing1{0%,24%,100%{opacity:1}25%,99%{opacity:0}}
@keyframes wing2{0%,24%,50%,74%,100%{opacity:0}25%,49%,75%,99%{opacity:1}}
@keyframes wing3{0%,49%,75%,100%{opacity:0}50%,74%{opacity:1}}
@keyframes glimmer{0%,100%{opacity:.4}50%{opacity:.85}}
.cloud{animation:breeze 38s ease-in-out infinite}.far-cloud{animation:breeze 61s ease-in-out infinite reverse}
.wave{animation:tide 8s ease-in-out infinite}.wave-slow{animation:tide 13s ease-in-out -3s infinite reverse}
.fly{transform:translateX(352px);animation:flight 34s linear -12s infinite}.fly-far{transform:translateX(680px);animation:flight 49s linear -35s infinite}.fly-near{transform:translateX(440px);animation:flight 27s linear -20s infinite}
.hover{animation:hover 2s ease-in-out infinite}.hop{animation:hop 9s steps(2,end) infinite}
.look{transform-origin:12px 17px;animation:look 11s steps(2,end) infinite}
.eyelid{opacity:0;animation:blink 7.5s steps(1,end) infinite}
.w1{animation:wing1 1.6s steps(1,end) infinite}.w2{opacity:0;animation:wing2 1.6s steps(1,end) infinite}.w3{opacity:0;animation:wing3 1.6s steps(1,end) infinite}
.hum1{animation:wing1 .28s steps(1,end) infinite}.hum2{opacity:0;animation:wing2 .28s steps(1,end) infinite}.hum3{opacity:0;animation:wing3 .28s steps(1,end) infinite}
.star{animation:glimmer 9s ease-in-out infinite}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}
'''

def bird_defs():
    out = []
    for name in ['kingfisher','robin','owl','hummingbird','gull-body','wing-up','wing-mid','wing-down']:
        out.append(f'<g id="{name}-pixels">{bitmap(SPRITES[name])}</g>')
    out.append('<g id="kingfisher"><g class="look"><use href="#kingfisher-pixels"/></g></g>')
    out.append('<g id="robin"><g class="hop"><use href="#robin-pixels"/></g></g>')
    out.append('<g id="owl"><use href="#owl-pixels"/>'+rect(6,6,3,1,'brown','class="eyelid"')+rect(12,6,3,1,'brown','class="eyelid"')+'</g>')
    wings = ''.join(f'<use href="#wing-{n}-pixels" class="w{i}"/>' for i,n in enumerate(['up','mid','down'],1))
    out.append(f'<g id="seagull"><use href="#gull-body-pixels" x="0" y="9"/>{wings}</g>')
    humwing = (path('M8 6H6V3H4V0H2v5h2v4h4z','mist','class="hum1"')+
               path('M8 7H3V5H0v3h3v2h5z','foam','class="hum2"')+
               path('M8 7H5v3H3v4h2v-2h3z','mist','class="hum3"'))
    out.append(f'<g id="hummingbird"><g class="hover">{humwing}<use href="#hummingbird-pixels"/></g></g>')
    return ''.join(out)

def bird(species,x,y,scale=3,extra=''):
    return group(f'<use href="#{species}"/>',x,y,scale,extra)

def svg(title, description, content, height, static=False):
    style = '' if static else f'<style>{CSS}</style>'
    # Explicit static opacity keeps the first wing frame and open eyes visible.
    if static:
        style = '<style>.fly{transform:translateX(352px)}.fly-far{transform:translateX(680px)}.fly-near{transform:translateX(440px)}.w2,.w3,.hum2,.hum3,.eyelid{opacity:0}text{font-family:Menlo,Consolas,monospace}</style>'
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="'+str(height)+'" '
            f'viewBox="0 0 1200 {height}" role="img" aria-labelledby="title desc">'
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>'
            f'{style}<defs>{bird_defs()}</defs><g shape-rendering="crispEdges">{content}</g></svg>\n')

def cloud(x,y,scale=1,fill='cream',kind='cloud'):
    p = path('M0 20h16V12h20V4h32v8h20v8h24v12H0z',fill)
    return group(f'<g class="{kind}">{p}</g>',x,y,scale)

def pine(x,y,scale=1,fill='forest'):
    b = rect(-4,92,8,28,'brown')
    b += path('M-4 0h8v12h8v12h8v12h8v8H16v8h20v12h8v8H24v8h20v12h12v8H-56V88h12V76h20v-8h-20V56h20v-8h8v-8h-16V28h12V16h12z',fill)
    b += path('M-4 12h8v16h8v8H4v20h16v8H4v24h20v8H-4z','pine' if fill=='forest' else fill)
    return group(b,x,y,scale)

def flowers(x,y,scale=1):
    b=''
    for i,offset in enumerate([0,24,52]):
        xx=offset; yy=8*(i%2)
        b+=rect(xx,yy,4,36-yy,'pine')+rect(xx-8,yy+16,8,4,'sage')
        b+=rect(xx-4,yy-8,12,4,'rose')+rect(xx-8,yy-4,20,8,'rose')+rect(xx-4,yy+4,12,4,'rose')+rect(xx,yy-4,4,8,'gold')
    return group(b,x,y,scale)

def stars(seed=2):
    rng=random.Random(seed);b=''
    for i in range(34):
        x=rng.randrange(12,288)*4;y=rng.randrange(7,62)*4
        if (108<y<244 and 180<x<1020) or (52<y<92 and 380<x<820):continue
        b+=rect(x,y,4,4,'sand',f'class="star" style="animation-delay:-{i%9}s"')
        if i%8==0: b+=rect(x-4,y,12,4,'sand')+rect(x,y-4,4,12,'sand')
    return b

def coast(night=False):
    b=rect(0,0,1200,560,'night' if night else 'sky')
    # Pixel sunset / sun, no gradients: discrete atmospheric bands.
    b+=rect(0,252,1200,112,'lavender' if night else 'paper')
    b+=rect(0,332,1200,68,'rose' if night else 'sand')
    b+=path('M876 248h48v8h16v12h8v48h-8v12h-16v8h-48v-8h-16v-12h-8v-48h8v-12h16z','gold' if night else 'cream')
    if night:b+=stars()
    else:b+=cloud(48,72,1.6)+cloud(892,100,1.8,kind='far-cloud')+cloud(452,280,.8,kind='far-cloud')
    b+=path('M0 368V340h40v-16h40v-20h32v-24h28v-16h20v-16h20v16h24v20h24v20h28v20h36v20h40v24H0z','mist' if not night else 'lavender')
    b+=group(path('M660 380v-24h36v-24h32v-20h24v-24h24v-24h20v-20h20v-20h16v20h16v20h24v24h24v16h28v28h40v24h40v24z','mountain' if not night else 'night'),0,32)
    b+=group(path('M780 276h16v-20h20v-20h16v20h16v20h-20v-8h-16v16h-16v-8z','paper' if not night else 'lavender'),0,32)
    b+=path('M0 396v-16h40v-12h64v-12h80v12h48v12h64v16h360v-16h48v-12h48v12h56v-12h72v12h64v16h256v164H0z','water' if not night else 'forest')
    # Two independently moving wave fields, clipped naturally at the SVG edge.
    waves=['','']
    rng=random.Random(19)
    for i in range(85):
        x=rng.randrange(0,300)*4;y=rng.randrange(99,140)*4
        waves[i%2]+=rect(x,y,rng.choice([12,20,28,40,64]),4,'foam' if not night else 'water',f'opacity="{.45 if i%3 else .7}"')
    b+='<g class="wave">'+waves[0]+'</g><g class="wave-slow">'+waves[1]+'</g>'
    b+=path('M0 412h48v12h64v12h80v16h44v20h44v16h-20v16h-56v16h-72v16H0z','sand' if not night else 'brown')
    b+=path('M0 400h48v8h56v16h64v12h48v16h-32v8h-40v12h-64v12H0z','sage' if not night else 'forest')
    b+=path('M0 388h40v12h64v12h56v16h-20v12h-56v16H0z','forest' if not night else 'deep')
    b+=path('M1200 420h-48v12h-60v16h-36v20h-28v20h-36v16h-40v20h-36v36h284z','sand' if not night else 'brown')
    b+=path('M1200 404h-48v16h-44v12h-40v24h-40v20h-28v24h-28v24h228z','forest' if not night else 'deep')
    b+=pine(32,240,1.5,'deep')+pine(102,296,1,'forest')+pine(1172,248,1.7,'deep')+pine(1104,300,1,'forest')
    b+=rect(968,466,92,12,'brown')+rect(1008,466,12,70,'brown')
    # Tiny footprints at the shore.
    for xx,yy in [(188,476),(204,484),(220,488)]:
        b+=rect(xx,yy,4,4,'brown')+rect(xx+4,yy-4,4,4,'brown')
    b+=flowers(32,488,.7)+flowers(1136,488,.75)
    return b

def hero(config):
    b=coast()
    b+=text(52,44,'M / L     •     FIELD NOTES FROM '+config['location'].upper(),15,extra='letter-spacing="2"')
    b+=text(1148,44,'VOL. 01',15,anchor='end',extra='letter-spacing="2"')
    name_width=sum(len(FONT[c.upper()].split('/')[0])+1 for c in config['name'])-1
    name_unit=min(11,1000//name_width)
    b+=pixel_text(config['name'],600,134,name_unit,'sand',True)
    b+=pixel_text(config['name'],600,126,name_unit,'ink',True)
    b+=text(600,248,config['role'].upper(),19,anchor='middle',extra='letter-spacing="3"')
    b+=text(600,278,'CODE, CURIOSITY & A LITTLE WILD WONDER.',15,anchor='middle',extra='letter-spacing="2"')
    # A robin rests on the final A; the feet are aligned with the top of the letter.
    b+=bird('robin',600+name_width*name_unit/2-77,75,3)
    b+=bird('kingfisher',978,409,3)
    b+=group('<g class="fly">'+bird('seagull',0,0,2)+'</g>',0,308)
    b+=group('<g class="fly-far">'+bird('seagull',0,0,1)+'</g>',0,294)
    b+=text(600,530,'A SMALL WORLD. AN OPEN MIND.',14,'cream','middle',extra='letter-spacing="3"')
    return ('Martin Lema — a pixel coast at daybreak','Animated coast, layered mountains, drifting clouds, wing-flapping gulls, a robin perched on the name and a blue-orange kingfisher by the sea.',b,560)

def about(config):
    b=rect(0,0,1200,300,'paper')+rect(0,0,400,300,'sky')
    b+=pine(50,44,1.7)+pine(336,60,1.6)+pine(114,120,.8,'sage')
    b+=rect(0,254,400,46,'sage')+rect(0,280,400,20,'forest')
    # A tiny outdoor coding desk; no invented technology names.
    b+=rect(138,210,132,12,'brown')+rect(150,222,8,58,'brown')+rect(250,222,8,58,'brown')
    b+=rect(164,154,88,56,'ink')+rect(172,162,72,40,'deep')
    b+=path('M180 174h8v4h4v4h-4v4h-8v-4h4v-4h-4z','mint')+rect(200,186,20,4,'mint')
    b+=rect(152,210,108,4,'mist')+bird('robin',272,202,3)+flowers(64,238,.75)
    b+=text(450,56,'01 / THE FOREST DESK',16,'pine',extra='letter-spacing="2"')
    b+=pixel_text('Hello, I am Martin'.replace(',',''),450,90,4)
    b+=text(450,162,config['role'],23)
    b+=text(450,198,config['qualification']+' · '+config['location'],19,'pine')
    b+=text(450,254,'Build thoughtfully. Stay curious.',19)
    return ('The forest desk — about Martin','A forest desk with a pixel terminal and hopping robin. Martin is an apprentice application developer in Switzerland.',b,300)

def species():
    b=rect(0,0,1200,284,'paper')
    labels=[('KINGFISHER','RIVERSIDE WATCH', 'kingfisher'),('ROBIN','THE TRAIL COMPANION','robin'),('OWL','AFTER-HOURS KEEPER','owl'),('SEAGULL','COASTAL EXPLORER','seagull'),('HUMMINGBIRD','FLOWER VISITOR','hummingbird')]
    for i,(name,subtitle,sp) in enumerate(labels):
        xx=i*240
        b+=rect(xx+8,8,224,200,'night' if sp=='owl' else 'sky')
        if sp=='owl':
            b+=rect(xx+28,32,4,4,'sand')+rect(xx+190,60,4,4,'sand')+rect(xx+180,32,16,16,'cream')
        if sp in ('robin','owl','kingfisher'):
            b+=rect(xx+40,160,160,8,'brown')+rect(xx+120,168,8,40,'brown')
        if sp=='kingfisher':b+=rect(xx+8,192,224,16,'water')
        if sp=='hummingbird':b+=flowers(xx+168,140,1)
        if sp=='seagull':b+=rect(xx+8,176,224,32,'water')+rect(xx+40,188,60,4,'foam','class="wave"')
        locations={'kingfisher':(70,65,5),'robin':(65,76,5),'owl':(70,60,5),'seagull':(45,56,5),'hummingbird':(30,92,5)}
        x,y,s=locations[sp];b+=bird(sp,xx+x,y,s)
        b+=text(xx+120,240,name,17,anchor='middle',extra='letter-spacing="1"')
        b+=text(xx+120,266,subtitle,11,'pine','middle',extra='letter-spacing="1"')
    return ('Five residents of the bird universe','Kingfisher: blue back and orange breast. Robin: rounded body and orange face. Owl: paired facial discs and blinking eyes. Gull: white body, grey wings, black tips. Hummingbird: slender bill, green plumage and rapid wingbeats.',b,284)

def section_header(number,title,subtitle,height=180):
    return rect(0,0,1200,height,'paper')+text(48,42,number,14,'pine',extra='letter-spacing="2"')+pixel_text(title,48,70,4)+text(48,134,subtitle,19,'pine')

def nest(config):
    b=section_header('03 / TOOLS FOR THE JOURNEY',"THE DEVELOPER'S NEST",'A growing collection of things I work with.',320)
    for i,t in enumerate(config['technologies']):
        x=48+i*372
        b+=rect(x+8,184,340,108,'sand')+rect(x,176,340,108,'sky')
        b+=text(x+20,212,t['category'],15,'pine',extra='letter-spacing="2"')
        items=t['items']
        label=' / '.join(items) if items else '[ ADD YOUR TECHNOLOGIES ]'
        # Full technology lists stay in native README text; signs are short.
        if len(label)>29:label=label[:26]+'...'
        b+=text(x+20,254,label,17)
    b+=bird('robin',1038,125,3)
    return ("The developer's nest",'Editable technology signs. Only explicitly configured technologies are shown.',b,320)

def exploration(config):
    b=section_header('04 / A FEW PLACES TO EXPLORE','THE EXPLORATION MAP','Small ideas. Open paths. Room to grow.',300)
    b+=path('M0 284h1200v16H0z','sage')
    b+=path('M48 250h220v-12h180v24h180v-12h240v-12h284','none',f'stroke="{color("sand")}" stroke-width="12" stroke-dasharray="12 12"')
    for i,x in enumerate([174,572,970]):
        b+=rect(x,192,8,92,'brown')+rect(x-32,176,88,40,'forest')+text(x+12,204,f'0{i+1}',20,'cream','middle')
    b+=pine(72,170,.7)+pine(1116,162,.8)+flowers(760,260,.6)
    b+=bird('robin',384,233,3)
    return ('The exploration map','A dotted walking trail links three numbered project destinations. Repository links are in the text below the image.',b,300)

def garden(data):
    b=section_header('02 / EVERY SMALL STEP COUNTS','THE CONTRIBUTION GARDEN','Real days. Real progress. A little more green.',452)
    b+=rect(44,160,1112,210,'sky')+rect(44,366,1112,8,'sand')
    if data:
        days=data['days'];first=__import__('datetime').date.fromisoformat(days[0]['date'])
        offset=(first.weekday()+1)%7
        ncols=(offset+len(days)+6)//7
        step=min(19,1004/ncols);size=step-4;x0=116;y0=192
        previous_month=None
        level_colors=['mist','sage','pine','forest','deep']
        for i,day in enumerate(days):
            d=__import__('datetime').date.fromisoformat(day['date']);position=offset+i
            col=position//7;row=position%7;x=x0+col*step;y=y0+row*22
            if d.month!=previous_month:
                if col < ncols-2:b+=text(x,y0-12,d.strftime('%b'),13,'pine')
                previous_month=d.month
            b+=f'<g><title>{day["date"]}: {day["count"]} contributions</title>'
            b+=rect(round(x,2),y,round(size,2),18,level_colors[day['level']])
            # Each day remains a distinct cell; growth icon is contained in it.
            if day['level']>0:
                b+=rect(round(x+size/2-1,2),y+8,2,8,'mint')
                b+=rect(round(x+size/2-5,2),y+8,4,3,'mint')
            if day['level']>=2:b+=rect(round(x+size/2+1,2),y+5,4,3,'mint')
            if day['level']>=3:b+=rect(round(x+size/2-3,2),y+2,6,4,'gold')
            b+='</g>'
        for yy,label in [(1,'M'),(3,'W'),(5,'F')]:b+=text(80,y0+yy*22+14,label,13,'pine')
        b+=text(48,411,f'{data["total_contributions"]:,} CONTRIBUTIONS',17)
        b+=text(48,438,f'{days[0]["date"]} — {days[-1]["date"]} · updated {data["updated_at"][:10]} UTC',13,'pine')
        b+=text(850,413,'LESS',12,'pine')
        for i,c in enumerate(level_colors):b+=rect(900+i*26,398,18,18,c)
        b+=text(1040,413,'MORE',12,'pine')
    else:
        b+=pixel_text('Ready to grow',600,218,4,'ink',True)
        b+=text(600,290,'Your real GitHub activity will take root here.',21,anchor='middle')
        b+=text(600,328,'AWAITING THE FIRST DATA UPDATE · NO ACTIVITY DATA LOADED',13,'pine','middle')
        b+=text(48,420,'ONE DAY = ONE PLOT. INTENSITY = GROWTH.',14,'pine',extra='letter-spacing="1"')
    b+=bird('robin',1080,110,3)+flowers(1116,332,.5)
    b+=bird('hummingbird',14,314,2)
    return ('The contribution garden','GitHub contribution calendar: one day per cell, Sunday at the top, oldest week on the left. Intensity comes directly from GitHub. '+('Live API snapshot.' if data else 'Waiting for GitHub data; no contribution numbers have been invented.'),b,452)

def stats(data):
    b=rect(0,0,1200,312,'deep')
    b+=text(40,40,'FIELD OBSERVATIONS / GITHUB',15,'mint',extra='letter-spacing="2"')
    labels=['CONTRIBUTIONS','PUBLIC REPOS','ACTIVE DAYS']
    values=[data['total_contributions'],data['public_repositories'],sum(d['count']>0 for d in data['days'])] if data else ['—']*3
    for i,(label,value) in enumerate(zip(labels,values)):
        x=40+i*270
        b+=text(x,112,f'{value:,}' if isinstance(value,int) else value,44,'cream')
        b+=text(x,146,label,14,'mint',extra='letter-spacing="1"')
    b+=rect(40,178,800,2,'forest')
    if data:
        langs=data['primary_languages'];top=sorted(langs.items(),key=lambda t:(-t[1],t[0]))[:3]
        b+=text(40,216,'PRIMARY LANGUAGES / PUBLIC NON-FORK REPOSITORIES',13,'sage')
        if not top:b+=text(40,256,'No primary-language data available.',18,'cream')
        for i,(name,count) in enumerate(top):
            x=40+i*270
            b+=rect(x,238,4,32,['gold','blue','rose'][i])+text(x+16,251,name[:18],18,'cream')
            b+=text(x+16,277,f'{count} '+('repository' if count==1 else 'repositories'),13,'mint')
    else:
        b+=text(40,220,'No GitHub snapshot yet.',20,'cream')
        b+=text(40,260,'Numbers appear after the first successful update.',16,'mint')
    b+=rect(952,210,152,8,'brown')+rect(1024,218,8,94,'brown')+bird('owl',978,110,5)
    b+=rect(1120,56,4,4,'sand')+rect(932,76,4,4,'sand')
    return ('Field observations — GitHub statistics','Genuine GitHub metrics. Contributions and active days use the displayed calendar period. Public repository total includes forks. Primary language counts use all owned public non-fork repositories, not skill ratings.',b,312)

def footer(config):
    b=coast(True)
    b+=text(600,76,'THE TRAIL CONTINUES',15,'sand','middle',extra='letter-spacing="4"')
    b+=text(600,152,'Always learning. Always building. Always exploring.',25,'cream','middle')
    b+=pixel_text(config['name'],600,200,5,'cream',True)
    b+=group('<g class="fly-near">'+bird('seagull',0,0,2)+'</g>',0,310)
    b+=group('<g class="fly-far">'+bird('seagull',0,0,1)+'</g>',0,298)
    b+=bird('owl',34,376,4)+bird('kingfisher',978,409,3)
    b+=text(600,528,'UNTIL THE NEXT ADVENTURE.',14,'mint','middle',extra='letter-spacing="3"')
    return ('Until the next adventure — Martin Lema','A quiet pixel sunset over the sea. Gulls cross layered mountains, waves move gently, an owl blinks, and a kingfisher waits by the water. Always learning. Always building. Always exploring.',b,560)
