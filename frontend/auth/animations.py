"""animations.py — CSS & HTML constants for the ClinicalAI premium login page."""

LOGIN_ANIMATIONS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&family=Fraunces:ital,wght@0,600;1,300&display=swap');

[data-testid="stSidebar"],[data-testid="collapsedControl"],header{display:none!important;}
.block-container{padding:0!important;max-width:100%!important;}
html,body,.stApp{background:transparent!important;font-family:'DM Sans',sans-serif!important;}
.stApp.login-active{overflow:hidden!important;}

.clinicalai-bg{position:fixed;inset:0;z-index:-2;pointer-events:none;
  background:linear-gradient(135deg,#050e1a 0%,#071828 30%,#0a2030 60%,#06141f 100%);
  overflow:hidden;}
.clinicalai-bg::before{content:'';position:absolute;top:-20%;left:-10%;width:65vw;height:65vw;border-radius:50%;
  background:radial-gradient(circle,rgba(0,200,180,.09) 0%,rgba(10,107,114,.06) 40%,transparent 70%);
  animation:orb1 18s ease-in-out infinite alternate;}
.clinicalai-bg::after{content:'';position:absolute;bottom:-20%;right:-10%;width:55vw;height:55vw;border-radius:50%;
  background:radial-gradient(circle,rgba(37,99,235,.1) 0%,rgba(26,63,111,.07) 40%,transparent 70%);
  animation:orb2 22s ease-in-out infinite alternate;}

.bg-grid{position:fixed;inset:0;z-index:-1;pointer-events:none;
  background-image:linear-gradient(rgba(0,200,180,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(0,200,180,.04) 1px,transparent 1px);
  background-size:48px 48px;animation:gridfade 4s ease-in-out infinite alternate;}

.particle{position:fixed;border-radius:50%;pointer-events:none;z-index:2;animation:floatp linear infinite;}
.p1{width:4px;height:4px;background:rgba(0,220,190,.5);left:10%;top:20%;animation-duration:12s;}
.p2{width:3px;height:3px;background:rgba(37,99,235,.4);left:25%;top:70%;animation-duration:16s;animation-delay:-4s;}
.p3{width:5px;height:5px;background:rgba(0,200,180,.35);left:70%;top:15%;animation-duration:14s;animation-delay:-2s;}
.p4{width:3px;height:3px;background:rgba(99,179,237,.45);left:85%;top:55%;animation-duration:18s;animation-delay:-6s;}
.p5{width:4px;height:4px;background:rgba(0,220,190,.3);left:50%;top:85%;animation-duration:11s;animation-delay:-1s;}
.p6{width:2px;height:2px;background:rgba(37,99,235,.5);left:38%;top:42%;animation-duration:20s;animation-delay:-8s;}
.p7{width:5px;height:5px;background:rgba(0,180,170,.25);left:62%;top:30%;animation-duration:15s;animation-delay:-3s;}
.p8{width:3px;height:3px;background:rgba(147,197,253,.4);left:18%;top:88%;animation-duration:13s;animation-delay:-5s;}

.neural-node{position:fixed;border-radius:50%;pointer-events:none;z-index:2;}
.nn1{width:10px;height:10px;left:15%;top:30%;background:rgba(0,220,190,.6);box-shadow:0 0 20px 6px rgba(0,220,190,.2);animation:neuralpulse 4s ease-in-out infinite;}
.nn2{width:8px;height:8px;left:80%;top:20%;background:rgba(37,99,235,.5);box-shadow:0 0 18px 5px rgba(37,99,235,.15);animation:neuralpulse 5s ease-in-out infinite 1.2s;}
.nn3{width:6px;height:6px;left:60%;top:75%;background:rgba(0,200,180,.5);box-shadow:0 0 14px 4px rgba(0,200,180,.15);animation:neuralpulse 3.5s ease-in-out infinite .7s;}
.nn4{width:9px;height:9px;left:35%;top:60%;background:rgba(99,179,237,.4);box-shadow:0 0 16px 5px rgba(99,179,237,.12);animation:neuralpulse 6s ease-in-out infinite 2s;}

.ecg-container{position:fixed;bottom:80px;left:3%;width:42%;z-index:3;opacity:.4;pointer-events:none;}

.login-root{position:relative;z-index:10;display:flex;min-height:100vh;align-items:center;
  justify-content:center;gap:3rem;padding:2rem 4vw;}

.hero-panel{flex:1;max-width:480px;color:#fff;animation:fadeup .8s ease-out both;}
.brand-logo{width:72px;height:72px;background:linear-gradient(135deg,#00c8b4 0%,#1a3f6f 100%);
  border-radius:22px;display:flex;align-items:center;justify-content:center;font-size:2.2rem;
  margin-bottom:1.8rem;box-shadow:0 8px 32px rgba(0,200,180,.35);animation:logoglow 3s ease-in-out infinite alternate;}
.hero-eyebrow{font-family:'DM Mono',monospace;font-size:.68rem;letter-spacing:.2em;text-transform:uppercase;
  color:#00c8b4;margin-bottom:.8rem;opacity:.85;}
.hero-headline{font-family:'Fraunces',serif;font-size:clamp(2rem,3.5vw,3rem);font-weight:600;
  line-height:1.15;color:#fff;margin-bottom:1rem;letter-spacing:-.02em;}
.hero-headline span{background:linear-gradient(135deg,#00e5cc,#00a8f3);-webkit-background-clip:text;
  -webkit-text-fill-color:transparent;background-clip:text;}
.hero-desc{font-size:.92rem;color:rgba(176,210,230,.65);line-height:1.7;max-width:380px;margin-bottom:2.5rem;}

.trust-grid{display:grid;grid-template-columns:1fr 1fr;gap:.75rem;margin-bottom:2rem;}
.trust-badge{display:flex;align-items:center;gap:.6rem;background:rgba(255,255,255,.04);
  border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:.7rem .9rem;
  font-size:.78rem;color:rgba(200,230,240,.8);transition:all .25s;animation:fadeup .8s ease-out both;}
.trust-badge:nth-child(2){animation-delay:.1s;}
.trust-badge:nth-child(3){animation-delay:.2s;}
.trust-badge:nth-child(4){animation-delay:.3s;}
.trust-badge:hover{background:rgba(0,200,180,.08);border-color:rgba(0,200,180,.2);}
.trust-icon{width:28px;height:28px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:.95rem;flex-shrink:0;}
.trust-label{font-weight:600;font-size:.75rem;line-height:1.2;}
.trust-sub{font-size:.65rem;color:rgba(150,190,210,.6);margin-top:.1rem;}

.ai-status{display:inline-flex;align-items:center;gap:.5rem;background:rgba(0,200,180,.08);
  border:1px solid rgba(0,200,180,.2);border-radius:99px;padding:.4rem 1rem;
  font-family:'DM Mono',monospace;font-size:.68rem;letter-spacing:.1em;text-transform:uppercase;color:#00c8b4;}
.pulse-dot{width:8px;height:8px;border-radius:50%;background:#00e5cc;
  box-shadow:0 0 0 3px rgba(0,229,204,.2);animation:pulsering 1.8s ease-in-out infinite;}

.auth-card{width:100%;max-width:480px;background:rgba(255,255,255,.07);backdrop-filter:blur(28px);
  -webkit-backdrop-filter:blur(28px);border:1px solid rgba(255,255,255,.15);border-radius:28px;
  padding:2.8rem 2.5rem;box-shadow:0 32px 64px rgba(0,0,0,.4),0 0 0 1px rgba(0,200,180,.06),
  inset 0 1px 0 rgba(255,255,255,.1);animation:fadeup .8s ease-out .2s both;}
.auth-card-header{text-align:center;margin-bottom:1.8rem;}
.auth-card-title{font-family:'Fraunces',serif;font-size:1.65rem;font-weight:600;color:#f0f8ff;
  letter-spacing:-.02em;margin-bottom:.4rem;}
.auth-card-sub{font-size:.84rem;color:rgba(176,210,230,.55);}

.stTextInput>label,.stNumberInput>label{font-family:'DM Sans',sans-serif!important;font-size:.75rem!important;
  font-weight:600!important;text-transform:uppercase!important;letter-spacing:.08em!important;
  color:rgba(176,210,230,.6)!important;margin-bottom:.3rem!important;}
.stTextInput>div>div>input,.stNumberInput>div>div>input{background:rgba(255,255,255,.06)!important;
  border:1.5px solid rgba(255,255,255,.12)!important;border-radius:12px!important;color:#f0f8ff!important;
  font-family:'DM Sans',sans-serif!important;font-size:.92rem!important;padding:.65rem 1rem!important;
  transition:border-color .2s,box-shadow .2s!important;caret-color:#00c8b4!important;}
.stTextInput>div>div>input:focus{border-color:rgba(0,200,180,.5)!important;
  box-shadow:0 0 0 3px rgba(0,200,180,.1)!important;background:rgba(0,200,180,.05)!important;}
.stTextInput>div>div>input::placeholder{color:rgba(176,210,230,.3)!important;font-style:italic;}

.stButton>button,[data-testid="stFormSubmitButton"]>button{
  background:linear-gradient(135deg,#0a6b72 0%,#1a3f6f 100%)!important;
  color:#fff!important;border:none!important;border-radius:14px!important;
  padding:.8rem 2rem!important;font-family:'DM Sans',sans-serif!important;font-weight:700!important;
  font-size:.9rem!important;letter-spacing:.05em!important;transition:all .25s ease!important;
  box-shadow:0 4px 18px rgba(0,200,180,.3)!important;text-transform:uppercase!important;}
.stButton>button:hover,[data-testid="stFormSubmitButton"]>button:hover{
  filter:brightness(1.15)!important;box-shadow:0 8px 28px rgba(0,200,180,.45)!important;
  transform:translateY(-2px)!important;}
.stButton>button:active,[data-testid="stFormSubmitButton"]>button:active{transform:translateY(0)!important;}

.stForm{border:none!important;padding:0!important;}
[data-testid="stAlert"]{border-radius:12px!important;}

.auth-security-bar{display:flex;align-items:center;justify-content:center;gap:1.2rem;margin-top:1.6rem;
  padding-top:1.2rem;border-top:1px solid rgba(255,255,255,.07);font-family:'DM Mono',monospace;
  font-size:.62rem;letter-spacing:.08em;text-transform:uppercase;color:rgba(150,190,210,.4);}
.auth-security-dot{width:4px;height:4px;border-radius:50%;background:rgba(0,200,180,.35);}

.or-divider{display:flex;align-items:center;gap:.75rem;margin:1.2rem 0;
  color:rgba(150,190,210,.35);font-size:.75rem;font-family:'DM Mono',monospace;letter-spacing:.08em;}
.or-divider::before,.or-divider::after{content:'';flex:1;height:1px;background:rgba(255,255,255,.07);}

.page-footer{position:fixed;bottom:1.2rem;left:50%;transform:translateX(-50%);z-index:20;
  font-family:'DM Mono',monospace;font-size:.62rem;letter-spacing:.1em;text-transform:uppercase;
  color:rgba(150,190,210,.3);white-space:nowrap;pointer-events:none;}

.forgot-link{text-align:right;margin-top:-.5rem;margin-bottom:.8rem;}
.forgot-link a,.forgot-link span{font-size:.75rem;color:rgba(0,200,180,.7);cursor:pointer;
  text-decoration:none;font-family:'DM Mono',monospace;letter-spacing:.04em;
  transition:color .2s;}
.forgot-link a:hover,.forgot-link span:hover{color:#00e5cc;}

.signup-prompt{text-align:center;margin-top:1rem;font-size:.78rem;color:rgba(150,190,210,.5);}
.signup-prompt span{color:rgba(0,200,180,.8);cursor:pointer;font-weight:600;margin-left:.3rem;transition:color .2s;}
.signup-prompt span:hover{color:#00e5cc;}

.role-tab-container{display:flex;background:rgba(0,0,0,.3);border-radius:14px;padding:4px;
  margin-bottom:1.8rem;gap:4px;border:1px solid rgba(255,255,255,.06);}

@keyframes orb1{from{transform:translate(0,0) scale(1);}to{transform:translate(5%,4%) scale(1.08);}}
@keyframes orb2{from{transform:translate(0,0) scale(1);}to{transform:translate(-4%,-3%) scale(1.05);}}
@keyframes gridfade{from{opacity:.5;}to{opacity:1;}}
@keyframes floatp{0%{transform:translateY(0) translateX(0);opacity:0;}10%{opacity:1;}90%{opacity:1;}100%{transform:translateY(-80px) translateX(20px);opacity:0;}}
@keyframes neuralpulse{0%,100%{transform:scale(1);opacity:.6;}50%{transform:scale(1.6);opacity:1;}}
@keyframes pulsering{0%{box-shadow:0 0 0 0 rgba(0,229,204,.4);}70%{box-shadow:0 0 0 8px rgba(0,229,204,0);}100%{box-shadow:0 0 0 0 rgba(0,229,204,0);}}
@keyframes logoglow{from{box-shadow:0 8px 32px rgba(0,200,180,.3);}to{box-shadow:0 8px 48px rgba(0,200,180,.55);}}
@keyframes fadeup{from{opacity:0;transform:translateY(24px);}to{opacity:1;transform:translateY(0);}}
@keyframes ecgmove{0%{stroke-dashoffset:1000;}100%{stroke-dashoffset:0;}}
@keyframes ecgglow{0%,100%{filter:drop-shadow(0 0 3px rgba(0,229,204,.6));}50%{filter:drop-shadow(0 0 8px rgba(0,229,204,1));}}
</style>
"""

ECG_SVG = """
<div class="ecg-container">
<svg viewBox="0 0 800 80" xmlns="http://www.w3.org/2000/svg" style="width:100%;overflow:visible;">
  <defs>
    <linearGradient id="ecggrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00c8b4" stop-opacity="0"/>
      <stop offset="30%" stop-color="#00c8b4" stop-opacity="0.8"/>
      <stop offset="70%" stop-color="#00e5cc" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#00c8b4" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <path d="M0,40 L80,40 L100,40 L110,15 L120,65 L130,5 L145,75 L158,40 L200,40
           L220,40 L230,18 L240,62 L248,8 L260,72 L272,40 L320,40
           L340,40 L352,20 L362,60 L370,10 L382,70 L394,40 L440,40
           L460,40 L472,16 L482,64 L490,6 L504,74 L516,40 L560,40
           L580,40 L592,22 L602,58 L610,12 L622,68 L634,40 L680,40
           L700,40 L712,18 L722,62 L730,8 L742,72 L754,40 L800,40"
        fill="none" stroke="url(#ecggrad)" stroke-width="2.5"
        stroke-linecap="round" stroke-linejoin="round"
        stroke-dasharray="1000" stroke-dashoffset="1000"
        style="animation:ecgmove 3s linear infinite,ecgglow 2s ease-in-out infinite;"/>
</svg>
</div>
"""

ANIMATED_BACKGROUND_HTML = """
<div class="clinicalai-bg"></div>
<div class="bg-grid"></div>
<div class="particle p1"></div><div class="particle p2"></div>
<div class="particle p3"></div><div class="particle p4"></div>
<div class="particle p5"></div><div class="particle p6"></div>
<div class="particle p7"></div><div class="particle p8"></div>
<div class="neural-node nn1"></div><div class="neural-node nn2"></div>
<div class="neural-node nn3"></div><div class="neural-node nn4"></div>
""" + ECG_SVG + """
<div class="page-footer">ClinicalAI v2.0 &nbsp;·&nbsp; HIPAA-Ready Infrastructure &nbsp;·&nbsp; TLS 1.3 Encrypted</div>
"""

def get_hero_panel_html():
    return """
<div class="hero-panel">
    <div class="brand-logo">⚕️</div>
    <div class="hero-eyebrow">⚡ AI-Powered Healthcare Platform</div>
    <div class="hero-headline">Clinical Intelligence<br/><span>Redefined.</span></div>
    <p class="hero-desc">Enterprise-grade AI decision support trusted by hospitals, clinics, and patients.
    Real-time predictive analytics — secured, private, and HIPAA-ready.</p>
    <div class="trust-grid">
        <div class="trust-badge">
            <div class="trust-icon" style="background:rgba(0,200,180,.12);color:#00c8b4;">🛡️</div>
            <div><div class="trust-label">HIPAA-Ready</div><div class="trust-sub">Compliant Architecture</div></div>
        </div>
        <div class="trust-badge">
            <div class="trust-icon" style="background:rgba(37,99,235,.12);color:#60a5fa;">🔐</div>
            <div><div class="trust-label">AES-256</div><div class="trust-sub">End-to-End Encrypted</div></div>
        </div>
        <div class="trust-badge">
            <div class="trust-icon" style="background:rgba(139,92,246,.12);color:#a78bfa;">🔑</div>
            <div><div class="trust-label">JWT Secured</div><div class="trust-sub">Token Authentication</div></div>
        </div>
        <div class="trust-badge">
            <div class="trust-icon" style="background:rgba(16,185,129,.12);color:#34d399;">🤖</div>
            <div><div class="trust-label">AI Engine</div><div class="trust-sub">All Systems Active</div></div>
        </div>
    </div>
    <div class="ai-status">
        <span class="pulse-dot"></span>
        AI Diagnostic Engine Active &nbsp;·&nbsp; 3 Models Online
    </div>
</div>
"""
