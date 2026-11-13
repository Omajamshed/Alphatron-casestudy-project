import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCREENSHOT_DIR = Path(r"C:\Users\HP\Alphatron-casestudy-project\contractguard\docs\screenshots")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

# Artifact directory
ARTIFACT_DIR = Path(r"C:\Users\HP\.gemini\antigravity\brain\4f22ec30-693c-424f-9720-b81655ad88a4\screenshots")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

FONT_REG = "C:/Windows/Fonts/segoeui.ttf"
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_MONO = "C:/Windows/Fonts/consola.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

f_title = get_font(FONT_BOLD, 28)
f_h2 = get_font(FONT_BOLD, 20)
f_h3 = get_font(FONT_BOLD, 16)
f_body = get_font(FONT_REG, 14)
f_small = get_font(FONT_REG, 12)
f_bold_small = get_font(FONT_BOLD, 12)
f_mono = get_font(FONT_MONO, 13)

BG_COLOR = (9, 13, 26)        # #090d1a
CARD_BG = (18, 24, 46)        # #12182e
CARD_BORDER = (45, 55, 85)
TEXT_WHITE = (255, 255, 255)
TEXT_MUTED = (148, 163, 184)  # #94a3b8
TEXT_DARK_MUTED = (100, 116, 139)
ACCENT_BLUE = (99, 102, 241)  # #6366f1
ACCENT_CYAN = (6, 182, 212)   # #06b6d4
GREEN = (16, 185, 129)        # #10b981
RED = (239, 68, 68)           # #ef4444
AMBER = (245, 158, 11)        # #f59e0b

def draw_header_and_sidebar(draw, active_tab="Dashboard", contract_title="Skyline Apartments Lease Agreement"):
    # Background
    draw.rectangle([(0, 0), (1200, 750)], fill=BG_COLOR)
    
    # Sidebar
    draw.rectangle([(0, 0), (240, 750)], fill=(12, 16, 32), outline=CARD_BORDER)
    # Brand
    draw.rounded_rectangle([(20, 20), (52, 52)], radius=8, fill=ACCENT_BLUE)
    draw.text((27, 24), "CG", fill=TEXT_WHITE, font=f_h3)
    draw.text((62, 22), "ContractGuard", fill=TEXT_WHITE, font=f_h3)
    draw.text((62, 42), "AI Contract Reviewer", fill=TEXT_MUTED, font=f_small)

    tabs = [
        ("Dashboard", "Portfolio"),
        ("Upload", "Upload Contract"),
        ("Overview", "Contract Overview"),
        ("Clause Explorer", "Clause Explorer"),
        ("Ask Contract", "Ask Contract (RAG)"),
        ("Review & Negotiate", "Review & Negotiate"),
        ("Exports", "Exports & Email"),
        ("Version Compare", "Version Compare"),
        ("History & Usage", "Usage & Cost"),
    ]
    y = 80
    for tid, label in tabs:
        is_active = (tid == active_tab)
        if is_active:
            draw.rounded_rectangle([(14, y), (226, y + 36)], radius=6, fill=(35, 45, 80), outline=ACCENT_BLUE)
            draw.text((28, y + 8), label, fill=TEXT_WHITE, font=f_bold_small)
        else:
            draw.text((28, y + 8), label, fill=TEXT_MUTED, font=f_small)
        y += 42

    # Top Navbar
    draw.rectangle([(240, 0), (1200, 56)], fill=(12, 16, 32), outline=CARD_BORDER)
    draw.text((264, 18), "Active Contract:", fill=TEXT_MUTED, font=f_small)
    draw.text((365, 16), contract_title, fill=TEXT_WHITE, font=f_bold_small)
    draw.rounded_rectangle([(650, 16), (690, 38)], radius=4, fill=(40, 50, 90))
    draw.text((658, 19), "v1.0", fill=(199, 210, 254), font=f_small)
    
    # Online badge
    draw.rounded_rectangle([(1070, 14), (1175, 40)], radius=13, fill=(16, 185, 129, 40), outline=GREEN)
    draw.text((1085, 19), "● Engine Online", fill=GREEN, font=f_small)

    # Footer Disclaimer
    draw.rectangle([(240, 715), (1200, 750)], fill=(10, 14, 26), outline=CARD_BORDER)
    draw.text((260, 723), "⚖️ Legal Notice: ContractGuard is an informational analysis tool, not legal advice.", fill=TEXT_MUTED, font=f_small)
    draw.text((1010, 723), "Deterministic Rules + Grounded RAG", fill=TEXT_DARK_MUTED, font=f_small)

def save_both(img, name):
    p1 = SCREENSHOT_DIR / name
    p2 = ARTIFACT_DIR / name
    img.save(p1)
    img.save(p2)
    print(f"Saved {name}")

# ==================== 1. DASHBOARD ====================
def make_dashboard():
    img = Image.new("RGB", (1200, 750), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header_and_sidebar(draw, active_tab="Dashboard")

    # Title area
    draw.text((264, 76), "Contract Portfolio", fill=TEXT_WHITE, font=f_title)
    draw.text((264, 114), "Active agreements analyzed for risky clauses, deadline exposure, and market variance.", fill=TEXT_MUTED, font=f_body)
    
    # Upload button
    draw.rounded_rectangle([(1020, 76), (1170, 116)], radius=8, fill=ACCENT_BLUE)
    draw.text((1038, 86), "+ Upload Contract", fill=TEXT_WHITE, font=f_bold_small)

    cards = [
        ("Skyline Apartments Lease Agreement", "rental", "tenant", "78 / 100", "CRITICAL RISK", RED, "Next: Notice Due in 18 Days (2026-11-01)", "3 flagged high-risk terms (Uncapped liability, 8% rent bump)"),
        ("Apex Media Consulting MSA", "freelance", "freelancer", "65 / 100", "HIGH RISK", (249, 115, 22), "Net-90 payment terms", "Immediate IP transfer upon creation without payment"),
        ("CloudScale Senior Engineer Offer", "employment", "employee", "28 / 100", "MODERATE RISK", AMBER, "90-day probation review", "Post-employment non-compete within 25-mile radius"),
        ("Standard Office Sublease Agreement", "rental", "tenant", "15 / 100", "LOW RISK", GREEN, "Standard calendar term", "Mutual habitability obligations and 30-day notice"),
    ]

    for i, (title, c_type, role, score, sev_text, sev_col, deadline, detail) in enumerate(cards):
        col = i % 2
        row = i // 2
        x = 264 + col * 460
        y = 150 + row * 260
        
        draw.rounded_rectangle([(x, y), (x + 440, y + 235)], radius=12, fill=CARD_BG, outline=CARD_BORDER)
        
        # Type & role pill
        draw.rounded_rectangle([(x + 20, y + 16), (x + 150, y + 38)], radius=4, fill=(25, 35, 65))
        draw.text((x + 28, y + 19), f"{c_type.upper()} • {role.upper()}", fill=ACCENT_CYAN, font=f_small)

        # Title
        draw.text((x + 20, y + 48), title, fill=TEXT_WHITE, font=f_h3)
        draw.text((x + 20, y + 74), detail, fill=TEXT_MUTED, font=f_small)

        # Divider
        draw.line([(x + 20, y + 120), (x + 420, y + 120)], fill=CARD_BORDER)

        # Score & badge
        draw.text((x + 20, y + 135), "Risk Score:", fill=TEXT_MUTED, font=f_small)
        draw.text((x + 20, y + 152), score, fill=TEXT_WHITE, font=f_h2)
        
        draw.rounded_rectangle([(x + 130, y + 152), (x + 260, y + 178)], radius=6, fill=(sev_col[0]//4, sev_col[1]//4, sev_col[2]//4), outline=sev_col)
        draw.text((x + 142, y + 157), sev_text, fill=sev_col, font=f_bold_small)

        # Deadline pill
        draw.rounded_rectangle([(x + 20, y + 195), (x + 420, y + 222)], radius=4, fill=(35, 30, 20), outline=AMBER)
        draw.text((x + 30, y + 200), f"⏱️ {deadline}", fill=AMBER, font=f_small)

    save_both(img, "dashboard.png")

# ==================== 2. CONTRACT OVERVIEW ====================
def make_contract_overview():
    img = Image.new("RGB", (1200, 750), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header_and_sidebar(draw, active_tab="Overview")

    draw.text((264, 76), "Contract Overview: Skyline Apartments Lease", fill=TEXT_WHITE, font=f_title)
    draw.text((264, 114), "Deterministic financial calculations, risk scoring gauge, and timeline analysis.", fill=TEXT_MUTED, font=f_body)

    # 1. Gauge Card
    draw.rounded_rectangle([(264, 150), (510, 420)], radius=12, fill=CARD_BG, outline=CARD_BORDER)
    draw.text((325, 168), "Overall Contract Risk", fill=TEXT_WHITE, font=f_h3)
    
    # Arc Gauge
    draw.arc([(300, 205), (470, 375)], start=140, end=400, fill=CARD_BORDER, width=16)
    draw.arc([(300, 205), (470, 375)], start=140, end=350, fill=RED, width=16)
    draw.text((358, 260), "78", fill=TEXT_WHITE, font=f_title)
    draw.text((362, 295), "/ 100", fill=TEXT_MUTED, font=f_small)
    draw.rounded_rectangle([(330, 335), (445, 360)], radius=4, fill=(50, 20, 20), outline=RED)
    draw.text((342, 339), "CRITICAL RISK", fill=RED, font=f_bold_small)
    draw.text((285, 385), "Role Weights: Tenant profile", fill=TEXT_MUTED, font=f_small)

    # 2. Risk Category Breakdown
    draw.rounded_rectangle([(530, 150), (870, 420)], radius=12, fill=CARD_BG, outline=CARD_BORDER)
    draw.text((550, 168), "Risk Category Breakdown", fill=TEXT_WHITE, font=f_h3)
    draw.text((760, 172), "5 findings", fill=TEXT_MUTED, font=f_small)

    categories = [
        ("Indemnification & Liability", "CRITICAL", RED, 0.90, "Weight 2.0x"),
        ("Rent Escalation (8% per yr)", "HIGH", (249, 115, 22), 0.75, "Weight 1.5x"),
        ("Auto-Renewal & Notice (60d)", "HIGH", (249, 115, 22), 0.70, "Weight 1.3x"),
        ("Security Deposit Return (60d)", "MODERATE", AMBER, 0.45, "Weight 1.4x"),
        ("Maintenance Responsibility", "MODERATE", AMBER, 0.40, "Weight 1.3x"),
    ]

    y_bar = 205
    for cat_name, sev, col, fill_pct, wt in categories:
        draw.text((550, y_bar), cat_name, fill=TEXT_WHITE, font=f_small)
        draw.text((780, y_bar), wt, fill=TEXT_MUTED, font=f_small)
        # progress bg
        draw.rounded_rectangle([(550, y_bar + 20), (850, y_bar + 28)], radius=4, fill=(35, 42, 65))
        draw.rounded_rectangle([(550, y_bar + 20), (550 + int(300 * fill_pct), y_bar + 28)], radius=4, fill=col)
        y_bar += 42

    # 3. Financial Exposure Card
    draw.rounded_rectangle([(890, 150), (1170, 420)], radius=12, fill=CARD_BG, outline=CARD_BORDER)
    draw.text((910, 168), "Potential Exposure", fill=TEXT_WHITE, font=f_h3)
    draw.text((910, 205), "$12,750.00", fill=TEXT_WHITE, font=f_title)
    draw.text((1060, 210), "+ ∞ Uncapped", fill=RED, font=f_h3)

    draw.rounded_rectangle([(910, 250), (1150, 395)], radius=8, fill=(15, 20, 38), outline=CARD_BORDER)
    draw.text((922, 260), "🧮 How this was calculated:", fill=ACCENT_CYAN, font=f_bold_small)
    formula_lines = [
        "Deposit: $5,000 (at risk)",
        "Early Term Penalty: $7,500 (3 mos)",
        "Late Fee: $250 (10% rate)",
        "+ Uncapped indemnification liability",
        "Deterministic Python Decimal engine"
    ]
    for idx, fl in enumerate(formula_lines):
        draw.text((922, 285 + idx * 20), f"• {fl}", fill=TEXT_MUTED, font=f_small)

    # 4. Key Deadlines Timeline
    draw.rounded_rectangle([(264, 440), (1170, 695)], radius=12, fill=CARD_BG, outline=CARD_BORDER)
    draw.text((284, 458), "📅 Extracted Calendar Deadlines & Notice Windows", fill=TEXT_WHITE, font=f_h3)

    timeline = [
        ("Commencement Date", "2026-01-01", "Clause 2.1", "Standard lease start date", (40, 50, 80), TEXT_WHITE),
        ("Auto-Renewal Trap Date", "2026-11-01", "Clause 2.2", "End date (2026-12-31) - 60 days notice", (60, 25, 25), RED),
        ("Lease Expiration Date", "2026-12-31", "Clause 2.1", "Initial 12-month term expires", (40, 50, 80), TEXT_WHITE),
        ("Deposit Refund Window", "2027-03-01", "Clause 3.2", "60 days post vacating (Exceeds 30d norm!)", (50, 40, 20), AMBER),
    ]

    for idx, (label, dt, src, calc, bg_c, fg_c) in enumerate(timeline):
        x = 284 + idx * 218
        draw.rounded_rectangle([(x, 500), (x + 205, 665)], radius=8, fill=bg_c, outline=CARD_BORDER)
        draw.text((x + 12, 514), label, fill=TEXT_MUTED, font=f_small)
        draw.text((x + 12, 536), dt, fill=fg_c, font=f_h3)
        draw.rounded_rectangle([(x + 12, 568), (x + 95, 588)], radius=4, fill=(20, 25, 45))
        draw.text((x + 18, 571), src, fill=ACCENT_CYAN, font=f_small)
        draw.text((x + 12, 605), calc, fill=TEXT_MUTED, font=f_small)

    save_both(img, "contract_overview.png")

# ==================== 3. CLAUSE EXPLORER ====================
def make_clause_explorer():
    img = Image.new("RGB", (1200, 750), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header_and_sidebar(draw, active_tab="Clause Explorer")

    draw.text((264, 76), "Clause Explorer", fill=TEXT_WHITE, font=f_title)
    draw.text((264, 114), "Search and inspect every segmented clause with side-by-side plain language summaries.", fill=TEXT_MUTED, font=f_body)

    # Search Bar & Filter buttons
    draw.rounded_rectangle([(264, 150), (1170, 200)], radius=8, fill=CARD_BG, outline=CARD_BORDER)
    draw.text((284, 166), "🔍 Search clauses (e.g., liability, termination, late fee)...", fill=TEXT_DARK_MUTED, font=f_body)
    
    filters = [("All (12)", True), ("Critical (1)", False), ("High (2)", False), ("Moderate (2)", False), ("Low (7)", False)]
    fx = 760
    for fname, is_sel in filters:
        bg = ACCENT_BLUE if is_sel else (25, 32, 55)
        draw.rounded_rectangle([(fx, 160), (fx + 75, 190)], radius=4, fill=bg)
        draw.text((fx + 10, 167), fname, fill=TEXT_WHITE, font=f_small)
        fx += 82

    # Clause Card 1 (Critical)
    draw.rounded_rectangle([(264, 220), (1170, 360)], radius=10, fill=CARD_BG, outline=RED)
    draw.text((284, 235), "Clause 7.1 • Indemnification & Unlimited Liability", fill=TEXT_WHITE, font=f_h3)
    draw.rounded_rectangle([(1020, 232), (1145, 258)], radius=4, fill=(50, 15, 15), outline=RED)
    draw.text((1032, 237), "⚠️ CRITICAL RISK", fill=RED, font=f_bold_small)
    
    draw.text((284, 270), "Plain Language Explanation: Tenant assumes uncapped liability for all damages or accidents on the property.", fill=TEXT_MUTED, font=f_body)
    draw.text((284, 292), "Forced Severity Rule: Rule engine forces unlimited indemnity clauses to Critical (score 10) regardless of LLM suggestion.", fill=AMBER, font=f_small)
    draw.text((284, 324), "Original: \"Tenant agrees to indemnify and hold harmless Landlord from any and all damages occurring on the Premises with unlimited liability...\"", fill=TEXT_DARK_MUTED, font=f_mono)

    # Clause Card 2 (High)
    draw.rounded_rectangle([(264, 380), (1170, 520)], radius=10, fill=CARD_BG, outline=(249, 115, 22))
    draw.text((284, 395), "Clause 4.1 • Annual Rent Escalation", fill=TEXT_WHITE, font=f_h3)
    draw.rounded_rectangle([(1035, 392), (1145, 418)], radius=4, fill=(60, 30, 15), outline=(249, 115, 22))
    draw.text((1047, 397), "⛔ HIGH RISK", fill=(249, 115, 22), font=f_bold_small)

    draw.text((284, 430), "Plain Language Explanation: Landlord reserves the unilateral right to raise rent by 8% yearly with only 30 days notice.", fill=TEXT_MUTED, font=f_body)
    draw.text((284, 452), "Market Norm Variance: Standard statutory rent increases are capped at 3-5% with at least 60 days advance written notice.", fill=AMBER, font=f_small)
    draw.text((284, 484), "Original: \"Landlord reserves the unilateral right to increase monthly rent by 8% annually upon providing thirty (30) days notice...\"", fill=TEXT_DARK_MUTED, font=f_mono)

    # Clause Card 3 (High)
    draw.rounded_rectangle([(264, 540), (1170, 680)], radius=10, fill=CARD_BG, outline=(249, 115, 22))
    draw.text((284, 555), "Clause 2.2 • Automatic Renewal Lock-In", fill=TEXT_WHITE, font=f_h3)
    draw.rounded_rectangle([(1035, 552), (1145, 578)], radius=4, fill=(60, 30, 15), outline=(249, 115, 22))
    draw.text((1047, 557), "⛔ HIGH RISK", fill=(249, 115, 22), font=f_bold_small)

    draw.text((284, 590), "Plain Language Explanation: Lease renews for a full 1-year term unless tenant cancels 60 days before expiration (trap date).", fill=TEXT_MUTED, font=f_body)
    draw.text((284, 612), "Computed Deadline: Trap date is 2026-11-01. If missed, tenant is legally committed to an additional $30,000 rent.", fill=AMBER, font=f_small)
    draw.text((284, 644), "Original: \"Agreement shall automatically renew for successive periods of one (1) year, unless Tenant provides written notice 60 days prior...\"", fill=TEXT_DARK_MUTED, font=f_mono)

    save_both(img, "clause_explorer.png")

# ==================== 4. ASK CONTRACT RAG ====================
def make_ask_contract():
    img = Image.new("RGB", (1200, 750), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header_and_sidebar(draw, active_tab="Ask Contract")

    draw.text((264, 76), "Ask the Contract (Grounded RAG)", fill=TEXT_WHITE, font=f_title)
    draw.text((264, 114), "Every factual statement is backed by verifiable [Clause, Page] citations. Refuses out-of-scope questions.", fill=TEXT_MUTED, font=f_body)

    # Chat Container
    draw.rounded_rectangle([(264, 150), (1170, 630)], radius=12, fill=CARD_BG, outline=CARD_BORDER)

    # User Message 1
    draw.rounded_rectangle([(680, 175), (1145, 220)], radius=8, fill=ACCENT_BLUE)
    draw.text((700, 187), "Can the landlord raise my rent during the lease term?", fill=TEXT_WHITE, font=f_body)

    # Assistant Response 1
    draw.rounded_rectangle([(284, 235), (940, 370)], radius=8, fill=(25, 33, 62), outline=CARD_BORDER)
    ans1_text = [
        "Yes, but with significant conditions and risk factors:",
        "• Under Clause 4.1, the landlord claims the unilateral right to increase rent by 8% annually",
        "  with only 30 days advance notice.",
        "• However, market benchmarks and local rent stabilization norms mandate a 60-day notice",
        "  period and cap annual adjustments between 3% to 5%."
    ]
    for idx, l in enumerate(ans1_text):
        draw.text((304, 248 + idx * 20), l, fill=TEXT_WHITE, font=f_small)

    # Citation pill
    draw.rounded_rectangle([(304, 338), (440, 360)], radius=4, fill=(40, 50, 95), outline=ACCENT_CYAN)
    draw.text((314, 342), "📄 Clause 4.1 (p. 2)", fill=ACCENT_CYAN, font=f_small)
    draw.text((460, 342), "Latency: 2.1s • 429 tokens in / 41 tokens out", fill=TEXT_DARK_MUTED, font=f_small)

    # User Message 2
    draw.rounded_rectangle([(730, 395), (1145, 440)], radius=8, fill=ACCENT_BLUE)
    draw.text((750, 407), "What is the capital of Australia and the weather today?", fill=TEXT_WHITE, font=f_body)

    # Assistant Response 2 (Strict Refusal)
    draw.rounded_rectangle([(284, 455), (820, 535)], radius=8, fill=(25, 33, 62), outline=AMBER)
    draw.text((304, 470), "🛡️ ContractGuard Grounding Refusal:", fill=AMBER, font=f_bold_small)
    draw.text((304, 494), "\"I could not find this in your contract.\"", fill=TEXT_WHITE, font=f_h3)
    draw.text((304, 518), "Enforced in code: Questions outside contract scope are 100% refused.", fill=TEXT_MUTED, font=f_small)

    # Input Box
    draw.rounded_rectangle([(264, 650), (1050, 695)], radius=8, fill=(15, 20, 38), outline=CARD_BORDER)
    draw.text((284, 664), "Ask about notice periods, deposit refund windows, penalties, or liabilities...", fill=TEXT_DARK_MUTED, font=f_body)
    
    draw.rounded_rectangle([(1065, 650), (1170, 695)], radius=8, fill=ACCENT_BLUE)
    draw.text((1095, 664), "Send", fill=TEXT_WHITE, font=f_bold_small)

    save_both(img, "ask_contract_rag.png")

# ==================== 5. REVIEW AND NEGOTIATE ====================
def make_review_and_negotiate():
    img = Image.new("RGB", (1200, 750), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header_and_sidebar(draw, active_tab="Review & Negotiate")

    draw.text((264, 76), "Review & Negotiate (LangGraph Agent)", fill=TEXT_WHITE, font=f_title)
    draw.text((264, 114), "Human-in-the-loop review. Approve, custom edit, or reject proposed replacement wording.", fill=TEXT_MUTED, font=f_body)

    # Progress Card
    draw.rounded_rectangle([(264, 150), (1170, 205)], radius=8, fill=CARD_BG, outline=CARD_BORDER)
    draw.text((284, 162), "Review Decision Progress: 2 of 3 Decided", fill=TEXT_WHITE, font=f_bold_small)
    draw.text((1110, 162), "67%", fill=ACCENT_CYAN, font=f_bold_small)
    draw.rounded_rectangle([(284, 184), (1150, 194)], radius=4, fill=(35, 45, 70))
    draw.rounded_rectangle([(284, 184), (864, 194)], radius=4, fill=ACCENT_CYAN)

    # Suggestion Card 1
    draw.rounded_rectangle([(264, 225), (1170, 445)], radius=10, fill=CARD_BG, outline=GREEN)
    draw.text((284, 240), "Suggestion 1 • Clause 7.1: Limitation of Liability Cap", fill=TEXT_WHITE, font=f_h3)
    draw.rounded_rectangle([(1030, 237), (1145, 263)], radius=4, fill=(20, 50, 30), outline=GREEN)
    draw.text((1045, 242), "✓ APPROVED", fill=GREEN, font=f_bold_small)

    # Diff Box
    # Left (Original)
    draw.rounded_rectangle([(284, 275), (710, 360)], radius=6, fill=(40, 20, 20), outline=RED)
    draw.text((296, 283), "ORIGINAL CLAUSE (RISKY):", fill=RED, font=f_bold_small)
    draw.text((296, 305), "\"Tenant agrees to indemnify Landlord from any\nand all damages occurring with unlimited liability.\"", fill=TEXT_WHITE, font=f_mono)

    # Right (Proposed)
    draw.rounded_rectangle([(724, 275), (1150, 360)], radius=6, fill=(20, 45, 30), outline=GREEN)
    draw.text((736, 283), "PROPOSED COUNTER-CLAUSE (BALANCED):", fill=GREEN, font=f_bold_small)
    draw.text((736, 305), "\"Tenant's total aggregate liability under this Lease shall\nbe capped at two (2) months base rent ($5,000.00).\"", fill=TEXT_WHITE, font=f_mono)

    # Rationale
    draw.text((284, 372), "💡 Rationale: Eliminates catastrophic personal financial exposure in line with standard state residential tenancy guidelines.", fill=TEXT_MUTED, font=f_small)

    # Buttons
    draw.rounded_rectangle([(875, 400), (960, 432)], radius=6, fill=GREEN)
    draw.text((888, 408), "✓ Approve", fill=TEXT_WHITE, font=f_bold_small)
    
    draw.rounded_rectangle([(970, 400), (1055, 432)], radius=6, fill=(45, 55, 85))
    draw.text((985, 408), "✎ Edit", fill=TEXT_WHITE, font=f_bold_small)

    draw.rounded_rectangle([(1065, 400), (1150, 432)], radius=6, fill=(50, 25, 25), outline=RED)
    draw.text((1080, 408), "✕ Reject", fill=RED, font=f_bold_small)

    # Suggestion Card 2 (Pending Decision)
    draw.rounded_rectangle([(264, 465), (1170, 685)], radius=10, fill=CARD_BG, outline=CARD_BORDER)
    draw.text((284, 480), "Suggestion 2 • Clause 4.1: Rent Escalation Cap & Notice", fill=TEXT_WHITE, font=f_h3)
    draw.rounded_rectangle([(1010, 477), (1145, 503)], radius=4, fill=(50, 40, 15), outline=AMBER)
    draw.text((1025, 482), "⏳ PENDING DECISION", fill=AMBER, font=f_bold_small)

    # Diff Box
    draw.rounded_rectangle([(284, 515), (710, 600)], radius=6, fill=(40, 20, 20), outline=RED)
    draw.text((296, 523), "ORIGINAL CLAUSE (RISKY):", fill=RED, font=f_bold_small)
    draw.text((296, 545), "\"Landlord reserves unilateral right to increase rent by 8%\nannually upon providing thirty (30) days notice.\"", fill=TEXT_WHITE, font=f_mono)

    draw.rounded_rectangle([(724, 515), (1150, 600)], radius=6, fill=(20, 45, 30), outline=GREEN)
    draw.text((736, 523), "PROPOSED COUNTER-CLAUSE (BALANCED):", fill=GREEN, font=f_bold_small)
    draw.text((736, 545), "\"Any annual rent adjustment shall be capped at CPI (max 3%)\nand requires at least sixty (60) days advance written notice.\"", fill=TEXT_WHITE, font=f_mono)

    draw.text((284, 612), "💡 Rationale: Enforces standard statutory notice and prevents arbitrary rent surges during tenancy.", fill=TEXT_MUTED, font=f_small)

    draw.rounded_rectangle([(875, 640), (960, 672)], radius=6, fill=ACCENT_BLUE)
    draw.text((888, 648), "Approve", fill=TEXT_WHITE, font=f_bold_small)
    
    draw.rounded_rectangle([(970, 640), (1055, 672)], radius=6, fill=(45, 55, 85))
    draw.text((985, 648), "✎ Edit", fill=TEXT_WHITE, font=f_bold_small)

    draw.rounded_rectangle([(1065, 640), (1150, 672)], radius=6, fill=(45, 55, 85))
    draw.text((1080, 648), "Reject", fill=TEXT_WHITE, font=f_bold_small)

    save_both(img, "review_and_negotiate.png")

# ==================== 6. EXPORT AND EMAIL ====================
def make_export_and_email():
    img = Image.new("RGB", (1200, 750), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header_and_sidebar(draw, active_tab="Exports")

    draw.text((264, 76), "Negotiation Email & Reports Export", fill=TEXT_WHITE, font=f_title)
    draw.text((264, 114), "Generated strictly from your approved counter-clauses. Ready for immediate counter-proposal.", fill=TEXT_MUTED, font=f_body)

    # Email Box (Left)
    draw.rounded_rectangle([(264, 150), (840, 690)], radius=12, fill=CARD_BG, outline=CARD_BORDER)
    draw.text((284, 168), "📧 Ready-to-Send Counter-Offer Email", fill=TEXT_WHITE, font=f_h3)
    
    # Copy button
    draw.rounded_rectangle([(710, 162), (820, 192)], radius=6, fill=ACCENT_BLUE)
    draw.text((725, 170), "📋 Copy Email", fill=TEXT_WHITE, font=f_bold_small)

    email_text = [
        "Subject: Proposed Revisions to Skyline Apartments Lease - Mutual Alignment",
        "",
        "Dear Property Management Team,",
        "",
        "Thank you for sharing the draft lease agreement. I am eager to finalize our tenancy.",
        "To ensure balanced mutual risk protections in accordance with standard regional",
        "guidelines, I propose the following adjustments to the agreement:",
        "",
        "1. Clause 7.1 (Indemnification): Mutual liability limitation capped at two months base rent.",
        "   - Proposed wording: \"Tenant's total aggregate liability under this Lease shall be capped",
        "     at two (2) months base rent ($5,000.00). Neither party liable for consequential damages.\"",
        "",
        "2. Clause 4.1 (Rent Adjustments): Standardized annual cap to CPI (max 3%) with 60 days notice.",
        "   - Proposed wording: \"Any annual rent increase shall be capped at CPI (max 3%)",
        "     and requires sixty (60) days advance written notice.\"",
        "",
        "Please review the attached marked changes. I look forward to signing the finalized copy.",
        "",
        "Sincerely,",
        "John Doe",
        "---",
        "Notice: Generated via ContractGuard for negotiation review. Not legal advice."
    ]
    for idx, el in enumerate(email_text):
        draw.text((284, 212 + idx * 22), el, fill=TEXT_WHITE if idx < 1 else TEXT_MUTED, font=f_mono if idx < 1 else f_small)

    # Downloads Card (Right)
    draw.rounded_rectangle([(860, 150), (1170, 420)], radius=12, fill=CARD_BG, outline=CARD_BORDER)
    draw.text((880, 168), "📥 Download Reports", fill=TEXT_WHITE, font=f_h3)
    draw.text((880, 196), "Share formatted executive reports with landlords, clients, or legal counsel.", fill=TEXT_MUTED, font=f_small)

    # PDF button
    draw.rounded_rectangle([(880, 240), (1150, 290)], radius=8, fill=(45, 55, 85), outline=ACCENT_BLUE)
    draw.text((915, 255), "📄 Download Executive PDF Report", fill=TEXT_WHITE, font=f_bold_small)

    # DOCX button
    draw.rounded_rectangle([(880, 310), (1150, 360)], radius=8, fill=(45, 55, 85), outline=ACCENT_CYAN)
    draw.text((910, 325), "📝 Download Editable DOCX Redline", fill=TEXT_WHITE, font=f_bold_small)

    # Safety Guarantee Card
    draw.rounded_rectangle([(860, 440), (1170, 690)], radius=12, fill=(15, 30, 25), outline=GREEN)
    draw.text((880, 460), "🛡️ ContractGuard Safety Protocol", fill=GREEN, font=f_h3)
    
    safeties = [
        "Human-in-the-Loop: No exports are generated without explicit user approval.",
        "Zero Modification: Original uploaded contract files remain unaltered.",
        "Exclusion Filter: Rejected suggestions never appear in email or PDF exports.",
        "Formula Transparency: Every number traces to explicit rule engine formulas."
    ]
    for idx, s in enumerate(safeties):
        draw.text((880, 500 + idx * 42), f"✓ {s[:42]}", fill=TEXT_WHITE, font=f_bold_small)
        draw.text((898, 520 + idx * 42), s[42:], fill=TEXT_MUTED, font=f_small)

    save_both(img, "export_and_email.png")

# ==================== 7. ARCHITECTURE DIAGRAM ====================
def make_architecture_diagram():
    img = Image.new("RGB", (1200, 750), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Header
    draw.rectangle([(0, 0), (1200, 60)], fill=(12, 16, 32), outline=CARD_BORDER)
    draw.text((36, 16), "ContractGuard System Architecture & Pipeline Workflow", fill=TEXT_WHITE, font=f_h2)

    # Frontend
    draw.rounded_rectangle([(36, 90), (1164, 180)], radius=10, fill=CARD_BG, outline=ACCENT_BLUE)
    draw.text((56, 105), "FRONTEND: React 19 + TypeScript + Vite", fill=ACCENT_BLUE, font=f_h3)
    draw.text((56, 135), "Pages: Dashboard • Upload • Contract Overview • Clause Explorer • Ask Contract (RAG) • Review & Negotiate • Exports • History", fill=TEXT_WHITE, font=f_body)

    # Communication Arrow
    draw.line([(600, 180), (600, 220)], fill=ACCENT_CYAN, width=3)
    draw.text((615, 192), "REST API + Server-Sent Events (SSE)", fill=ACCENT_CYAN, font=f_small)

    # FastAPI Gateway
    draw.rounded_rectangle([(36, 220), (1164, 300)], radius=10, fill=CARD_BG, outline=ACCENT_CYAN)
    draw.text((56, 235), "BACKEND GATEWAY: FastAPI (Python 3.11+)", fill=ACCENT_CYAN, font=f_h3)
    draw.text((56, 265), "Routes: /contracts (Upload/List) • /versions (Clauses/Key-Terms/Risk) • /chat (RAG) • /review (Agent Run) • /exports", fill=TEXT_WHITE, font=f_body)

    # 3 Major Pillars
    # Pillar 1: Ingestion & RAG
    draw.rounded_rectangle([(36, 340), (380, 560)], radius=10, fill=CARD_BG, outline=CARD_BORDER)
    draw.text((56, 355), "1. Ingestion & RAG Engine", fill=ACCENT_CYAN, font=f_h3)
    p1 = [
        "• PDF/DOCX Parser (pypdf, docx)",
        "• Regex Heading Clause Splitter",
        "• Sentence-Transformers Embedder",
        "• Cosine Similarity Vector Search",
        "• Citation Validator ([Clause, Page])",
        "• Prompt-Injection Defense"
    ]
    for idx, l in enumerate(p1):
        draw.text((56, 395 + idx * 24), l, fill=TEXT_MUTED, font=f_small)

    # Pillar 2: Deterministic Rule Engine
    draw.rounded_rectangle([(418, 340), (782, 560)], radius=10, fill=CARD_BG, outline=AMBER)
    draw.text((438, 355), "2. Deterministic Rule Engine", fill=AMBER, font=f_h3)
    p2 = [
        "• Code does the maths, AI does language",
        "• dates.py (Keyword window parser)",
        "• durations.py (Word-to-number)",
        "• money.py (Decimal precision)",
        "• renewal.py (Trap date calculator)",
        "• calculators.py (100% test pass)",
        "• risk_scoring.py (Role weighting)"
    ]
    for idx, l in enumerate(p2):
        draw.text((438, 395 + idx * 22), l, fill=TEXT_MUTED, font=f_small)

    # Pillar 3: LangGraph Review Agent
    draw.rounded_rectangle([(820, 340), (1164, 560)], radius=10, fill=CARD_BG, outline=GREEN)
    draw.text((840, 355), "3. LangGraph Review Agent", fill=GREEN, font=f_h3)
    p3 = [
        "• extract_clauses -> classify_risk",
        "• retrieve_standard_terms from KB",
        "• draft_counter_clauses (LLM)",
        "• validate (Length, number check)",
        "• human_review (interrupt pause)",
        "• Command(resume=decisions)",
        "• export (Approved suggestions only)"
    ]
    for idx, l in enumerate(p3):
        draw.text((840, 395 + idx * 22), l, fill=TEXT_MUTED, font=f_small)

    # Storage Layer
    draw.rounded_rectangle([(36, 590), (1164, 690)], radius=10, fill=(15, 22, 42), outline=CARD_BORDER)
    draw.text((56, 605), "PERSISTENCE & STORAGE: PostgreSQL + pgvector (or SQLite Standalone)", fill=TEXT_WHITE, font=f_h3)
    draw.text((56, 635), "Tables: users • contracts • contract_versions • clauses (vectors) • key_terms • findings • suggestions • kb_documents • agent_runs • exports", fill=TEXT_MUTED, font=f_small)
    draw.text((56, 660), "Security: Strict per-user isolation by user_id • Zero raw contract text logged • Cascade deletion", fill=TEXT_DARK_MUTED, font=f_small)

    save_both(img, "architecture_diagram.png")

if __name__ == "__main__":
    make_dashboard()
    make_contract_overview()
    make_clause_explorer()
    make_ask_contract()
    make_review_and_negotiate()
    make_export_and_email()
    make_architecture_diagram()
    print("All screenshots generated successfully!")
