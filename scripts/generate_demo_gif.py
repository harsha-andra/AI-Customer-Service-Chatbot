"""
Rich animated demo GIF v3 — AI Customer Service Chatbot
Shows 4 separate use-case conversations with scene titles:
  1. Appointment Booking
  2. Order Tracking / Complaint
  3. Technical Support
  4. Billing Enquiry
Each scene fades in with a title card, then plays out naturally.
"""

from PIL import Image, ImageDraw, ImageFont
import os, random, math

# ── Canvas ─────────────────────────────────────────────────────
W, H   = 640, 820
SCALE  = 2
SW, SH = W*SCALE, H*SCALE

# ── Palette ────────────────────────────────────────────────────
BG       = (10, 12, 17)
SURFACE  = (19, 22, 30)
SURFACE2 = (27, 31, 44)
BORDER   = (38, 44, 60)
ACCENT   = (88, 138, 240)
WHITE    = (225, 230, 245)
MUTED    = (95, 104, 122)
GREEN    = (34, 197, 94)
AMBER    = (251, 191, 36)
RED_C    = (239, 68, 68)
TEAL     = (20, 184, 166)
USER_A   = (68, 108, 215)
USER_B   = (105, 52, 210)
BOT_BG   = SURFACE2
CHIP_BG  = (24, 28, 40)
CHIP_BOR = (46, 53, 72)
SCENE_BG = (14, 16, 22)

def lerp(a, b, t):
    return tuple(max(0,min(255, int(a[i]+(b[i]-a[i])*t))) for i in range(3))

# ── Fonts ───────────────────────────────────────────────────────
def font(size, bold=False):
    s = "-Bold" if bold else ""
    for p in [
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{s}.ttf",
        f"/usr/share/fonts/truetype/liberation/LiberationSans{s if bold else '-Regular'}.ttf",
    ]:
        try: return ImageFont.truetype(p, size*SCALE)
        except: pass
    return ImageFont.load_default()

F_XS  = font(10);  F_SM  = font(11);  F_MD  = font(13)
F_MDB = font(13,1);F_LG  = font(15,1);F_XL  = font(18,1);F_XXL = font(22,1)

def rr(d, xy, r, fill=None, outline=None, w=2):
    d.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=w)

def wrap(text, f, max_w, d):
    words=text.split(); lines,line=[],""
    for word in words:
        t=(line+" "+word).strip()
        if d.textlength(t,font=f)<=max_w: line=t
        else:
            if line: lines.append(line)
            line=word
    if line: lines.append(line)
    return lines

def downscale(img):
    return img.resize((W,H), Image.LANCZOS)

# ── Header builder ──────────────────────────────────────────────
def draw_header(d, provider="ollama", status_col=GREEN, status_txt="Online · Powered by AI"):
    s = SCALE
    rr(d, (0,0,SW,76*s), 0, fill=SURFACE)
    d.rectangle((0,74*s,SW,76*s), fill=BORDER)
    # avatar gradient
    for xi in range(14*s, 58*s):
        t=(xi-14*s)/max(44*s,1)
        d.rectangle((xi,13*s,xi,57*s), fill=lerp(USER_A,USER_B,t))
    rr(d,(14*s,13*s,58*s,57*s),13*s,outline=lerp(USER_A,USER_B,0.4),w=s)
    # "AI" text in avatar
    aw=int(d.textlength("AI",font=F_LG))
    d.text(((14*s+58*s-aw)//2, 24*s), "AI", font=F_LG, fill=WHITE)
    # name
    d.text((66*s,14*s), "Aria  —  AI Customer Assistant", font=F_LG, fill=WHITE)
    # status
    d.ellipse((66*s,42*s,76*s,52*s), fill=status_col)
    d.text((82*s,41*s), status_txt, font=F_XS, fill=MUTED)
    # badge
    bw=int(d.textlength(provider,font=F_XS))+22*s
    rr(d,(SW-bw-14*s,24*s,SW-14*s,48*s),10*s,fill=(16,24,46),outline=(44,72,128),w=s)
    d.text((SW-bw-2*s,31*s), provider, font=F_XS, fill=ACCENT)

# ── Scene title card ────────────────────────────────────────────
def make_title_card(emoji, title, subtitle, alpha=255):
    img = Image.new("RGB",(SW,SH),SCENE_BG)
    d   = ImageDraw.Draw(img)
    # subtle grid lines
    for y in range(0,SH,40*SCALE):
        d.line((0,y,SW,y),fill=(20,24,34),width=1)
    for x in range(0,SW,40*SCALE):
        d.line((x,0,x,SH),fill=(20,24,34),width=1)
    # glow blob
    for r in range(120*SCALE,0,-4*SCALE):
        a = int(18*(r/(120*SCALE)))
        col = lerp(BG, ACCENT, a/255)
        d.ellipse((SW//2-r,SH//2-r,SW//2+r,SH//2+r),fill=col)
    # emoji
    ew=int(d.textlength(emoji,font=F_XXL))
    d.text(((SW-ew)//2, SH//2-110*SCALE), emoji, font=F_XXL, fill=WHITE)
    # title
    tw=int(d.textlength(title,font=F_XL))
    d.text(((SW-tw)//2, SH//2-48*SCALE), title, font=F_XL, fill=WHITE)
    # subtitle
    sw2=int(d.textlength(subtitle,font=F_MD))
    d.text(((SW-sw2)//2, SH//2+8*SCALE), subtitle, font=F_MD, fill=MUTED)
    # fade overlay
    if alpha < 255:
        overlay=Image.new("RGB",(SW,SH),SCENE_BG)
        img=Image.blend(img,overlay,1-alpha/255)
    return downscale(img)

# ── Main frame builder ──────────────────────────────────────────
def make_frame(messages, typing=False, input_text="", cursor=False,
               chips=None, provider="ollama", scroll_off=0,
               status_col=GREEN, status_txt="Online · Powered by AI",
               highlight_chip=None):
    img = Image.new("RGB",(SW,SH),BG)
    d   = ImageDraw.Draw(img)
    s   = SCALE

    # bg gradient
    for y in range(200*s):
        t=1-(y/(200*s))
        d.rectangle((0,y,SW,y+1),fill=lerp(BG,lerp(BG,SURFACE,0.5),t*0.4))

    draw_header(d, provider, status_col, status_txt)

    # messages
    PAD   = 18*s
    MAX_BW= int(SW*0.70)
    y     = (84-scroll_off)*s

    for role,text,ts,tag in messages:
        lines=wrap(text,F_MD,MAX_BW-28*s,d)
        lh=19*s
        bw=max((int(d.textlength(l,font=F_MD)) for l in lines),default=60*s)+30*s
        bw=min(bw,MAX_BW)
        th=14*s
        bh=len(lines)*lh+22*s+(th if ts else 0)

        if role=="user":
            bx=SW-PAD-bw
            for xi in range(bx,bx+bw):
                t2=(xi-bx)/max(bw,1)
                d.rectangle((xi,y,xi,y+bh),fill=lerp(USER_A,USER_B,t2))
            rr(d,(bx,y,bx+bw,y+bh),14*s,outline=lerp(USER_A,USER_B,0.3),w=s)
            for i,line in enumerate(lines):
                d.text((bx+14*s,y+11*s+i*lh),line,font=F_MD,fill=WHITE)
            if ts:
                tw2=int(d.textlength(ts,font=F_XS))
                d.text((bx+bw-tw2-10*s,y+bh-13*s),ts,font=F_XS,fill=(185,200,255))
        else:
            bx=PAD
            # tag badge (e.g. "RESOLVED", "ESCALATED")
            tag_h=0
            if tag:
                tag_cols={"✅ Resolved":(20,80,40),"⚠️ Escalated":(80,40,10),"🔵 Info":(20,40,90)}
                tc=tag_cols.get(tag,(30,30,50))
                tw3=int(d.textlength(tag,font=F_XS))+16*s
                rr(d,(bx,y,bx+tw3,y+20*s),6*s,fill=tc,outline=None,w=0)
                d.text((bx+8*s,y+4*s),tag,font=F_XS,fill=WHITE)
                y+=24*s; tag_h=24*s
            rr(d,(bx,y,bx+bw,y+bh),14*s,fill=BOT_BG,outline=BORDER,w=s)
            for i,line in enumerate(lines):
                d.text((bx+14*s,y+11*s+i*lh),line,font=F_MD,fill=WHITE)
            if ts:
                d.text((bx+14*s,y+bh-13*s),ts,font=F_XS,fill=MUTED)
        y+=bh+10*s

    # typing indicator
    if typing:
        bx=PAD
        rr(d,(bx,y,bx+72*s,y+40*s),14*s,fill=BOT_BG,outline=BORDER,w=s)
        for i,dx in enumerate([14,28,42]):
            d.ellipse((bx+dx*s,y+14*s,bx+dx*s+9*s,y+23*s),fill=MUTED)
        y+=50*s

    # chips
    if chips:
        cx=PAD; cy=y+8*s
        for chip in chips:
            cw=int(d.textlength(chip,font=F_XS))+26*s
            if cx+cw>SW-PAD: cx=PAD; cy+=34*s
            is_hl = (chip==highlight_chip)
            bg_c = lerp(CHIP_BG,ACCENT,0.2) if is_hl else CHIP_BG
            bo_c = ACCENT if is_hl else CHIP_BOR
            rr(d,(cx,cy,cx+cw,cy+27*s),13*s,fill=bg_c,outline=bo_c,w=s)
            fc = WHITE if is_hl else WHITE
            d.text((cx+13*s,cy+7*s),chip,font=F_XS,fill=fc)
            cx+=cw+9*s

    # input bar
    iy=H-70
    rr(d,(14*s,iy*s,(W-14)*s,(H-26)*s),22*s,fill=SURFACE2,outline=BORDER,w=s)
    txt=input_text+("|" if cursor else "") if input_text else ""
    if txt:
        d.text((30*s,(iy+10)*s),txt,font=F_MD,fill=WHITE)
    else:
        d.text((30*s,(iy+10)*s),"Type your message…",font=F_MD,fill=MUTED)
    sbx,sby=W-60,iy+2
    for xi in range(sbx*s,(sbx+40)*s):
        t2=(xi-sbx*s)/max(40*s,1)
        d.rectangle((xi,sby*s,xi,(sby+38)*s),fill=lerp(USER_A,USER_B,t2))
    rr(d,(sbx*s,sby*s,(sbx+40)*s,(sby+38)*s),13*s,outline=lerp(USER_A,USER_B,0.3),w=s)
    d.text(((sbx+11)*s,(sby+9)*s),"➤",font=F_SM,fill=WHITE)

    # footer
    hint="AI can make mistakes · verify important info"
    hw=int(d.textlength(hint,font=F_XS))
    d.text(((SW-hw)//2,(H-17)*s),hint,font=F_XS,fill=(50,57,72))

    return downscale(img)

# ── Frame helpers ───────────────────────────────────────────────
frames,durations=[],[]
def add(f,ms): frames.append(f); durations.append(ms)
def hold(f,ms,n=1): [add(f,ms) for _ in range(n)]
random.seed(99)

def type_msg(conv, text, fargs):
    for i in range(len(text)+1):
        add(make_frame(conv,input_text=text[:i],cursor=i%2==0,**fargs), random.randint(45,95))

def bot_typing(conv, fargs, n=5):
    hold(make_frame(conv,typing=True,**fargs), 260, n)

CHIPS_ALL = [
    "📅 Book appointment","🕐 Opening hours","📦 Track order",
    "💳 Billing query","🔧 Tech support","🔄 Return / Refund",
    "📞 Request callback","🏷️ Services & pricing","⚠️ File complaint",
    "📍 Find location","❌ Cancel subscription","👤 Human agent",
]

# ═══════════════════════════════════════════════════════════════
# SCENE 0 — Welcome
# ═══════════════════════════════════════════════════════════════
W0=[("bot","Hi! I'm Aria 👋 Your AI assistant is ready. Choose a topic or just type your question below.","09:41","")]
FA=dict(chips=CHIPS_ALL,provider="ollama")
hold(make_frame(W0,**FA), 600, 9)

# ═══════════════════════════════════════════════════════════════
# SCENE 1 — Appointment Booking
# ═══════════════════════════════════════════════════════════════
for alpha in range(0,256,32): hold(make_title_card("📅","Appointment Booking","Booking a service slot",alpha),60)
hold(make_title_card("📅","Appointment Booking","Booking a service slot"),400,4)
for alpha in range(255,-1,-32): hold(make_title_card("📅","Appointment Booking","Booking a service slot",alpha),55)

c1=[("bot","Hi! I'm Aria 👋 Your AI assistant is ready. How can I help you today?","09:41","")]
FA1=dict(provider="ollama")
hold(make_frame(c1,**FA1),500,5)

t1a="I need to book a dental appointment for next Monday"
type_msg(c1,t1a,FA1)
c1+=[("user",t1a,"09:42","")]
hold(make_frame(c1,**FA1),120,2)
bot_typing(c1,FA1)
c1+=[("bot","Sure! I have these slots available next Monday:\n• 10:00 AM  • 1:30 PM  • 4:00 PM\nWhich works best for you?","09:42","")]
hold(make_frame(c1,**FA1),650,8)

t1b="1:30 PM please. My name is Jordan Lee."
type_msg(c1,t1b,FA1)
c1+=[("user",t1b,"09:43","")]
bot_typing(c1,FA1)
c1+=[("bot","✅ Booked! Monday 1:30 PM for Jordan Lee.\nConfirmation sent to your email. Reply here to reschedule anytime.","09:43","✅ Resolved")]
hold(make_frame(c1,**FA1),700,9)

# ═══════════════════════════════════════════════════════════════
# SCENE 2 — Order Tracking + Complaint
# ═══════════════════════════════════════════════════════════════
for alpha in range(0,256,32): hold(make_title_card("📦","Order Tracking","Track orders & handle complaints",alpha),60)
hold(make_title_card("📦","Order Tracking","Track orders & handle complaints"),400,4)
for alpha in range(255,-1,-32): hold(make_title_card("📦","Order Tracking","Track orders & handle complaints",alpha),55)

c2=[("bot","Hi! I'm Aria 👋 How can I help you today?","10:02","")]
FA2=dict(provider="openai")
hold(make_frame(c2,**FA2),500,5)

t2a="Where is my order? It was supposed to arrive 3 days ago."
type_msg(c2,t2a,FA2)
c2+=[("user",t2a,"10:03","")]
bot_typing(c2,FA2)
c2+=[("bot","I'm sorry to hear that! Could you share your order number so I can look it up right away?","10:03","")]
hold(make_frame(c2,**FA2),600,7)

t2b="Order #ORD-88421"
type_msg(c2,t2b,FA2)
c2+=[("user",t2b,"10:03","")]
bot_typing(c2,FA2,6)
c2+=[("bot","Found it! Order #ORD-88421 is with the courier and shows delayed due to weather.\nExpected delivery: tomorrow by 8 PM.","10:04","🔵 Info")]
hold(make_frame(c2,**FA2),650,8)

t2c="That's unacceptable, I needed it today. I want a refund."
type_msg(c2,t2c,FA2)
c2+=[("user",t2c,"10:04","")]
bot_typing(c2,FA2)
c2+=[("bot","I completely understand your frustration. I've flagged this as urgent and raised a refund request (Ref: REF-2041).\nOur team will contact you within 2 hours. Apologies for the inconvenience!","10:05","⚠️ Escalated")]
hold(make_frame(c2,**FA2,scroll_off=60),700,9)

# ═══════════════════════════════════════════════════════════════
# SCENE 3 — Technical Support
# ═══════════════════════════════════════════════════════════════
for alpha in range(0,256,32): hold(make_title_card("🔧","Technical Support","Diagnosing & resolving issues",alpha),60)
hold(make_title_card("🔧","Technical Support","Diagnosing & resolving issues"),400,4)
for alpha in range(255,-1,-32): hold(make_title_card("🔧","Technical Support","Diagnosing & resolving issues",alpha),55)

c3=[("bot","Hi! I'm Aria 👋 What can I help you with today?","14:17","")]
FA3=dict(provider="anthropic")
hold(make_frame(c3,**FA3),500,5)

t3a="My app keeps crashing when I open the dashboard"
type_msg(c3,t3a,FA3)
c3+=[("user",t3a,"14:18","")]
bot_typing(c3,FA3)
c3+=[("bot","I'm sorry about that! Let's fix it quickly.\nCould you tell me:\n1. Which device & OS are you on?\n2. App version number?","14:18","")]
hold(make_frame(c3,**FA3),620,7)

t3b="iPhone 15, iOS 17.4, app version 3.2.1"
type_msg(c3,t3b,FA3)
c3+=[("user",t3b,"14:19","")]
bot_typing(c3,FA3,6)
c3+=[("bot","Thanks! There's a known bug in v3.2.1 on iOS 17.4.\nFix: go to Settings → Clear Cache → Restart app.\nIf that doesn't work, update to v3.2.2 from the App Store.","14:19","")]
hold(make_frame(c3,**FA3),660,8)

t3c="Clearing cache fixed it! Thanks Aria 🙌"
type_msg(c3,t3c,FA3)
c3+=[("user",t3c,"14:21","")]
bot_typing(c3,FA3)
c3+=[("bot","Brilliant! Glad that sorted it 🎉\nIf the issue comes back after updating, feel free to message again. Have a great day!","14:21","✅ Resolved")]
hold(make_frame(c3,**FA3,scroll_off=55),700,9)

# ═══════════════════════════════════════════════════════════════
# SCENE 4 — Billing Enquiry
# ═══════════════════════════════════════════════════════════════
for alpha in range(0,256,32): hold(make_title_card("💳","Billing Enquiry","Handling payments & subscriptions",alpha),60)
hold(make_title_card("💳","Billing Enquiry","Handling payments & subscriptions"),400,4)
for alpha in range(255,-1,-32): hold(make_title_card("💳","Billing Enquiry","Handling payments & subscriptions",alpha),55)

c4=[("bot","Hi! I'm Aria 👋 How can I assist you today?","16:55","")]
FA4=dict(provider="ibm watson")
hold(make_frame(c4,**FA4),500,5)

t4a="I was charged twice this month on my credit card"
type_msg(c4,t4a,FA4)
c4+=[("user",t4a,"16:56","")]
bot_typing(c4,FA4)
c4+=[("bot","That's definitely not right — I'm sorry! Could you confirm the email on your account so I can verify the charges?","16:56","")]
hold(make_frame(c4,**FA4),600,7)

t4b="alex@gmail.com"
type_msg(c4,t4b,FA4)
c4+=[("user",t4b,"16:56","")]
bot_typing(c4,FA4,7)
c4+=[("bot","Found it. I can see two charges of $29.99 on March 3rd — this is a duplicate.\nI've initiated a full refund of $29.99. It'll appear in 3–5 business days.","16:57","✅ Resolved")]
hold(make_frame(c4,**FA4),650,8)

t4c="Perfect, thank you! Can I also cancel my subscription?"
type_msg(c4,t4c,FA4)
c4+=[("user",t4c,"16:58","")]
bot_typing(c4,FA4)
c4+=[("bot","Of course. Your subscription has been cancelled effective end of current billing period (March 31).\nYou'll keep full access until then. Sorry to see you go! 💙","16:58","")]
hold(make_frame(c4,**FA4,scroll_off=70),750,10)

# ═══════════════════════════════════════════════════════════════
# OUTRO — Loop back to welcome
# ═══════════════════════════════════════════════════════════════
for alpha in range(0,256,30): hold(make_title_card("🤖","Aria — AI Assistant","Business-independent · 6 cloud providers",alpha),55)
hold(make_title_card("🤖","Aria — AI Assistant","Business-independent · 6 cloud providers"),600,8)
for alpha in range(255,-1,-30): hold(make_title_card("🤖","Aria — AI Assistant","Business-independent · 6 cloud providers",alpha),55)

hold(make_frame(W0,**FA),700,6)

# ── Save ──────────────────────────────────────────────────────
os.makedirs("/home/claude/chatbot-v3/docs", exist_ok=True)
out="/home/claude/chatbot-v3/docs/demo.gif"
frames[0].save(out,save_all=True,append_images=frames[1:],
               duration=durations,loop=0,optimize=True)
print(f"✅  {len(frames)} frames · {os.path.getsize(out)//1024} KB → {out}")
