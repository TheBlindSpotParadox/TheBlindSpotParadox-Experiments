from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from copy import deepcopy

# === COLOR PALETTE (from reference deck) ===
TEAL_DARK   = RGBColor(0x00, 0x74, 0x8C)  # primary brand
TEAL        = RGBColor(0x1B, 0x7A, 0x8A)  # header bar
BLUE_DEEP   = RGBColor(0x3B, 0x6F, 0xA0)
BLUE        = RGBColor(0x29, 0x80, 0xB9)
ORANGE      = RGBColor(0xE0, 0x80, 0x00)
ORANGE_LT   = RGBColor(0xE8, 0x83, 0x3A)
RED         = RGBColor(0xC0, 0x39, 0x2B)
RED_LT      = RGBColor(0xE7, 0x4C, 0x3C)
PURPLE      = RGBColor(0x8E, 0x44, 0xAD)
GREEN       = RGBColor(0x27, 0xAE, 0x60)
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
BG_BLUE_LT  = RGBColor(0xEB, 0xF2, 0xFA)
BG_CREAM    = RGBColor(0xFF, 0xF8, 0xF0)
BG_PINK     = RGBColor(0xFF, 0xF0, 0xF0)
BG_GREEN_LT = RGBColor(0xE8, 0xF6, 0xEF)
TXT_DARK    = RGBColor(0x2C, 0x3E, 0x50)
TXT_BODY    = RGBColor(0x5D, 0x6D, 0x7E)
TXT_FAINT   = RGBColor(0x8A, 0x9B, 0xB0)
TXT_DARKER  = RGBColor(0x2D, 0x37, 0x48)

# === SLIDE GEOMETRY ===
SLIDE_W = 10.00  # inches
SLIDE_H = 5.62   # inches
TOTAL_SLIDES = 30

prs = Presentation()
prs.slide_width = Inches(SLIDE_W)
prs.slide_height = Inches(SLIDE_H)

# Use blank layout
BLANK = prs.slide_layouts[6]

def add_rect(slide, x, y, w, h, fill, line=None, shape=MSO_SHAPE.RECTANGLE):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
    s.shadow.inherit = False
    return s

def add_text(slide, x, y, w, h, text, font_name="Calibri", size=11, bold=False,
             color=TXT_DARK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, italic=False):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font_name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return tb

def add_multi_text(slide, x, y, w, h, runs, anchor=MSO_ANCHOR.TOP, align=PP_ALIGN.LEFT):
    """runs = list of (text, size, bold, color, italic_optional)"""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    for i, r in enumerate(runs):
        text = r[0]
        size = r[1]
        bold = r[2]
        color = r[3]
        italic = r[4] if len(r) > 4 else False
        if i == 0:
            run = p.add_run()
        else:
            run = p.add_run()
        run.text = text
        run.font.name = "Calibri"
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = color
    return tb

def add_paragraphs(slide, x, y, w, h, paragraphs, anchor=MSO_ANCHOR.TOP):
    """paragraphs = list of list of (text, size, bold, color, italic_optional)"""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for pi, para in enumerate(paragraphs):
        if pi == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        for r in para:
            text = r[0]
            size = r[1]
            bold = r[2]
            color = r[3]
            italic = r[4] if len(r) > 4 else False
            run = p.add_run()
            run.text = text
            run.font.name = "Calibri"
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.italic = italic
            run.font.color.rgb = color
    return tb

def header_bar(slide, title, page_num=None, total=20):
    idx = len(prs.slides)
    add_rect(slide, 0, 0, 10.00, 0.58, TEAL)
    add_text(slide, 0.40, 0.05, 8.50, 0.50, title, size=17, bold=True, color=WHITE,
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, 8.80, 5.20, 1.00, 0.35, f"{idx}", size=9, color=TXT_BODY,
             align=PP_ALIGN.RIGHT)

def page_num_only(slide, page_num=None, total=20):
    idx = len(prs.slides)
    add_text(slide, 8.80, 5.20, 1.00, 0.35, f"{idx}", size=9, color=TXT_BODY,
             align=PP_ALIGN.RIGHT)

def badge(slide, text, x=8.90, y=0.07, w=0.90, h=0.27, color=RED):
    add_rect(slide, x, y, w, h, color)
    add_text(slide, x, y, w, h, text, size=8, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

def vertical_bar(slide, x, y, color=TEAL, height=0.70):
    add_rect(slide, x, y, 0.06, height, color)

def lettered_circle(slide, x, y, letter, color=TEAL, size=0.55, fontsize=18):
    add_rect(slide, x, y, size, size, color, shape=MSO_SHAPE.OVAL)
    add_text(slide, x, y, size, size, letter, size=fontsize, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

def footer_refs(slide, refs):
    add_text(slide, 0.50, 5.36, 8.00, 0.26, refs, size=8, color=TXT_FAINT)

# --- deck-specific helpers (typography, placeholders, conclusion bands) ---

def fr(t):
    return t.replace(" :", "\u00A0:").replace(" ;", "\u00A0;")

def rich(text):
    parts = text.split("**")
    return [(seg, i % 2 == 1) for i, seg in enumerate(parts) if seg]

def body_runs(text, size=8.5, color=TXT_BODY, bold_color=TXT_DARK):
    return [(seg, size, b, bold_color if b else color) for seg, b in rich(fr(text))]

def sec(slide, x, y, w, text, color=TEAL_DARK, size=9.5):
    add_text(slide, x, y, w, 0.24, fr(text), size=size, bold=True, color=color)

def bullets(slide, x, y, w, h, items, size=8.5, color=TXT_BODY, bold_color=TXT_DARK):
    paras = [body_runs("•  " + it, size, color, bold_color) for it in items]
    return add_paragraphs(slide, x, y, w, h, paras)

def conclusion_band(slide, text):
    add_rect(slide, 0.30, 4.85, 9.40, 0.27, BG_CREAM)
    add_text(slide, 0.30, 4.85, 9.40, 0.27, fr(text), size=9, bold=True, color=ORANGE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

def visual_placeholder(slide, x, y, w, h, desc):
    add_rect(slide, x, y, w, h, BG_BLUE_LT)
    add_text(slide, x + 0.15, y + 0.10, w - 0.30, h - 0.20, "[FIGURE]  " + fr(desc),
             size=9, italic=True, color=TXT_FAINT, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)

def underline_urls(tb):
    for p in tb.text_frame.paragraphs:
        for r in p.runs:
            if r.text.startswith("http"):
                r.font.underline = True

def equation_box(slide, x, y, w, h, formula, note):
    add_rect(slide, x, y, w, h, BG_BLUE_LT)
    add_text(slide, x + 0.10, y + 0.05, w - 0.20, 0.26, formula, size=10,
             italic=True, color=TXT_DARKER)
    add_text(slide, x + 0.10, y + 0.32, w - 0.20, h - 0.36, fr(note), size=7.5,
             color=TXT_BODY)

def divider(slide, letter, color, title, desc):
    add_rect(slide, 0.00, 1.50, 10.00, 2.60, TEAL)
    add_rect(slide, 1.20, 1.85, 1.50, 1.50, color)
    add_text(slide, 1.20, 1.85, 1.50, 1.50, letter, size=42, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, 3.20, 2.05, 6.00, 0.60, title, size=26, bold=True, color=WHITE)
    add_text(slide, 3.20, 2.95, 6.00, 0.80, fr(desc), size=12,
             color=RGBColor(0xD5, 0xDB, 0xDB))
    page_num_only(slide)

# =========================================================================
# SLIDE 1 — TITRE
# =========================================================================
s = prs.slides.add_slide(BLANK)
add_rect(s, 0.60, 0.50, 8.80, 2.20, TEAL_DARK)
add_paragraphs(s, 0.75, 0.65, 8.50, 2.00, [
    [("Blind Spot Paradox", 28, True, WHITE)],
    [("Manuscrit v65 figé", 26, True, WHITE)],
    [("", 8, False, WHITE)],
    [("Huit faiblesses ICDM 2026 → huit réponses mesurées", 16, False, WHITE, True)],
])
add_rect(s, 0.60, 2.80, 8.80, 0.06, ORANGE)
add_rect(s, 0.00, 3.00, 10.00, 1.80, BLUE_DEEP)
add_rect(s, 0.60, 3.10, 8.80, 0.46, ORANGE)
add_text(s, 0.70, 3.14, 8.60, 0.38, "Point Hebdo C.S. du 28/09/2026",
         size=14, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
add_text(s, 0.70, 3.62, 8.60, 0.38, "R. Minato  —  Résultats, points ouverts, soumission",
         size=12, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
idx = len(prs.slides)
add_text(s, 9.00, 5.25, 0.80, 0.30, f"{idx}", size=9, color=WHITE,
         align=PP_ALIGN.RIGHT)

# =========================================================================
# SLIDE 2 — PLAN
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "Plan")
sections = [
    ("A", ORANGE_LT, "A — Le point de départ",
     "Ce que les relecteurs ont reproché, et le vocabulaire pour en parler"),
    ("B", TEAL, "B — Tableau de bord",
     "Huit faiblesses, huit chantiers, huit résultats"),
    ("C", RED, "C — Résultats, point par point",
     "Ce qui répond, ce qui dépasse la demande, ce qui surprend"),
    ("D", GREEN, "D — Ce qui reste",
     "En suspens et à ré-auditer"),
    ("E", PURPLE, "E — Publication",
     "Revue cible et solutions de repli"),
]
for i, (letter, color, title, desc) in enumerate(sections):
    y = 0.80 + i * 0.84
    lettered_circle(s, 0.50, y, letter, color=color, size=0.55, fontsize=18)
    add_text(s, 1.30, y - 0.02, 8.00, 0.32, title, size=11, bold=True, color=TXT_DARK)
    add_text(s, 1.30, y + 0.30, 8.00, 0.30, fr(desc), size=9, color=TXT_BODY)

# =========================================================================
# SLIDE 3 — DIVIDER A
# =========================================================================
s = prs.slides.add_slide(BLANK)
divider(s, "A", ORANGE_LT, "Le point de départ",
        "Quatre relecteurs, deux rejets fermes, deux avis marginaux  ·  "
        "Phénomène jugé intéressant, théorie jugée insuffisante")

# =========================================================================
# SLIDE 4 — LES HUIT FAIBLESSES
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "Ce que les relecteurs ont reproché")

add_rect(s, 0.30, 0.72, 0.65, 0.30, TEAL)
add_text(s, 0.30, 0.72, 0.65, 0.30, "#", size=9, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_rect(s, 0.95, 0.72, 6.50, 0.30, TEAL)
add_text(s, 0.95, 0.72, 6.50, 0.30, "  Faiblesse", size=9, bold=True, color=WHITE,
         anchor=MSO_ANCHOR.MIDDLE)
add_rect(s, 7.45, 0.72, 2.25, 0.30, TEAL)
add_text(s, 7.45, 0.72, 2.25, 0.30, "  Origine", size=9, bold=True, color=WHITE,
         anchor=MSO_ANCHOR.MIDDLE)

weaknesses = [
    ("W1", "La borne centrale supprime un terme positif d'une inégalité, ignore la remise à zéro du compteur, et conclut à une probabilité d'alarme nulle à horizon infini", "3 relecteurs", False),
    ("W2", "La course entre adaptation et détection compare une variable aléatoire à une constante ; la borne d'indépendance entre arbres est affirmée, pas démontrée", "3 relecteurs", False),
    ("W3", "L'adaptation de la forêt est datée au premier arbre remplacé ; aucune trajectoire synchronisée ne relie remplacement, erreur et statistique du moniteur", "3 relecteurs", False),
    ("W4", "Le principe de découplage est énoncé en « si et seulement si », que les données du papier réfutent ; sa condition mêle une horloge et un seuil, propres à deux familles différentes", "2 relecteurs", False),
    ("W5", "Pourquoi surveiller de l'extérieur un modèle qui se répare seul ? L'architecture n'est pas motivée", "1 relecteur, avec veto", True),
    ("W6", "Le phénomène est-il un artefact d'une bibliothèque, d'un classifieur et d'un détecteur uniques ?", "2 relecteurs", False),
    ("W7", "L'immunité d'un détecteur à fenêtres est déclarée structurelle sur un balayage partiel", "1 relecteur", False),
    ("W8", "Validité externe, protocole statistique incomplet, écarts entre le manuscrit et son code public", "1 relecteur", False),
]
for i, (wid, text, orig, is_w5) in enumerate(weaknesses):
    y = 1.02 + i * 0.44
    fill = BG_PINK if is_w5 else (WHITE if i % 2 == 0 else BG_BLUE_LT)
    add_rect(s, 0.30, y, 9.40, 0.44, fill)
    if is_w5:
        add_rect(s, 0.30, y, 0.05, 0.44, RED)
    add_text(s, 0.30, y, 0.65, 0.44, wid, size=9, bold=True, color=ORANGE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_paragraphs(s, 0.95, y, 6.50, 0.44, [body_runs(text, 8)])
    if is_w5:
        add_multi_text(s, 7.45, y, 2.25, 0.44, [
            ("1 relecteur, ", 8, False, TXT_DARK),
            ("avec veto", 8, True, RED),
        ], anchor=MSO_ANCHOR.MIDDLE)
    else:
        add_text(s, 7.45, y, 2.25, 0.44, orig, size=8, color=TXT_DARK,
                 anchor=MSO_ANCHOR.MIDDLE)

conclusion_band(s, "★ Les scores : technique −4 / −4 / −2 / −2. Deux relecteurs se "
                  "déclarent d'expertise haute ; l'un d'eux rejette la prémisse elle-même.")

# =========================================================================
# SLIDE 5 — NOTATIONS
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "Le vocabulaire, une fois pour toutes")

add_rect(s, 0.30, 0.72, 9.40, 1.24, BG_BLUE_LT)
add_text(s, 0.40, 0.74, 9.20, 0.22, "Le flux et le classifieur", size=9.5, bold=True,
         color=TEAL_DARK)
flux_items = [
    ("e_t", " — erreur de prédiction au pas de temps t, valant 0 ou 1"),
    ("p_0", " — taux d'erreur avant la rupture"),
    ("τ*", " — instant de la rupture ; Δe — saut du taux d'erreur qu'elle provoque"),
    ("M", " — nombre d'arbres de la forêt ; τ_ARF — instant du premier arbre remplacé"),
    ("τ_erase", " — instant où l'erreur moyenne repasse sous p_0 + δ_P"),
    ("W", " — durée du transitoire exploitable, de τ* à τ_erase"),
]
add_paragraphs(s, 0.40, 0.98, 9.20, 0.94,
               [[(sym, 8.5, True, TXT_DARK), (fr(desc), 8.5, False, TXT_BODY)]
                for sym, desc in flux_items])

add_rect(s, 0.30, 2.02, 9.40, 0.94, BG_CREAM)
add_text(s, 0.40, 2.04, 9.20, 0.22, "Le moniteur externe", size=9.5, bold=True,
         color=ORANGE)
mon_items = [
    ("δ_P", " — tolérance : l'excès d'erreur en deçà duquel le moniteur n'accumule rien"),
    ("S_t", " — compteur cumulé, remis à zéro dès qu'il passe sous zéro"),
    ("λ", " — seuil d'alarme ; α — niveau de fausse alarme ; ARL₀ — temps moyen avant fausse alarme"),
    ("τ_det", " — instant de l'alarme"),
]
add_paragraphs(s, 0.40, 2.28, 9.20, 0.64,
               [[(sym, 8.5, True, TXT_DARK), (fr(desc), 8.5, False, TXT_BODY)]
                for sym, desc in mon_items])

add_rect(s, 0.30, 3.02, 9.40, 0.88, BG_GREEN_LT)
add_rect(s, 0.30, 3.02, 0.05, 0.88, ORANGE)
add_text(s, 0.45, 3.04, 9.15, 0.22, "Les deux grandeurs que l'article introduit",
         size=9.5, bold=True, color=GREEN)
add_paragraphs(s, 0.45, 3.28, 9.15, 0.58, [
    [("A", 8.5, True, TXT_DARK),
     (fr(" — budget de preuve : l'excès d'erreur intégré que l'adaptation laisse au moniteur"), 8.5, False, TXT_BODY)],
    [("R(D, ε, α)", 8.5, True, TXT_DARK),
     (fr(" — exigence de preuve du moniteur D : ce qu'il lui faut pour alarmer avec probabilité 1 − ε au niveau α"), 8.5, False, TXT_BODY)],
])

add_rect(s, 0.30, 4.00, 9.40, 0.52, BG_BLUE_LT)
add_text(s, 0.30, 4.00, 9.40, 0.52,
         "S_t = max(0 ; S_{t−1} + (e_t − p_0) − δ_P)",
         size=10, italic=True, color=TXT_DARKER, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE)

# =========================================================================
# SLIDE 6 — DIVIDER B
# =========================================================================
s = prs.slides.add_slide(BLANK)
divider(s, "B", BLUE, "Tableau de bord",
        "Huit faiblesses, huit chantiers, huit résultats  ·  "
        "Manuscrit figé, audit adversarial à lancer")

# =========================================================================
# SLIDE 7 — TABLEAU DE BORD 1/2
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "État du travail — W1 à W4")

col_x = [0.30, 2.00, 5.85]
col_w = [1.70, 3.85, 3.85]
headers = ["Faiblesse", "Travail réalisé", "Résultat"]
for x, w, htxt in zip(col_x, col_w, headers):
    add_rect(s, x, 0.72, w, 0.30, TEAL)
    add_text(s, x, 0.72, w, 0.30, "  " + htxt, size=9, bold=True, color=WHITE,
             anchor=MSO_ANCHOR.MIDDLE)

dash1 = [
    ("W1 — Borne centrale invalide",
     "Preuve refaite : inégalité maximale de Doob, concentration d'Azuma–Hoeffding, réunion sur les remises à zéro. Horizon infini traité par le temps moyen avant fausse alarme",
     "**Terminé.** Borne valide, terme de fluctuation conservé. **Et elle est vide presque partout** : informative sur 32 couples (λ, Δe) sur 240. Le résultat porteur devient un certificat déterministe sur le budget mesuré"),
    ("W2 — Course mal posée, indépendance non démontrée",
     "Course reformulée en risques concurrents avec censure. Deux bornes : une sans hypothèse de dépendance, une sous indépendance conditionnelle",
     "**Terminé.** L'indépendance conditionnelle est **réfutée par le code** — la forêt partage un seul générateur aléatoire. La borne sans hypothèse porte seule, elle sature, la taille critique d'ensemble est retirée"),
    ("W3 — Métrique d'adaptation, pas de trajectoires",
     "Famille de temps d'adaptation définie et instrumentée. Bras contrefactuels partageant flux, histoire et bifurcation",
     "**Terminé.** L'effacement vient à **98,6 %** de l'apprentissage ordinaire des arbres survivants. Le premier remplacement pèse **0,71 %** du volume — et **31 points** de taux de détection"),
    ("W4 — « Si et seulement si » réfuté, condition hybride",
     "Biconditionnel retiré. Condition suffisante de calibration, exprimée en budget contre exigence, indépendante de la famille de détecteur",
     "**Terminé.** Plancher de détectabilité mesuré **Δe_c = 0,120** ; seuil opérationnel **λ_op = 21,9**. Deux prédicats publiés au lieu d'un, chacun avec son mécanisme"),
]
for i, (w, trav, res) in enumerate(dash1):
    y = 1.02 + i * 0.98
    fill = WHITE if i % 2 == 0 else BG_BLUE_LT
    add_rect(s, 0.30, y, 9.40, 0.98, fill)
    add_text(s, col_x[0] + 0.05, y + 0.04, col_w[0] - 0.10, 0.90, fr(w), size=8,
             bold=True, color=TXT_DARK)
    add_paragraphs(s, col_x[1] + 0.05, y + 0.04, col_w[1] - 0.10, 0.90,
                   [body_runs(trav, 8)])
    add_paragraphs(s, col_x[2] + 0.05, y + 0.04, col_w[2] - 0.10, 0.90,
                   [body_runs(res, 8)])

# =========================================================================
# SLIDE 8 — TABLEAU DE BORD 2/2
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "État du travail — W5 à W8")

for x, w, htxt in zip(col_x, col_w, headers):
    add_rect(s, x, 0.72, w, 0.30, TEAL)
    add_text(s, x, 0.72, w, 0.30, "  " + htxt, size=9, bold=True, color=WHITE,
             anchor=MSO_ANCHOR.MIDDLE)

dash2 = [
    ("W5 — Architecture non motivée",
     "Problème reformulé en détection de défaut sur un résidu endogène — le classifieur agit sur la grandeur même que le moniteur lit. Ancrage réglementaire et outillage de production",
     "**Terminé.** Le cadre existait depuis trente ans en automatique : un régulateur à action intégrale masque le défaut aux détecteurs à résidus. Le règlement européen sur l'IA nomme le danger"),
    ("W6 — Artefact de bibliothèque ?",
     "Autres mécanismes internes, seconde implémentation, second générateur à prior équilibré",
     "**Terminé.** Le phénomène survit partout, mais il est **moins extrême** que la grille publiée ne le disait : 0,99–1,00 de manqués sur la famille d'origine, **0,33–0,77** sous le générateur corrigé"),
    ("W7 — Immunité surinterprétée",
     "Balayage complet, niveaux de fausse alarme égalisés, détecteur ré-armé à vif",
     "**Terminé, et retourné.** À seuil publié, le détecteur à fenêtres est lu **4,5× plus permissif** que le cumulatif. Sur flux à socle d'erreur non nul, il alarme **avant même la rupture**, à tous les niveaux"),
    ("W8 — Validité externe, protocole, cohérence",
     "Section protocole complète. Oracle sur classifieur gelé. Correction pour comparaisons multiples. Gel des empreintes",
     "**Terminé.** L'écart de **10,6×** sur données réelles tombe à **1,27** à budget égal : 90 % venait du seuil. Un jeu de données requalifié en témoin négatif, prouvé"),
]
for i, (w, trav, res) in enumerate(dash2):
    y = 1.02 + i * 0.88
    fill = WHITE if i % 2 == 0 else BG_BLUE_LT
    add_rect(s, 0.30, y, 9.40, 0.88, fill)
    add_text(s, col_x[0] + 0.05, y + 0.04, col_w[0] - 0.10, 0.80, fr(w), size=8,
             bold=True, color=TXT_DARK)
    add_paragraphs(s, col_x[1] + 0.05, y + 0.04, col_w[1] - 0.10, 0.80,
                   [body_runs(trav, 8)])
    add_paragraphs(s, col_x[2] + 0.05, y + 0.04, col_w[2] - 0.10, 0.80,
                   [body_runs(res, 8)])

conclusion_band(s, "★ Manuscrit figé le 27/09 : 64 pages, 192 tests au vert, "
                  "PDF reproductible à l'octet. Reste l'audit adversarial.")

# =========================================================================
# SLIDE 9 — DIVIDER C
# =========================================================================
s = prs.slides.add_slide(BLANK)
divider(s, "C", RED, "Résultats, point par point",
        "Ce qui répond à la demande, ce qui la dépasse, ce qui surprend")

# =========================================================================
# SLIDE 10 — W1 : LA BORNE
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "W1 — La borne réparée, et ce qu'elle apprend")

sec(s, 0.30, 0.72, 4.55, "Le reproche, en une phrase")
add_paragraphs(s, 0.30, 0.96, 4.55, 0.50, [body_runs(
    "La preuve écrivait E[max] ≤ dérive + fluctuation, puis gardait la dérive seule. "
    "Supprimer un terme positif d'une borne supérieure n'est pas permis.", 8)])
sec(s, 0.30, 1.48, 4.55, "Ce que nous avons fait")
bullets(s, 0.30, 1.72, 4.55, 1.60, [
    "Le compteur se remet à zéro : franchir le seuil, c'est le franchir depuis **l'un quelconque** des points de remise à zéro. Une réunion sur ces points, puis l'inégalité maximale de Doob, puis la concentration d'Azuma–Hoeffding pour des incréments bornés.",
    "Le terme de fluctuation reste. Il vaut √((W/2)·ln(W/ε)) et il **domine** en régime de dérive faible.",
    "L'énoncé à horizon infini est remplacé par le temps moyen avant fausse alarme, qui croît exponentiellement avec le seuil. Après récupération, toute alarme est une fausse alarme de taux 1/ARL₀ : elle ne dit rien de la dérive.",
], size=8)
sec(s, 0.30, 3.42, 4.55, "Le résultat inattendu")
bullets(s, 0.30, 3.66, 4.55, 1.45, [
    "Lue à la vraie durée du transitoire, la borne honnête est **vide presque partout**. Informative sur 32 couples (λ, Δe) sur 240 testés.",
    "Ce domaine étroit contient exactement le point d'opération où le certificat de famine est énoncé. Le papier le dit, et déplace le résultat porteur vers un **certificat déterministe** : s'il existe une sous-fenêtre où l'aire excédentaire dépasse le seuil augmenté du coût de tolérance, l'alarme se déclenche nécessairement.",
], size=8)

add_rect(s, 5.00, 0.72, 4.70, 0.92, BG_PINK)
add_text(s, 5.10, 0.76, 4.50, 0.22, "La preuve fautive", size=9, bold=True, color=RED)
tb = add_multi_text(s, 5.10, 1.00, 4.50, 0.28, [
    ("E[max] ≤ μW + ", 10, False, TXT_DARKER, True),
    ("√((W/2)·ln(W/ε))", 10, False, RED, True),
])
for r in tb.text_frame.paragraphs[0].runs:
    if "√" in r.text:
        r._r.get_or_add_rPr().set("strike", "sngStrike")
add_text(s, 5.10, 1.30, 4.50, 0.24, "terme supprimé — interdit", size=8,
         italic=True, color=RED)
s.shapes.add_picture("figures/fig1_borne_deux_termes.png", Inches(5.00),
                     Inches(1.78), width=Inches(4.70))

equation_box(s, 0.30, 4.12, 4.55, 0.92,
             "P(τ_det ≤ W) ≤ W · exp(−2·(λ − S_0 − μW)² / W)",
             "La borne à horizon fini. μ = Δe − δ_P est le taux d'accumulation moyen ; "
             "S_0 : niveau du compteur à la rupture ; parenthèse à sa partie positive.")
equation_box(s, 5.00, 4.12, 4.70, 0.92,
             "S_max(H) = max_{0 ≤ k ≤ j ≤ H} [ A(k,j) − (j−k)·δ_P ]",
             "Le certificat déterministe, vrai sur chaque exécution prise isolément. "
             "A(k,j) : aire excédentaire entre les pas k et j.")
footer_refs(s, "Doob (1953) · Hoeffding (1963) · Siegmund (1985) · Lorden (1971)")

# =========================================================================
# SLIDE 11 — W2 : LA COURSE
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "W2 — La course, et l'hypothèse que le code réfute")

sec(s, 0.30, 0.72, 5.55, "Le reproche")
add_paragraphs(s, 0.30, 0.96, 5.55, 0.45, [body_runs(
    "L'instant de détection était traité comme une constante, alors qu'il varie d'une "
    "exécution à l'autre. Et la borne d'indépendance entre arbres était annoncée, "
    "jamais démontrée.", 8)])
sec(s, 0.30, 1.42, 5.55, "Ce que nous avons fait")
bullets(s, 0.30, 1.66, 5.55, 1.00, [
    "La course devient un modèle de **risques concurrents avec censure** : les exécutions sans alarme sont comptées, pas écartées. C'est là que les rapports dérapent d'ordinaire.",
    "Deux bornes. L'une, dite de Boole, est valide quelle que soit la dépendance. L'autre suppose les arbres indépendants **conditionnellement au flux** — l'aléa propre à chaque arbre étant ses poids de rééchantillonnage et ses tirages de variables.",
], size=8)
sec(s, 0.30, 2.72, 5.55, "Le résultat inattendu, et il est net")
bullets(s, 0.30, 2.96, 5.55, 1.80, [
    "L'indépendance conditionnelle **ne tient pas** : la bibliothèque fait circuler **un seul générateur aléatoire** dans toute la forêt. La voie par inégalité de Jensen tombe.",
    "Reste la borne sans hypothèse. Elle sature : au point d'opération, elle affirme que la probabilité de manquer vaut au plus 100 %.",
    "Conséquence assumée : la **taille critique d'ensemble est retirée**, remplacée par l'incidence mesurée. Un corollaire qui ne survit pas à sa propre hypothèse ne se publie pas.",
    "Deux mesures de plus, non demandées : la substitution du délai d'un arbre unique à celui d'un membre de la forêt est **réfutée** sur 10 cellules testables sur 80, toujours dans le sens optimiste. Et la course **n'est pas monotone** en amplitude : à seuil intermédiaire, le moniteur gagne 0 fois, puis 32 fois sur 100, puis 0.",
], size=8)

visual_placeholder(s, 6.00, 0.72, 3.70, 3.30,
    "Schéma en deux voies partant de « borne d'indépendance ». Voie haute "
    "« indépendance conditionnelle » barrée en rouge, annotée « un seul générateur "
    "pour toute la forêt ». Voie basse « Boole, sans hypothèse » en vert, aboutissant "
    "à un encadré « sature au point d'opération → taille critique retirée ».")
equation_box(s, 0.30, 4.12, 9.40, 0.85,
             "P(min_i τ_i ≤ s) ≤ min(1 ; M·F(s))",
             "La borne sans hypothèse de dépendance. F est la loi du délai d'adaptation "
             "d'un arbre ; τ_i celui de l'arbre i.")
footer_refs(s, "Esary, Proschan & Walkup (1967) · Fine & Gray (1999)")

# =========================================================================
# SLIDE 12 — W3 : LA DÉCOMPOSITION CAUSALE
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "W3 — Qui efface la preuve, exactement")

sec(s, 0.30, 0.72, 4.55, "Le reproche")
add_paragraphs(s, 0.30, 0.96, 4.55, 0.65, [body_runs(
    "Dater l'adaptation de la forêt au premier arbre remplacé, c'est confondre le "
    "déclencheur et le mécanisme. Et aucune figure ne montrait, sur un même axe de "
    "temps, les remplacements, l'erreur et le compteur du moniteur.", 8.5)])
sec(s, 5.55, 0.72, 4.15, "Ce que nous avons fait")
bullets(s, 5.55, 0.96, 4.15, 0.70, [
    "Trajectoires synchronisées, instrumentées pas à pas.",
    "Trois bras contrefactuels partageant le même flux, la même histoire et le même point de bifurcation : la forêt complète, la forêt dont on supprime les remplacements postérieurs au premier, la forêt dont on supprime tous les remplacements depuis la rupture.",
], size=8)

s.shapes.add_picture("figures/fig2_decomposition_causale.png", Inches(0.30),
                     Inches(1.78), width=Inches(5.10))

tcol_x = [5.55, 7.55, 8.60]
tcol_w = [2.00, 1.05, 1.10]
for x, w, htxt in zip(tcol_x, tcol_w,
                      ["Contribution à l'effacement", "Part", "Intervalle"]):
    add_rect(s, x, 1.80, w, 0.24, TEAL)
    add_text(s, x, 1.80, w, 0.24, "  " + htxt, size=7.5, bold=True, color=WHITE,
             anchor=MSO_ANCHOR.MIDDLE)
decomp = [
    ("Apprentissage incrémental des M−1 arbres survivants", "98,64 %", "[98,48 ; 98,82]"),
    ("Premier remplacement", "0,71 %", "[0,63 ; 0,78]"),
    ("Remplacements suivants", "0,56 %", "[0,47 ; 0,67]"),
]
for i, (lab, part, interv) in enumerate(decomp):
    y = 2.04 + i * 0.30
    fill = WHITE if i % 2 == 0 else BG_BLUE_LT
    add_rect(s, 5.55, y, 4.15, 0.30, fill)
    add_text(s, 5.60, y, 1.95, 0.30, fr(lab), size=7.5, color=TXT_DARK,
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, 7.55, y, 1.05, 0.30, part, size=7.5, bold=True, color=TXT_DARK,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, 8.60, y, 1.10, 0.30, interv, size=7.5, color=TXT_BODY,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

bullets(s, 5.55, 3.05, 4.15, 2.05, [
    "Résidu d'additivité : 2,3 × 10⁻¹³. La décomposition est exacte.",
    "**Le mécanisme qui donnait son nom à l'article pèse 0,7 % du volume.** Ce qui efface la preuve, c'est l'apprentissage ordinaire.",
    "Et pourtant ces 0,7 % **valent 31 points de taux de détection** : 0 détection sur 100 pour la forêt complète, 18 sur 100 en supprimant les remplacements postérieurs au premier, **49 sur 100** en les supprimant tous. Le premier remplacement est volumétriquement négligeable et causalement décisif.",
    "Mesure annexe qui contredit le récit initial : la latence du premier remplacement **n'est pas monotone**. 130 pas à Δe = 0,028, **417,5** à Δe = 0,085, puis descente jusqu'à 29. Une dérive faible élève la variance, élargit la borne de confiance du mécanisme interne, et étouffe les remplacements de bruit.",
], size=8)

# =========================================================================
# SLIDE 13 — W4 : LA RÈGLE DE CALIBRATION
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "W4 — Du principe réfuté à la règle qui marche")

sec(s, 0.30, 0.72, 5.55, "Le reproche")
add_paragraphs(s, 0.30, 0.96, 5.55, 0.50, [body_runs(
    "Un « si et seulement si » que les propres données du papier contredisaient, et une "
    "condition qui conjuguait une horloge — propre à un détecteur à fenêtre adaptative — "
    "et un seuil — propre à un compteur cumulatif. Deux familles, une seule inégalité.", 8.5)])
sec(s, 0.30, 1.50, 5.55, "Ce que nous avons fait")
bullets(s, 0.30, 1.74, 5.55, 0.55, [
    "Le biconditionnel est retiré. À sa place, une **condition suffisante** énoncée dans la seule unité qui vaut pour tout le monde : la preuve.",
    "Détecter exige que le budget laissé par l'adaptation excède l'exigence du moniteur.",
], size=8.5)
sec(s, 0.30, 2.36, 5.55, "Le résultat, mesuré")
bullets(s, 0.30, 2.60, 5.55, 0.95, [
    "**Plancher de détectabilité** : Δe_c = 0,120, intervalle [0,114 ; 0,127]. Sous ce plancher, aucune calibration ne satisfait à la fois le budget de fausses alarmes et le certificat.",
    "**Seuil opérationnel** : λ_op = 21,93, intervalle [19,88 ; 22,40], sur la plage Δe ∈ [0,20 ; 0,40].",
    "Ce que le relecteur demandait — retirer un « ssi » — a produit un nombre qu'un praticien règle.",
], size=8.5)
sec(s, 0.30, 3.62, 5.55, "Ce que nous n'avons pas unifié, et pourquoi")
bullets(s, 0.30, 3.86, 5.55, 1.20, [
    "Deux familles de moniteurs, deux prédicats. Un compteur cumulatif dépense une **intégrale** d'excès d'erreur. Un test à deux échantillons dépense du **contraste** à l'intérieur de sa fenêtre.",
    "Le second modèle reproduit les mesures à **93,1 %** contre 85,0 % pour la forme unifiée. La généralisation avait été pré-enregistrée ; la règle fixée d'avance l'a refusée.",
], size=8.5)

visual_placeholder(s, 6.00, 0.72, 3.70, 3.30,
    "Axe horizontal Δe de 0 à 0,5. Zone rouge hachurée sous 0,120 annotée « plancher "
    "de détectabilité ». Ligne horizontale λ_op = 21,9 avec sa bande d'incertitude, "
    "tracée sur la plage [0,20 ; 0,40]. Au-dessus, deux boîtes « intégrale » et "
    "« contraste » reliées à la condition centrale.")
equation_box(s, 0.30, 4.12, 4.55, 0.92,
             "R(D, ε, α) ≤ A",
             "La condition de calibration, indépendante de la famille de détecteur. "
             "Détecter exige que le budget laissé par l'adaptation excède l'exigence "
             "du moniteur.")
equation_box(s, 5.00, 4.12, 4.70, 0.92,
             "min(W ; n_stat) · Δe ≥ k*(α ; n_stat)",
             "Le prédicat propre aux détecteurs à fenêtre. n_stat : taille de "
             "l'échantillon de test ; k* : contraste minimal requis.")

# =========================================================================
# SLIDE 14 — LE RÉSULTAT CENTRAL
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "La cloche d'évidence — trois régimes, une seule courbe")

s.shapes.add_picture("figures/Fig_S13_evidence_bell.png", Inches(0.30),
                     Inches(0.72), width=Inches(6.60))

sec(s, 7.05, 0.72, 2.65, "Ce que l'article disait, et qui était faux", size=8.5)
add_paragraphs(s, 7.05, 0.92, 2.65, 0.65, [body_runs(
    "Le budget de preuve était calculé par un produit : le saut d'erreur multiplié "
    "par la durée moyenne avant le premier remplacement. Ce produit donnait une "
    "constante, « 18,5 quelle que soit la violence de la dérive ».", 7.5)])
sec(s, 7.05, 1.61, 2.65, "Ce que nous mesurons", size=8.5)
add_paragraphs(s, 7.05, 1.81, 2.65, 0.52, [body_runs(
    "Le maximum réellement atteint par le compteur sur l'horizon, exécution par "
    "exécution, bruit compris. C'est exactement la grandeur que le détecteur compare "
    "à son seuil.", 7.5)])
bullets(s, 7.05, 2.37, 2.65, 0.90, [
    "Elle monte, culmine, redescend. Facteur **3,6** entre les deux extrémités.",
    "Le sommet n'est pas identifiable à cent graines : les deux points du plateau diffèrent de 0,58 contre des demi-largeurs de 0,97. Nous publions le **plateau**, pas le point.",
], size=7.5)

bell_x = [1.60, 2.757, 3.914, 5.071, 6.228, 7.385, 8.542]
bell_de = ["0,028", "0,141", "0,194", "0,243", "0,327", "0,416", "0,498"]
bell_de_bold = [False, False, True, True, False, False, False]
bell_smax = ["5,28", "29,18", "33,20", "32,62", "31,33", "26,43", "19,13"]
bell_smax_bold = [True, False, True, False, False, False, True]
add_rect(s, 0.30, 3.36, 1.30, 0.24, TEAL)
add_text(s, 0.30, 3.36, 1.30, 0.24, "Δe", size=8, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
for x, v, b in zip(bell_x, bell_de, bell_de_bold):
    add_rect(s, x, 3.36, 1.157, 0.24, BG_BLUE_LT)
    add_text(s, x, 3.36, 1.157, 0.24, v, size=8, bold=b, color=TXT_DARK,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_rect(s, 0.30, 3.60, 1.30, 0.24, TEAL)
add_text(s, 0.30, 3.60, 1.30, 0.24, "E[S_max]", size=8, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
for x, v, b in zip(bell_x, bell_smax, bell_smax_bold):
    add_rect(s, x, 3.60, 1.157, 0.24, WHITE)
    add_text(s, x, 3.60, 1.157, 0.24, v, size=8, bold=b, color=TXT_DARK,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

sec(s, 0.30, 3.94, 4.55, "Les trois régimes, sans un seul paramètre libre", size=8.5)
bullets(s, 0.30, 4.18, 4.55, 0.95, [
    "**λ = 50** domine la cloche partout → détection ≤ 0,01 de bout en bout.",
    "**λ = 25** coupe la cloche → 0,00 à gauche, **0,92** au sommet, **0,04** à droite. Le taux d'échec **croît avec l'amplitude de la dérive** sur toute la moitié droite.",
    "**λ = 8** passe sous la cloche presque partout → zone sûre.",
], size=8)
sec(s, 5.05, 3.94, 4.65, "Ce que cela résout", size=8.5)
bullets(s, 5.05, 4.18, 4.65, 0.95, [
    "Le régime paradoxal — détection fiable à amplitude moyenne, famine à forte amplitude — est la **pente droite de la cloche**. Il figurait dans les données publiées depuis le début, sans explication.",
    "La courbe n'est pas une loi de puissance : terme quadratique en échelle logarithmique **0,500**, intervalle [0,296 ; 0,759], et il **résiste** au retrait des deux extrémités suspectes (0,474 puis 0,592 puis 0,669).",
], size=8)

# =========================================================================
# SLIDE 15 — W5 : LA MOTIVATION
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "W5 — Pourquoi surveiller un modèle qui se répare seul")

sec(s, 0.30, 0.72, 5.45, "Le reproche, et c'était le veto")
add_paragraphs(s, 0.30, 0.96, 5.45, 0.45, [body_runs(
    "Un relecteur, expertise haute, coche « intérêt pour la communauté : non ». Son "
    "argument : une forêt adaptative s'adapte sans qu'on lui adjoigne un détecteur "
    "externe. L'architecture étudiée n'existerait pas.", 8)])
sec(s, 0.30, 1.43, 5.45, "Notre réponse, en trois temps")
add_paragraphs(s, 0.30, 1.67, 5.45, 3.45, [
    body_runs("**1. Trois objectifs, pas un.** S'adapter, c'est réparer le modèle. "
              "Surveiller, c'est savoir que le monde a changé, quand et où. Alarmer, "
              "c'est déclencher un humain, une procédure, un pipeline aval. Trois "
              "fonctions, trois consommateurs. L'article ne traite que les deux "
              "dernières.", 8),
    body_runs("**2. Le problème a un nom ailleurs.** Le flux d'erreur lu par le "
              "moniteur est **endogène** : le classifieur agit en contre-réaction sur "
              "la grandeur même qu'on mesure. C'est le problème canonique de la "
              "détection de défaut en boucle fermée, où un régulateur à action "
              "intégrale masque le défaut aux détecteurs à résidus. Trente ans de "
              "littérature en automatique, un vocabulaire établi, une antériorité qui "
              "protège.", 8),
    body_runs("**3. Le régulateur nomme le danger.** Le règlement européen sur l'IA "
              "impose de traiter les boucles de rétroaction des systèmes qui "
              "continuent d'apprendre après mise sur le marché, et exige une "
              "surveillance après commercialisation. Côté bancaire, la supervision "
              "américaine a renouvelé en avril 2026 son cadre de gestion du risque "
              "modèle, qui impose une surveillance continue indépendante du modèle.", 8),
    body_runs("**Effet** — La question du relecteur reçoit sa réponse dans le "
              "**premier paragraphe** de l'introduction. Un système qui se répare "
              "masque l'incident à son opérateur : c'est le sujet, et il est nommé "
              "comme tel.", 8),
])

s.shapes.add_picture("figures/fig5_boucle_fermee.png", Inches(5.95),
                     Inches(0.72), width=Inches(3.75))
add_rect(s, 5.95, 3.05, 3.75, 0.62, BG_BLUE_LT)
add_text(s, 6.05, 3.09, 3.55, 0.24,
         "Règlement (UE) 2024/1689 sur l'intelligence artificielle",
         size=8, color=TXT_BODY)
tb = add_text(s, 6.05, 3.33, 3.55, 0.28,
              "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
              size=8, color=BLUE)
for p in tb.text_frame.paragraphs:
    for r in p.runs:
        r.font.underline = True

# =========================================================================
# SLIDE 16 — W6 : LA GÉNÉRALITÉ
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "W6 — Artefact de bibliothèque ? Non, mais moins extrême")

sec(s, 0.30, 0.72, 4.70, "Le reproche")
add_paragraphs(s, 0.30, 0.96, 4.70, 0.42, [body_runs(
    "Un classifieur, un détecteur interne, une bibliothèque. Le phénomène pouvait "
    "n'être qu'un effet de configuration.", 8)])
sec(s, 0.30, 1.40, 4.70, "Ce que nous avons fait")
bullets(s, 0.30, 1.64, 4.70, 0.70, [
    "D'autres mécanismes internes que celui d'origine.",
    "Une **seconde implémentation** du classifieur, écrite indépendamment.",
    "Un **second générateur de flux**, construit pour tenir le déséquilibre de classes constant.",
], size=8)
sec(s, 0.30, 2.40, 4.70, "Les résultats")
bullets(s, 0.30, 2.64, 4.70, 2.10, [
    "Le phénomène survit à chaque changement. La course se produit sous la seconde implémentation aux deux points d'ancrage testés.",
    "Mais il est **nettement moins extrême** que la grille d'origine ne le laissait croire. Taux de manqués au seuil élevé : 0,99 à 1,00 sur la famille publiée, **0,33 à 0,77** sous le générateur corrigé.",
    "Et une anomalie disparaît. Au-delà d'un certain saut d'erreur, le budget devenait **négatif** : la forêt adaptée terminait sous son erreur d'avant rupture. Sous le générateur à prior équilibré, ce régime **n'existe pas**. C'était un artefact du déséquilibre de classes, et il est déclaré comme tel.",
], size=8)

s.shapes.add_picture("figures/fig3_generalite_plancher.png", Inches(5.15),
                     Inches(0.72), width=Inches(4.55))
equation_box(s, 5.15, 3.24, 4.55, 0.62,
             "skill = 1 − e_res / min(p ; 1−p)",
             "Le score d'habileté, contre le prédicteur constant. p : proportion de "
             "la classe minoritaire ; e_res : erreur résiduelle de l'ensemble.")
sec(s, 5.15, 3.94, 4.55, "Le corollaire honnête, non demandé", size=8.5)
bullets(s, 5.15, 4.16, 4.55, 0.99, [
    "Au quart droit de la grille d'origine, la classe minoritaire tombe sous 1,8 % du flux. Là, l'ensemble adaptatif **ne bat plus le prédicteur constant** qui répond toujours la classe majoritaire. Score d'habileté négatif à partir de Δe = 0,482, jusqu'à **−3,47**.",
    "Toute erreur résiduelle de cette zone est désormais publiée **avec son plancher trivial à côté**. Un régime dégénéré de classification n'est pas un régime de surveillance.",
], size=8)

# =========================================================================
# SLIDE 17 — W7 : L'IMMUNITÉ RETOURNÉE
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "W7 — L'immunité du détecteur à fenêtres, démontée deux fois")

sec(s, 0.30, 0.72, 5.55, "Le reproche")
add_paragraphs(s, 0.30, 0.96, 5.55, 0.42, [body_runs(
    "Un balayage sur un seul paramètre, un seul flux, et la conclusion : ce détecteur "
    "est « structurellement immunisé ».", 8)])
sec(s, 0.30, 1.40, 5.55, "Ce que nous avons fait")
bullets(s, 0.30, 1.64, 5.55, 0.70, [
    "Balayage complet — grille d'amplitudes entière, tailles de fenêtre, tailles d'échantillon de test, niveaux de fausse alarme, durées de transitoire, tailles d'ensemble.",
    "Et surtout : **égalisation du niveau de fausse alarme**. Comparer trois détecteurs à seuils publiés, c'est comparer trois calibrations.",
], size=8)
sec(s, 0.30, 2.40, 5.55, "Résultat 1 — la comparaison publiée était biaisée")
bullets(s, 0.30, 2.64, 5.55, 2.10, [
    "Au point d'opération de la table principale, le détecteur à fenêtre adaptative était déployé **45 fois plus serré** que le cumulatif, et le détecteur à fenêtres **4,5 fois plus lâche**.",
    "Sur la famille synthétique de référence, ce dernier est **le moins bon des trois** à tous les niveaux publiés : 0,928 pour le cumulatif, 0,885 pour la fenêtre adaptative, 0,713 au mieux pour lui.",
    "À niveau égalisé, il **descend** (0,458 → 0,337) pendant que la fenêtre adaptative **monte** (0,885 → 0,926, délai divisé par deux).",
], size=8)

visual_placeholder(s, 6.00, 0.72, 3.70, 1.90,
    "Tableau à quatre lignes (cumulatif, fenêtre adaptative, fenêtres deux "
    "échantillons, distances entre erreurs) et quatre colonnes (niveau publié, "
    "niveau égalisé, fausses alarmes pré-rupture, rang). Flèches orange dans la "
    "colonne « niveau égalisé » indiquant le sens du changement.")
sec(s, 6.00, 2.72, 3.70,
    "Résultat 2 — sa configuration déployée alarme avant la rupture", size=8.5)
bullets(s, 6.00, 2.98, 3.70, 0.89, [
    "Vérifié contre un détecteur vivant, ré-armé : **8 à 9 alarmes** par fenêtre de 1 000 pas **antérieure** à la rupture, la première vers le pas 99. Taux de fausse alarme pré-rupture de **1,00** à tous les niveaux.",
    "Son score parfait tenait à une particularité du flux de test : son erreur avant rupture est **identiquement nulle**. Rien ne pouvait y produire une fausse alarme.",
], size=7.5)
sec(s, 6.00, 3.92, 3.70,
    "Résultat 3 — le rang d'un détecteur dépend du flux, pas de la famille", size=8.5)
bullets(s, 6.00, 4.24, 3.70, 0.89, [
    "Un quatrième détecteur, fondé sur les distances entre erreurs, change **trois fois de rang** selon le seul taux d'erreur du flux avant rupture : jamais armé quand ce taux est nul, premier à 0,024, dernier à 0,069 avec 93 % de fausses alarmes.",
    "Conséquence de forme, désormais imposée : toute table qui ordonne des familles de moniteurs porte ce taux **en colonne**. Sans lui, elle ordonne des flux.",
], size=7.5)
footer_refs(s, "Raab, Heusinger & Schleif (2020) · Baena-García et al. (2006)")

# =========================================================================
# SLIDE 18 — W8 : VALIDITÉ EXTERNE
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "W8 — Ce que les données réelles disent vraiment")

sec(s, 0.30, 0.72, 4.55, "Le reproche")
add_paragraphs(s, 0.30, 0.96, 4.55, 0.45, [body_runs(
    "Sur données réelles, l'article montrait une inondation de fausses alarmes là où "
    "il annonçait une détection manquée. Et un jeu de données ne produisait aucun "
    "saut d'erreur mesurable.", 8)])
sec(s, 0.30, 1.46, 4.55, "Résultat 1 — l'inondation était un écart de calibration")
bullets(s, 0.30, 1.70, 4.55, 1.60, [
    "L'écart publié, un rapport de **10,57** en défaveur de la forêt adaptative, est reproduit à quatre décimales.",
    "Les deux configurations étaient lues à des seuils qui n'achètent pas le même budget de fausses alarmes : **21 d'un côté, 132 de l'autre**.",
    "À budget de portée égal, le rapport tombe à **1,27**, intervalle [1,16 ; 1,43]. **89,9 %** de l'écart venait du seuil.",
    "Le mécanisme n'est pas la réduction de variance par agrégation : l'écart est maximal là où la fenêtre de calibration est la plus courte, et il **s'inverse** sur les variantes à fenêtre longue. C'est un effet de durée d'observation.",
], size=8)
sec(s, 0.30, 3.36, 4.55, "Résultat 2 — la cellule emblématique détecte tout, au bon seuil")
bullets(s, 0.30, 3.60, 4.55, 1.50, [
    "La cellule affichée à zéro détection sur 1 080 en détecte **1 080 sur 1 080** à λ = 5, précision 1,000, délai moyen **6,05 pas**.",
    "Le détecteur à fenêtres, présenté comme supérieur, met **14 pas**. Le cumulatif le bat d'un facteur deux.",
    "Plafond de preuve de ce flux, mesuré pour la première fois : entre **8 et 15**. Le seuil publié était deux à trois fois trop haut.",
], size=8)

s.shapes.add_picture("figures/fig4_deux_panneaux.png", Inches(5.00),
                     Inches(0.72), width=Inches(4.70))
sec(s, 5.00, 3.14, 4.70, "Résultat 3 — deux flux requalifiés, et l'un renforce l'article", size=8.5)
bullets(s, 5.00, 3.40, 4.70, 0.80, [
    "Le jeu de données financier est un **témoin négatif prouvé** : l'erreur d'un classifieur gelé y vaut 0,0110, exactement le taux de fraude. Aucun pipeline n'y acquiert de signal. Il n'y a pas de transitoire à masquer.",
    "Sur un autre jeu réel, **aucun seuil n'est admissible** jusqu'à 200 : la précision plafonne à 0,333. Frontière du domaine de validité, écrite comme telle, avec ses deux remèdes ouverts.",
], size=8)
sec(s, 5.00, 4.28, 4.70, "Résultat 4 — le protocole, et ce qu'il a coûté", size=8.5)
bullets(s, 5.00, 4.54, 4.70, 0.60, [
    "Une correction pour comparaisons multiples **retire une affirmation** que le manuscrit avait déjà refusé de faire.",
    "Les intervalles de confiance mesuraient la mauvaise composante de variance : **cinq fois trop larges** à un endroit, **trois fois trop étroits** à un autre.",
], size=8)

# =========================================================================
# SLIDE 19 — CE QUE PERSONNE N'AVAIT VU
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "Quatre défauts que les relecteurs n'avaient pas relevés")

defects = [
    (1, BG_PINK, RED, "Le flux de test n'a aucune erreur avant la rupture.",
     "L'expérience phare, 1 080 exécutions, est mesurée sur un flux où il n'existe aucun arbitrage entre détection et fausses alarmes. Cela explique mécaniquement la précision parfaite au bon seuil — et cela impose de dire où la règle de calibration est réellement contrainte."),
    (2, BG_CREAM, ORANGE, "Un effondrement publié est un détecteur qui n'a jamais démarré.",
     "Il exige 30 erreurs pour s'armer ; le flux en produit 9 sur 8 000 pas. Il n'a pas échoué à détecter."),
    (3, BG_BLUE_LT, BLUE, "Le socle d'erreur moyenné sur tout le rodage est biaisé.",
     "Sur l'horizon, cela représente plusieurs unités d'aire — du même ordre que le seuil le plus bas testé. Faute de fenêtre pré-rupture assez longue dans les traces, cette quantité est déclarée non mesurable plutôt que remplacée par une valeur de référence."),
    (4, BG_GREEN_LT, GREEN, "Le facteur d'accélération de l'ensemble n'est pas une constante.",
     "Deux estimateurs légitimes du même effet varient en sens opposé avec l'amplitude. Le texte le dit et l'explique : les lois de délai des deux bras ne gardent pas leur forme."),
]
for i, (num, fill, color, title, body) in enumerate(defects):
    x = 0.30 + (i % 2) * 4.80
    y = 0.72 + (i // 2) * 1.90
    add_rect(s, x, y, 4.60, 1.78, fill)
    lettered_circle(s, x + 0.15, y + 0.13, str(num), color=color, size=0.30,
                    fontsize=11)
    add_text(s, x + 0.58, y + 0.13, 3.90, 0.42, fr(title), size=9, bold=True,
             color=TXT_DARK)
    add_paragraphs(s, x + 0.15, y + 0.62, 4.30, 1.10, [body_runs(body, 8)])

conclusion_band(s, "★ Chacun de ces quatre points est écrit dans le manuscrit. Un "
                  "relecteur qui ouvre le dépôt les trouverait ; autant que "
                  "l'annonce vienne de nous.")

# =========================================================================
# SLIDE 20 — DIVIDER D
# =========================================================================
s = prs.slides.add_slide(BLANK)
divider(s, "D", GREEN, "Ce qui reste", "En suspens, et à ré-auditer")

# =========================================================================
# SLIDE 21 — EN SUSPENS ET À RÉ-AUDITER
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "Points ouverts et résultats à reprendre")

add_rect(s, 0.30, 0.72, 2.90, 4.38, BG_PINK)
add_rect(s, 0.30, 0.72, 2.90, 0.30, RED)
add_text(s, 0.30, 0.72, 2.90, 0.30, "Bloquant", size=9.5, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_text(s, 0.40, 1.12, 2.70, 0.40, "L'audit adversarial du manuscrit assemblé.",
         size=9, bold=True, color=TXT_DARK)
add_paragraphs(s, 0.40, 1.56, 2.70, 3.40, [body_runs(
    "Cinq profils de relecteurs, lancés séparément, sans communication, sur le "
    "document figé : un théoricien des temps d'arrêt absent du panel d'origine, les "
    "successeurs des trois relecteurs critiques, un éditeur de revue. Mandat commun : "
    "chercher la contradiction interne. Quatre renversements de thèse et "
    "soixante-quatre pages : personne n'a encore lu l'ensemble d'un bout à l'autre en "
    "cherchant la faille.", 8)])

add_rect(s, 3.35, 0.72, 3.00, 4.38, BG_CREAM)
add_rect(s, 3.35, 0.72, 3.00, 0.30, ORANGE)
add_text(s, 3.35, 0.72, 3.00, 0.30, "À ré-auditer", size=9.5, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_text(s, 3.45, 1.12, 2.80, 0.40,
         "Résultats dont l'énoncé est plus fragile que les autres",
         size=8.5, bold=True, color=TXT_DARK)
reaudit = [
    "**Le choix de publier deux prédicats au lieu d'un.** La forme unifiée a été refusée par une règle fixée d'avance, à trois dixièmes de point d'écart. Le choix est assumé et argumenté par le mécanisme, mais il n'est pas tranché par une mesure décisive.",
    "**L'exposant de la loi d'amorce.** Déclaré non établi : la médiane n'est pas une loi de puissance sur le domaine valide, et la queue de grille est limitée par la résolution de la mesure.",
    "**Le sommet de la cloche.** Non identifiable à cent graines par amplitude. Le plateau est publié, le point ne l'est pas.",
    "**L'avantage résiduel à l'extrémité dégénérée de la grille.** Les intervalles chevauchent zéro ; la fenêtre de mesure y contient trop peu d'événements pour trancher.",
    "**La frontière sur le jeu réel sans seuil admissible.** Écrite comme limite, ses deux remèdes restent ouverts : désarmer le moniteur après détection, ou travailler sur des flux dont l'erreur revient à sa loi d'origine.",
]
add_paragraphs(s, 3.45, 1.56, 2.80, 3.40,
               [[("▪  ", 8, True, ORANGE)] + body_runs(it, 8) for it in reaudit])

add_rect(s, 6.50, 0.72, 3.20, 4.38, BG_GREEN_LT)
add_rect(s, 6.50, 0.72, 3.20, 0.30, GREEN)
add_text(s, 6.50, 0.72, 3.20, 0.30, "Extension", size=9.5, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_text(s, 6.60, 1.12, 3.00, 0.40, "Hors périmètre de la soumission",
         size=8.5, bold=True, color=TXT_DARK)
add_paragraphs(s, 6.60, 1.56, 3.00, 2.00, [body_runs(
    "**Période réfractaire après alarme.** Seul levier identifié sur l'inondation qui "
    "demande du code neuf. Réservé à la phase de révision.", 8)])

add_rect(s, 3.24, 0.90, 0.015, 4.00, TXT_FAINT)
add_rect(s, 6.39, 0.90, 0.015, 4.00, TXT_FAINT)

# =========================================================================
# SLIDE 22 — ÉTAT DU GEL
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "Le manuscrit est figé — les chiffres de conformité")

add_rect(s, 0.30, 0.72, 4.70, 0.30, TEAL)
add_text(s, 0.30, 0.72, 4.70, 0.30, "  Contrôle", size=9, bold=True, color=WHITE,
         anchor=MSO_ANCHOR.MIDDLE)
add_rect(s, 5.00, 0.72, 4.70, 0.30, TEAL)
add_text(s, 5.00, 0.72, 4.70, 0.30, "  Résultat", size=9, bold=True, color=WHITE,
         anchor=MSO_ANCHOR.MIDDLE)
freeze = [
    ("Suite de tests, dépôt", "**192 / 192**"),
    ("Suite de tests, **depuis l'archive de soumission seule**", "**173 passés, 15 sautés, 0 échec**"),
    ("Empreintes des résultats publiés", "**27 conformes, 7 écarts, tous déclarés et motivés**"),
    ("Compilation du manuscrit", "**64 pages**, zéro référence non résolue"),
    ("PDF reproductible à l'octet", "**Oui** — deux constructions indépendantes, même empreinte"),
]
for i, (ctrl, res) in enumerate(freeze):
    y = 1.02 + i * 0.46
    fill = WHITE if i % 2 == 0 else BG_BLUE_LT
    add_rect(s, 0.30, y, 9.40, 0.46, fill)
    add_paragraphs(s, 0.40, y, 4.55, 0.46, [body_runs(ctrl, 9)],
                   anchor=MSO_ANCHOR.MIDDLE)
    add_paragraphs(s, 5.10, y, 4.55, 0.46, [body_runs(res, 9, TXT_DARK, TEAL_DARK)],
                   anchor=MSO_ANCHOR.MIDDLE)

bullets(s, 0.30, 3.50, 9.40, 0.90, [
    "L'archive de soumission **s'auto-vérifie** : un évaluateur qui la décompresse fait tourner la suite et recompile le papier sans rien d'autre.",
    "Les quinze tests sautés et leurs motifs sont expliqués dans le fichier d'accompagnement. Aucune zone d'ombre.",
    "Chaque nombre du manuscrit est tracé jusqu'au fichier de résultat qui le porte.",
], size=9)
conclusion_band(s, "★ C'est le point fort du dossier auprès d'une revue : le paquet "
                  "de reproductibilité se vérifie tout seul.")

# =========================================================================
# SLIDE 23 — DIVIDER E
# =========================================================================
s = prs.slides.add_slide(BLANK)
divider(s, "E", PURPLE, "Publication", "Revue cible, et solutions de repli")

# =========================================================================
# SLIDE 24 — CONFÉRENCES ET REVUES
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "Revue cible et candidats de repli")

add_rect(s, 0.30, 0.66, 9.40, 1.66, BG_CREAM)
add_rect(s, 0.30, 0.66, 0.05, 1.66, ORANGE)
add_text(s, 0.45, 0.70, 9.15, 0.24,
         "Cible retenue : Machine Learning (Springer), par le Journal Track d'ECML PKDD.",
         size=10, bold=True, color=ORANGE)
add_text(s, 0.45, 0.94, 9.15, 0.20, "Quatre raisons, dans l'ordre de poids.",
         size=8.5, italic=True, color=TXT_BODY)
tb = add_paragraphs(s, 0.45, 1.16, 9.15, 1.10, [
    body_runs("•  **L'algorithme au cœur de l'article y a été publié** — la forêt "
              "adaptative étudiée, Gomes, Bifet, Read et al., Machine Learning 106, "
              "2017. Même revue, même objet, lectorat déjà acquis.  ", 8) +
    [("https://doi.org/10.1007/s10994-017-5642-8", 8, False, BLUE)],
    body_runs("•  **Pas de limite de pages.** Soixante-quatre pages avec annexes de "
              "preuve : aucun format court n'absorbe ce volume.", 8),
    body_runs("•  **Soumission continue**, jalonnée par des dates de coupure, avec "
              "présentation en conférence en cas d'acceptation. Pas d'attente d'un "
              "cycle annuel.", 8),
    body_runs("•  **Simple aveugle**, révisions complètes plutôt qu'une réfutation "
              "d'une page. Un dossier qui a changé de thèse quatre fois a besoin d'un "
              "échange, pas d'un verdict.  ", 8) +
    [("https://ecmlpkdd.org/ — Journal Track", 8, False, BLUE)],
])
underline_urls(tb)

conf_cols = [
    (0.30, 1.50, "Conférence", PP_ALIGN.LEFT),
    (1.80, 0.40, "Rang", PP_ALIGN.CENTER),
    (2.20, 1.02, "Deadline", PP_ALIGN.LEFT),
    (3.22, 0.70, "Sélect.", PP_ALIGN.CENTER),
    (3.92, 1.52, "Format manuscrit", PP_ALIGN.LEFT),
    (5.44, 0.78, "Présentation", PP_ALIGN.CENTER),
    (6.22, 0.72, "Rebuttal", PP_ALIGN.CENTER),
    (6.94, 0.52, "Adéq.", PP_ALIGN.CENTER),
    (7.46, 0.52, "Prio", PP_ALIGN.CENTER),
    (7.98, 1.72, "Commentaire", PP_ALIGN.LEFT),
]
for x, w, htxt, al in conf_cols:
    add_rect(s, x, 2.42, w, 0.26, TEAL)
    add_text(s, x, 2.42, w, 0.26, htxt, size=7, bold=True, color=WHITE,
             align=al, anchor=MSO_ANCHOR.MIDDLE)

conf_rows = [
    ("ECML PKDD 2027 — Journal Track (MLJ)", "A", "≈30 oct. 26 / ≈15 janv. 27 °", "n.c. (revue)", "Springer MLJ, sans limite ; annexes illim.", "Exposé conf.", "Révisions complètes", "★★★★★", "★★★★★", "**Cible retenue**"),
    ("PAKDD 2027", "B", "15 nov. 2026 °", "≈20 % °", "LNAI, ≈13 p. °", "Oral+poster", "Non °", "★★★★☆", "★★★☆☆", "Seule échéance courte"),
    ("KDD 2027 — Cycle 1", "A*", "févr. 2027 °", "≈15–20 % °", "ACM, 9 p. + réf. °", "Oral+poster", "Oui", "★★★☆☆", "★★☆☆☆", "Barre très haute"),
    ("ECML PKDD 2027 — Research", "A", "mars 2027 °", "24 %", "LNCS, ≈16 p. °", "Oral+poster", "Oui", "★★★★★", "★★★★☆", "Repli format court"),
    ("SDM 2027", "A", "avr. 2027 °", "≈25–30 % °", "SIAM, 8 p. ; annexes illim.", "Oral+poster", "Non °", "★★★★☆", "★★★★☆", "Annexes illimitées"),
    ("CIKM 2027", "A", "mai 2027 °", "27 % (2025)", "ACM, ≈9 p. °", "Oral", "Oui °", "★★☆☆☆", "★★☆☆☆", "Thématique peu alignée"),
    ("ICDM 2027", "A*", "juin 2027 °", "≈10–13 %", "IEEE, 10 p. tout inclus", "Reg./short", "Non", "★★★★★", "★★★☆☆", "Retour possible, comité renouvelé"),
    ("DSAA 2027", "B", "juin 2027 °", "≈20–25 % °", "IEEE, 10 p. °", "Oral", "Non °", "★★★☆☆", "★★☆☆☆", "Repli tardif"),
]
for i, row in enumerate(conf_rows):
    y = 2.68 + i * 0.27
    if i == 0:
        fill = BG_CREAM
    else:
        fill = WHITE if i % 2 == 1 else BG_BLUE_LT
    add_rect(s, 0.30, y, 9.40, 0.27, fill)
    if i == 0:
        add_rect(s, 0.30, y, 0.04, 0.27, ORANGE)
    for (x, w, _h, al), cell in zip(conf_cols, row):
        if cell.startswith("**"):
            add_paragraphs(s, x + 0.03, y, w - 0.06, 0.27,
                           [body_runs(cell, 7, TXT_DARK, ORANGE)],
                           anchor=MSO_ANCHOR.MIDDLE)
        else:
            add_text(s, x + 0.03, y, w - 0.06, 0.27, fr(cell), size=7,
                     color=TXT_DARK, align=al, anchor=MSO_ANCHOR.MIDDLE)

add_text(s, 0.30, 4.88, 9.40, 0.20,
         "° Dates 2027 projetées depuis l'édition 2026, à confirmer sur les appels "
         "officiels.", size=7.5, italic=True, color=TXT_FAINT)

# =========================================================================
# SLIDE 25 — ANNEXE 1
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "Annexe — La borne réparée, étape par étape")

bullets(s, 0.30, 0.72, 5.55, 1.90, [
    "Le compteur est une marche réfléchie : il repart de zéro dès que le cumul devient négatif. Franchir le seuil, c'est donc le franchir depuis l'un quelconque des points de remise à zéro.",
    "Une réunion sur ces points de redémarrage, puis l'inégalité maximale de Doob appliquée à la martingale exponentielle, puis la concentration d'Azuma–Hoeffding pour des incréments bornés dans un intervalle de longueur 1.",
    "Le niveau du compteur à l'instant de la rupture n'est pas nul : il suit la loi stationnaire de la marche réfléchie, dont la queue est exponentielle. Il entre dans l'énoncé, il n'est pas escamoté.",
    "La frontière qui en découle fait apparaître la fluctuation explicitement.",
], size=8.5)
equation_box(s, 0.30, 2.75, 5.55, 0.95,
             "λ_starve(W ; ε) = μW + √((W/2)·ln(W/ε))",
             "La frontière de famine. En régime de dérive faible, le second terme "
             "domine le premier.")
visual_placeholder(s, 6.00, 0.72, 3.70, 4.30,
    "Trajectoire en dents de scie du compteur, avec remises à zéro visibles et trois "
    "seuils horizontaux. Zone ombrée sur la fenêtre post-rupture.")

# =========================================================================
# SLIDE 26 — ANNEXE 2
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "Annexe — Pourquoi le budget de preuve forme une cloche")

bullets(s, 0.30, 0.72, 9.40, 1.60, [
    "**Montée, à gauche.** Le saut d'erreur est faible ; le transitoire est long, mais l'excès accumulé par pas est minuscule. Le budget reste bas.",
    "**Plateau, au milieu.** Le saut est assez fort pour accumuler vite, et le transitoire encore assez long pour que l'accumulation se produise.",
    "**Descente, à droite.** Le saut est fort, mais l'adaptation consomme le transitoire plus vite que la marche n'accumule. Et la latence du premier remplacement sature autour de 29 pas : elle ne peut plus raccourcir. L'intégrale rétrécit par le haut, pas par la durée.",
    "La pente locale en échelle logarithmique parcourt un facteur trois sur le domaine valide, mais les points de droite sont limités par la résolution de la médiane : l'ensemble de la queue tient en quatre demi-pas. Aucune pente ne s'y lit, dans aucun sens.",
    "La courbure agrégée, elle, tient : **0,500** [0,296 ; 0,759], et elle **augmente** quand on retire la queue quantifiée.",
], size=8.5)
visual_placeholder(s, 0.30, 2.45, 9.40, 2.65,
    "La cloche, avec trois zones annotées « accumulation lente », « plateau », "
    "« transitoire consommé ». Sous l'axe, une bande grise sur les six dernières "
    "amplitudes annotée « résolution de mesure : 4 demi-pas ».")

# =========================================================================
# SLIDE 27 — ANNEXE 3
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "Annexe — Le retard d'étiquetage")

bullets(s, 0.30, 0.72, 9.40, 1.45, [
    "Un moniteur externe lit un flux d'erreur, donc il lui faut des étiquettes. Elles arrivent rarement à l'instant de la prédiction.",
    "Deux régimes, et ils ne se comportent pas pareil.",
    "**Le moniteur seul est retardé.** Il lit en retard une erreur que le classifieur a déjà commencé à effacer. La fenêtre exploitable rétrécit mécaniquement : la latence pénalise.",
    "**Le classifieur et le moniteur partagent la latence.** Le classifieur apprend aussi en retard, donc il efface plus tard. L'instant d'effacement recule de presque exactement la latence — coefficient mesuré **0,998**. La fenêtre exploitable se **ré-élargit**.",
    "Conséquence de conception : dans un système où les étiquettes arrivent tard pour tout le monde, le retard n'aggrave pas l'angle mort. Dans un système où seul le moniteur attend, il l'aggrave.",
], size=8.5)
s.shapes.add_picture("figures/fig6_retard_etiquetage.png", Inches(0.30),
                     Inches(2.30), width=Inches(9.40))

# =========================================================================
# SLIDE 28 — ANNEXE 4
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "Annexe — Les deux prédicats, et pourquoi ils ne fusionnent pas")

bullets(s, 0.30, 0.72, 5.45, 4.30, [
    "**Un compteur cumulatif dépense une intégrale.** Il additionne l'excès d'erreur pas à pas et compare la somme à son seuil. Ce qu'il lui faut, c'est une aire.",
    "**Un test à deux échantillons dépense du contraste.** Il compare deux fenêtres et n'a besoin que d'un écart assez net à l'intérieur de ce qu'il regarde. Allonger le transitoire au-delà de sa fenêtre ne lui apporte rien.",
    "La mesure tranche : quand l'amplitude augmente, le budget disponible chute de 24,0 à 1,2 pendant que la détection du second monte de 0,00 à 1,00. Un moniteur qui détecte davantage quand son budget rétrécit ne dépense pas ce budget.",
    "Le modèle de contraste reproduit les mesures à **93,1 %** sur la grille entière, contre 85,0 % pour la forme unifiée — et l'écart se creuse exactement là où le transitoire dépasse la fenêtre de lecture.",
    "La généralisation avait été pré-enregistrée avec son seuil d'acceptation. Elle a été refusée par la règle, pas par une préférence.",
], size=8.5)
visual_placeholder(s, 5.90, 0.72, 3.80, 4.30,
    "Deux schémas côte à côte : à gauche, une courbe d'erreur avec l'aire sous la "
    "courbe hachurée, annotée « intégrale » ; à droite, deux fenêtres adjacentes avec "
    "la différence de leurs moyennes en flèche verticale, annotée « contraste ». "
    "Sous les deux, la barre d'accord 93,1 % contre 85,0 %.")

# =========================================================================
# SLIDE 29 — ANNEXE 5
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "Annexe — Ce que le manuscrit publie, et ce qu'il retire")

pub_cols = [
    (0.30, GREEN, "Publié avec sa preuve ou sa mesure", "✓  ", GREEN,
     ["La borne à horizon fini, avec son domaine d'informativité délimité",
      "Le certificat déterministe sur le budget mesuré",
      "La borne sans hypothèse de dépendance",
      "La condition suffisante de calibration, et ses deux prédicats",
      "Le plancher de détectabilité et le seuil opérationnel",
      "La cloche d'évidence et la carte de détection"]),
    (3.49, RED, "Retiré, avec le motif écrit", "✗  ", RED,
     ["Le biconditionnel du principe de découplage",
      "La taille critique d'ensemble",
      "Le substitut rectangulaire du budget de preuve",
      "L'exigence de preuve du détecteur à distances entre erreurs",
      "L'immunité structurelle du détecteur à fenêtres",
      "Toute affirmation de plancher de latence"]),
    (6.68, TXT_BODY, "Déclaré non mesurable", "?  ", TXT_FAINT,
     ["Le biais de fenêtre du socle d'erreur — les traces ne portent pas de phase "
      "pré-rupture assez longue. Aucune constante ne le remplace."]),
]
for x, hdr_color, hdr, mark, mark_color, items in pub_cols:
    add_rect(s, x, 0.72, 3.02, 0.32, hdr_color)
    add_text(s, x, 0.72, 3.02, 0.32, hdr, size=9, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_paragraphs(s, x + 0.05, 1.20, 2.92, 3.90,
                   [[(mark, 8.5, True, mark_color)] + body_runs(it, 8.5)
                    for it in items])

# =========================================================================
# SLIDE 30 — ANNEXE 6 : RÉFÉRENCES
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "Annexe — Références")

def ref_runs(authors, title, tail, url):
    runs = []
    if authors:
        runs.append((authors, 8, False, TXT_BODY))
    if title:
        runs.append((title, 8, False, TXT_DARK, True))
    if tail:
        runs.append((tail, 8, False, TXT_BODY))
    if url:
        runs.append((url, 8, False, BLUE))
    return runs

blocks = [
    ("Apprentissage sur flux", [
        ref_runs("Gomes, Bifet, Read et al. (2017), ", "Adaptive random forests for evolving data stream classification", ", Machine Learning 106 — ", "https://doi.org/10.1007/s10994-017-5642-8"),
        ref_runs("Bifet & Gavaldà (2007), ", "Learning from time-changing data with adaptive windowing", ", SDM", None),
        ref_runs("Montiel, Halford, Mastelini et al. (2021), ", "River: machine learning for streaming data in Python", ", JMLR 22 — ", "https://jmlr.org/papers/v22/20-1380.html"),
        ref_runs("Gama, Žliobaitė, Bifet et al. (2014), ", "A survey on concept drift adaptation", ", ACM Computing Surveys 46 — ", "https://doi.org/10.1145/2523813"),
    ]),
    ("Détection séquentielle de rupture", [
        ref_runs("Page (1954), ", "Continuous inspection schemes", ", Biometrika 41 — ", "https://doi.org/10.1093/biomet/41.1-2.100"),
        ref_runs("Lorden (1971), ", "Procedures for reacting to a change in distribution", ", Annals of Mathematical Statistics 42", None),
        ref_runs("Moustakides (1986), ", "Optimal stopping times for detecting changes in distributions", ", Annals of Statistics 14", None),
        ref_runs("Siegmund (1985), ", "Sequential Analysis", ", Springer", None),
        ref_runs("Tartakovsky, Nikiforov & Basseville (2014), ", "Sequential Analysis", ", CRC Press", None),
    ]),
    ("Concentration et dépendance", [
        ref_runs("Hoeffding (1963), ", "Probability inequalities for sums of bounded random variables", ", JASA 58 — ", "https://doi.org/10.1080/01621459.1963.10500830"),
        ref_runs("Esary, Proschan & Walkup (1967), ", "Association of random variables", ", Annals of Mathematical Statistics 38", None),
        ref_runs("Fine & Gray (1999), ", "A proportional hazards model for the subdistribution of a competing risk", ", JASA 94", None),
    ]),
    ("Détection de défaut en boucle fermée", [
        ref_runs("Chen & Patton (1999), ", "Robust Model-Based Fault Diagnosis for Dynamic Systems", ", Springer", None),
        ref_runs("Isermann (2006), ", "Fault-Diagnosis Systems", ", Springer", None),
    ]),
    ("Cadre réglementaire", [
        ref_runs("Règlement (UE) 2024/1689 sur l'intelligence artificielle — ", None, None, "https://eur-lex.europa.eu/eli/reg/2024/1689/oj"),
    ]),
]
y = 0.72
for hdr, refs in blocks:
    add_text(s, 0.30, y, 9.40, 0.22, hdr, size=9, bold=True, color=ORANGE)
    tb = add_paragraphs(s, 0.30, y + 0.24, 9.40, 0.20 + 0.15 * len(refs),
                       [r for r in refs])
    underline_urls(tb)
    y += 0.30 + 0.15 * len(refs) + 0.06

# =========================================================================
# SAVE
# =========================================================================
out = "2026_09_28_Point_Hebdo_v1.pptx"
prs.save(out)
print(f"Saved: {out}")
print(f"Total slides: {len(prs.slides)}")
