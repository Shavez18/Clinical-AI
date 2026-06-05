SIDEBAR_LOGO = """
<div style="padding: 1.5rem 0 2rem 0; display:flex; align-items:center; gap:0.9rem;">
    <div style="background: linear-gradient(135deg, #0d8c8c, #00f2ff);
                width: 48px; height: 48px; border-radius: 14px;
                display:flex; justify-content:center; align-items:center;
                font-family: 'DM Mono', monospace; color:#fff; font-weight:700; font-size:1.6rem;
                box-shadow: 0 0 20px rgba(0, 242, 255, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.2);">
        ⚕️
    </div>
    <div>
        <div style="color:#ffffff; font-family:'Fraunces', serif; font-weight:700; font-size:1.3rem; letter-spacing:0.02em; line-height:1.1; text-shadow: 0 0 10px rgba(0, 242, 255, 0.3);">ClinicalAI</div>
        <div style="color:#00f2ff; font-family:'DM Mono', monospace; font-size:0.65rem; letter-spacing:0.15em; text-transform:uppercase; margin-top:0.2rem; font-weight: 600;">Enterprise Intelligence</div>
    </div>
</div>
"""

GLOBAL_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&family=Fraunces:ital,wght@0,300;0,600;1,300&display=swap');

:root {
    --bg-base:       #050e1a;
    --bg-surface:    rgba(255, 255, 255, 0.03);
    --bg-panel:      rgba(255, 255, 255, 0.05);
    --bg-sidebar:    #020810;
    --bg-sidebar-2:  #040c18;
    
    --teal-dark:     #0d8c8c;
    --teal-mid:      #13b5b5;
    --teal-light:    #00f2ff;
    --teal-pale:     rgba(0, 242, 255, 0.1);
    
    --blue-deep:     #050e1a;
    --blue-mid:      #0a192f;
    --blue-soft:     rgba(0, 242, 255, 0.05);
    
    --text-primary:  #f0f6ff;
    --text-secondary: #b0d2e6;
    --text-muted:    #6b8aab;
    --text-inverse:  #f0f6ff;
    
    --border:        rgba(0, 242, 255, 0.15);
    --border-glow:   rgba(0, 242, 255, 0.3);
    
    --shadow-glow:   0 0 20px rgba(0, 242, 255, 0.15);
    --radius-lg:     20px;
}
</style>
"""

# ── Login page full-screen override ─────────────────────────────────────────
LOGIN_PAGE_CSS = """
<style>
html, body, .stApp {
    background: #050e1a !important;
    overflow: hidden !important;
}
#MainMenu, footer, .stDeployButton { display: none !important; }
</style>
"""

