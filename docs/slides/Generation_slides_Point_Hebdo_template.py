"""
Build PPTX for Point Hebdo C.S. du 04/05/2026 — Article v13
Same visual style as 2026_04_20_Point_Hebdo.pptx
"""
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
TOTAL_SLIDES = 11  # will be set after construction

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

# =========================================================================
# SLIDE 1 — TITRE
# =========================================================================
s = prs.slides.add_slide(BLANK)
# Top teal block
add_rect(s, 0.60, 0.50, 8.80, 2.20, TEAL_DARK)
add_paragraphs(s, 0.75, 0.65, 8.50, 2.00, [
    [("Avancées Article ", 28, True, WHITE)],
    [("Blind Spot Paradox", 28, True, WHITE)],
    [("v3 → v13", 26, True, WHITE)],
    [("", 8, False, WHITE)],
    [("Préparation soumission IEEE ICDM 2026", 16, False, WHITE, True)],
])
# Orange accent line
add_rect(s, 0.60, 2.80, 8.80, 0.06, ORANGE)
# Lower blue strip
add_rect(s, 0.00, 3.00, 10.00, 1.80, BLUE_DEEP)
# Orange separator
add_rect(s, 0.60, 3.10, 8.80, 0.46, ORANGE)
add_text(s, 0.70, 3.14, 8.60, 0.38, "Point Hebdo C.S. du 04/05/2026  —  Article v13",
         size=14, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
add_text(s, 0.70, 3.62, 8.60, 0.38, "R. Minato  —  Draft article v13 (IEEEtran 10pt)",
         size=12, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
idx = len(prs.slides)
add_text(s, 9.00, 5.25, 0.80, 0.30, f"{idx}", size=9, color=WHITE,
         align=PP_ALIGN.RIGHT)

# =========================================================================
# SLIDE 2 — PLAN
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "Plan de la présentation", 2)
sections = [
    ("A", ORANGE_LT, "Format & Restructuration",
     "IEEEtran 10pt conference · footnote 3 calibrations PHT"),
    ("B", TEAL, "Renforcement Théorique",
     "Prop 1 reformulée · Annexe A · Order Statistics · Related Work"),
    ("C", RED, "Stratégie Soumission ICDM 2026",
     "Taux acceptation comparés ICDM/NeurIPS/ICML · positionnement vs littérature"),
]
for i, (letter, color, title, desc) in enumerate(sections):
    y = 0.78 + i * 0.92
    lettered_circle(s, 0.50, y, letter, color=color, size=0.55, fontsize=18)
    add_text(s, 1.30, y - 0.02, 8.00, 0.32, title, size=11, bold=True, color=TXT_DARK)
    add_text(s, 1.30, y + 0.32, 8.00, 0.30, desc, size=9, color=TXT_BODY)

# =========================================================================
# SLIDE 3 — DIVIDER A
# =========================================================================
s = prs.slides.add_slide(BLANK)
add_rect(s, 0.00, 1.50, 10.00, 2.60, TEAL)
add_rect(s, 1.20, 1.85, 1.50, 1.50, ORANGE_LT)
add_text(s, 1.20, 1.85, 1.50, 1.50, "A", size=42, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_paragraphs(s, 3.20, 1.90, 6.00, 1.00, [
    [("Format &", 26, True, WHITE)],
    [("Restructuration", 26, True, WHITE)],
])
add_text(s, 3.20, 2.95, 6.00, 0.80,
         "IEEEtran 10pt conference · footnote justifiant les 3 calibrations PHT (λ ∈ {8, 25, 50} / 25 / 15)",
         size=12, color=RGBColor(0xD5, 0xDB, 0xDB))
page_num_only(s, 3)

# =========================================================================
# SLIDE 4 — Migration IEEEtran + Footnote calibrations
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "Migration Format IEEEtran & Justification des 3 Calibrations PHT", 4)
badge(s, "NOUVEAU", color=RED)

# Two columns: avant / après
col_w = 4.45
# AVANT (v3)
add_rect(s, 0.30, 0.75, col_w, 0.35, BG_PINK)
add_text(s, 0.30, 0.75, col_w, 0.35, "  Avant (v3)", size=10, bold=True,
         color=RED, anchor=MSO_ANCHOR.MIDDLE)
add_paragraphs(s, 0.40, 1.15, col_w - 0.10, 1.40, [
    [("\\documentclass[11pt,a4paper]{article}", 9, False, TXT_DARKER, True)],
    [("• 11 pages, marges 2.5 cm", 9, False, TXT_BODY)],
    [("• Figures \\columnwidth simple colonne", 9, False, TXT_BODY)],
    [("• Pas d'éditeur ciblé : généraliste", 9, False, TXT_BODY)],
    [("• Pas de footnote sur calibrations", 9, False, TXT_BODY)],
])

# APRÈS (v13)
add_rect(s, 5.25, 0.75, col_w, 0.35, BG_GREEN_LT)
add_text(s, 5.25, 0.75, col_w, 0.35, "  Après (v13)", size=10, bold=True,
         color=GREEN, anchor=MSO_ANCHOR.MIDDLE)
add_paragraphs(s, 5.35, 1.15, col_w - 0.10, 1.40, [
    [("\\documentclass[10pt,conference]{IEEEtran}", 9, False, TXT_DARKER, True)],
    [("• 10 pages strictes (deadline IEEE)", 9, False, TXT_BODY)],
    [("• Figures figure* sur 2 colonnes", 9, False, TXT_BODY)],
    [("• \\IEEEauthorblockN / \\IEEEauthorblockA", 9, False, TXT_BODY)],
    [("• Footnote dédiée 3 calibrations PHT", 9, False, TXT_BODY)],
])

# Bottom — 3 calibrations footnote summary
add_rect(s, 0.30, 2.75, 9.40, 0.35, BG_BLUE_LT)
add_text(s, 0.30, 2.75, 9.40, 0.35, "  Footnote des 3 calibrations PHT (justification expérimentale)",
         size=10, bold=True, color=TEAL_DARK, anchor=MSO_ANCHOR.MIDDLE)

calibs =[
    ("λ ∈ {8, 25, 50}", "§C2 (instrumented PHT vs ARF)",
     "Sondage threshold-sensitivity du Starvation Effect — couvre la dynamique"),
    ("λ = 25", "§4.4 Crossover (NOUVEAU)",
     "Médiane des 3 calibrations — point opérationnel neutre pour le crossover littérature"),
    ("λ = 15", "§ProteuS (financier)",
     "Calibré empiriquement contre la volatilité pré-drift (FA ≤ 1 par fenêtre warm-up)"),
]
for i, (lam, sec, desc) in enumerate(calibs):
    y = 3.20 + i * 0.55
    vertical_bar(s, 0.40, y, color=BLUE, height=0.45)
    add_multi_text(s, 0.65, y, 9.10, 0.45,[
        (lam + "  ", 10, True, BLUE),
        ("(" + sec + ")  — ", 9, False, TXT_DARK),
        (desc, 9, False, TXT_BODY),
    ], anchor=MSO_ANCHOR.MIDDLE)
add_rect(s, 0.30, 4.78, 9.40, 0.32, BG_CREAM)
add_text(s, 0.40, 4.78, 9.30, 0.32,
         "★ La signature blind spot manifeste sous les 3 calibrations → pas un artefact de tuning",
         size=10, bold=True, color=ORANGE, anchor=MSO_ANCHOR.MIDDLE)

# =========================================================================
# SLIDE 5 — DIVIDER B
# =========================================================================
s = prs.slides.add_slide(BLANK)
add_rect(s, 0.00, 1.50, 10.00, 2.60, TEAL)
add_rect(s, 1.20, 1.85, 1.50, 1.50, BLUE)
add_text(s, 1.20, 1.85, 1.50, 1.50, "B", size=42, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_paragraphs(s, 3.20, 1.90, 6.00, 1.00, [
    [("Renforcement", 26, True, WHITE)],
    [("Théorique", 26, True, WHITE)],
])
add_text(s, 3.20, 2.95, 6.00, 0.80,
         "Prop 1 reformulée · Annexe A renforcée · Order Statistics · §2.3 Related Work",
         size=12, color=RGBColor(0xD5, 0xDB, 0xDB))
page_num_only(s, 5)

# =========================================================================
# SLIDE 6 — Reformulation Proposition 1
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "Prop 1 — Sufficient Condition in Expectation", 6)
badge(s, "RÉÉCRIT", color=RED, w=0.95)

# Two columns
# v3 (left, faulty)
add_rect(s, 0.30, 0.75, 4.45, 0.35, BG_PINK)
add_text(s, 0.30, 0.75, 4.45, 0.35, "  v3 — Énoncé déterministe (FAUX)",
         size=10, bold=True, color=RED, anchor=MSO_ANCHOR.MIDDLE)
add_paragraphs(s, 0.35, 1.20, 4.40, 1.50, [
    [("Condition affirmée :", 10, True, TXT_DARK)],
    [("τ_ARF < λ / (Δe − δ_P)", 9, False, TXT_DARKER, True)],
    [("⇒ missed detection (déterministe)", 9, False, TXT_BODY, True)],
    [("", 8, False, TXT_BODY)],
    [("⚠ Faux : S* est une variable aléatoire,", 9, False, RED)],
    [("pas son espérance — fluctuations stochastiques", 9, False, RED)],[("peuvent dépasser λ même si E[S*] < λ.", 9, False, RED)],
])

# v13 (right, correct)
add_rect(s, 5.25, 0.75, 4.45, 0.35, BG_GREEN_LT)
add_text(s, 5.25, 0.75, 4.45, 0.35, "  v13 — Borne Markov (CORRECT)",
         size=10, bold=True, color=GREEN, anchor=MSO_ANCHOR.MIDDLE)
add_paragraphs(s, 5.30, 1.20, 4.40, 1.80, [
    [("Définition : S* := sup_{t∈[τ*, τ*+τ_ARF]} S_t", 9, False, TXT_BODY)],
    [("", 4, False, TXT_BODY)],
    [("Borne Markov sur sub-martingale :", 10, True, TXT_DARK)],[("P(S* ≥ λ)  ≤  τ_ARF · (Δe − δ_P) / λ", 9, False, TXT_DARKER, True)],
    [("", 4, False, TXT_BODY)],
    [("Régime starvation typique :", 10, True, TXT_DARK)],[("τ_ARF · (Δe − δ_P) ≪ λ", 9, False, TXT_DARKER, True)],
])

# LibreOffice Math reference box
add_rect(s, 0.30, 3.30, 9.40, 1.40, BG_BLUE_LT)
add_text(s, 0.30, 3.30, 9.40, 0.30, "  Code LibreOffice Math (v13)", size=10, bold=True,
         color=TEAL_DARK, anchor=MSO_ANCHOR.MIDDLE)
add_paragraphs(s, 0.40, 3.65, 9.20, 1.00, [[("P { left ( S^* >= %lambda right ) } <= { %tau_ARF cdot ( %DELTA e - %delta _P ) } over %lambda",
      9, False, TXT_DARKER, True)],[("", 4, False, TXT_DARKER)],[("Post-transient (t > τ*+τ_ARF) : S_t devient supermartingale (drift négatif − δ_P),",
      9, False, TXT_BODY)],[("draine la statistique vers 0 → pas de détection tardive (Doob's maximal inequality).",
      9, False, TXT_BODY)],
])

footer_refs(s, "Tartakovsky et al. (2014, Sequential Analysis) · Markov inequality on sub-martingales · Doob (1953)")

# =========================================================================
# SLIDE 7 — Remark 4 Sufficiency not Necessity
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "Remark 4 — Sufficiency, not Necessity", 7)
badge(s, "NOUVEAU", color=RED)

add_rect(s, 0.30, 0.75, 9.40, 0.35, BG_BLUE_LT)
add_text(s, 0.30, 0.75, 9.40, 0.35,
         "  La borne Markov (Prop 1) est suffisante mais NON nécessaire pour échec de détection",
         size=11, bold=True, color=TEAL_DARK, anchor=MSO_ANCHOR.MIDDLE)

points = [
    (TEAL, "Asymétrie logique",
     "(E[S*] < λ) ⇒ proba détection bornée loin de 1, MAIS E[S*] ≥ λ n'implique pas détection certaine"),
    (BLUE, "Fluctuations stochastiques",
     "S_t peut occasionnellement dépasser λ même quand son espérance reste sous le seuil — le bruit Bernoulli y contribue"),
    (ORANGE_LT, "Bornes Doob plus fines",
     "Tartakovsky (2014, Sequential Analysis) raffine la constante via supremum-of-random-walk bounds — préserve le scaling"),
    (RED, "Conséquence pour §4.4",
     "La phase transition empirique observée à Δe ≈ 0.25 n'est PAS prédictible depuis l'Eq. 6 seule — désamorce les attentes de fermeture analytique"),
]
for i, (color, title, desc) in enumerate(points):
    y = 1.30 + i * 0.85
    vertical_bar(s, 0.40, y, color=color, height=0.65)
    add_text(s, 0.65, y - 0.02, 9.00, 0.28, title, size=10, bold=True, color=TXT_DARK)
    add_text(s, 0.65, y + 0.26, 9.00, 0.45, desc, size=9, color=TXT_BODY)

footer_refs(s, "Tartakovsky et al. (2014) · Doob (1953) · Williams (1991, Probability with Martingales)")

# =========================================================================
# SLIDE 8 — Annexe A renforcée
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "Annexe A — Preuve renforcée (martingale + Markov + Doob)", 8)
badge(s, "RÉÉCRIT", color=RED, w=0.95)

# v3 vs v13 mini
add_rect(s, 0.30, 0.75, 9.40, 0.30, BG_BLUE_LT)
add_text(s, 0.30, 0.75, 9.40, 0.30, "  Décomposition formelle de la preuve (v13)",
         size=10, bold=True, color=TEAL_DARK, anchor=MSO_ANCHOR.MIDDLE)

# Random walk definition
add_paragraphs(s, 0.35, 1.15, 9.30, 0.50,[
    [("1. Marche aléatoire centrée non-réfléchie :", 10, True, TXT_DARK)],
    [("S̃_t := Σ_{s=τ*}^{t} (e_s − p_0 − δ_P),     t ∈ [τ*, τ*+τ_ARF]",
      9, False, TXT_DARKER, True)],
])

# Inequality
add_paragraphs(s, 0.35, 1.85, 9.30, 0.50,[
    [("2. Comparaison réflexion vs centré (sur la fenêtre transitoire) :", 10, True, TXT_DARK)],
    [("sup_t S_t ≤ 2 sup_t |S̃_t − E[S̃_t]| + μ τ_ARF,    μ := Δe − δ_P", 9, False, TXT_DARKER, True)],
])

# Markov bound
add_paragraphs(s, 0.35, 2.60, 9.30, 0.50, [
    [("3. Markov sur sub-martingale (E[S_{τ*+τ_ARF}] = μ τ_ARF) :", 10, True, TXT_DARK)],
    [("P(S* ≥ λ)  ≤  (2σ √τ_ARF + μ τ_ARF) / λ,    σ² ≤ 1/4 (Bernoulli)",
    9, False, TXT_DARKER, True)],
])

# Post-transient
add_paragraphs(s, 0.35, 3.30, 9.30, 0.50, [
    [("4. Post-transient (t > τ*+τ_ARF) : drift bascule à −δ_P :", 10, True, TXT_DARK)],
    [("S_t devient supermartingale → Doob : P(sup_{t > τ*+τ_ARF} S_t ≥ λ) → 0  □",
      9, False, TXT_DARKER, True)],
])

# Comparison block
add_rect(s, 0.30, 4.05, 9.40, 1.05, BG_PINK)
add_paragraphs(s, 0.40, 4.10, 9.20, 0.95, [
    [("v3 → v13 — Saut de rigueur :", 10, True, RED)],[("• v3 : preuve par linéarité de l'espérance uniquement (E[S_max] = τ_ARF·(Δe−δ_P)) — ignore la nature aléatoire",
      9, False, TXT_BODY)],[("• v13 : sub-martingale + Markov supremum + post-transient supermartingale + Doob inequality",
      9, False, TXT_BODY)],[("• Référence ajoutée : Tartakovsky et al. (2014) pour Doob's maximal inequality sur supermartingales",
      9, False, TXT_BODY)],
])
footer_refs(s, "Tartakovsky et al. (2014, Sequential Analysis) · Doob (1953) · variance bound Bernoulli σ² ≤ 1/4")

# =========================================================================
# SLIDE 9 — DIVIDER C
# =========================================================================
s = prs.slides.add_slide(BLANK)
add_rect(s, 0.00, 1.50, 10.00, 2.60, TEAL)
add_rect(s, 1.20, 1.85, 1.50, 1.50, RED)
add_text(s, 1.20, 1.85, 1.50, 1.50, "C", size=42, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_paragraphs(s, 3.20, 1.90, 6.00, 1.00, [
    [("Stratégie Soumission", 24, True, WHITE)],
    [("ICDM 2026", 24, True, WHITE)],
])
add_text(s, 3.20, 3.00, 6.00, 0.80,
         "Comparaison taux acceptation ICDM / NeurIPS / ICML · positionnement vs littérature",
         size=12, color=RGBColor(0xD5, 0xDB, 0xDB))
page_num_only(s, 9)

# =========================================================================
# SLIDE 10 — Comparaison taux acceptation
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "ICDM 2026 — Comparaison Taux Acceptation Conférences Majeures", 10)
badge(s, "ANALYSE", color=BLUE, w=1.00)

# Table header
add_rect(s, 0.30, 0.75, 9.40, 0.35, TEAL)
headers = [(0.30, 2.20, "Conférence (édition)"),
           (2.50, 1.40, "Soumissions"),
           (3.90, 1.55, "Regular Accept"),
           (5.45, 1.55, "Overall Accept"),
           (7.00, 2.70, "Profil")]
for x, w, text in headers:
    add_text(s, x, 0.75, w, 0.35, text, size=10, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# Rows
data_rows = [
    ("ICDM 2024", "604",   "67 (11.07%)",  "118 (19.54%)", "Petit, très sélectif", BG_GREEN_LT, GREEN),
    ("ICDM 2025", "785",   "106 (13.50%)", "176 (22.42%)", "Tendance haussière",   BG_GREEN_LT, GREEN),
    ("ICDM moy. 10 ans", "~860",  "~9–12%",  "~19–22%",   "Spécialisé data mining", BG_GREEN_LT, GREEN),
    ("NeurIPS 2024", "15 671", "—",          "4 044 (25.8%)", "Massif, généraliste ML", BG_BLUE_LT, BLUE),
    ("NeurIPS 2023", "13 330", "—",          "3 218 (26.1%)", "Massif, généraliste ML", BG_BLUE_LT, BLUE),
    ("ICML 2024",    "9 473",  "—",          "2 609 (27.5%)", "Massif, généraliste ML", BG_BLUE_LT, BLUE),
]
for i, (conf, sub, reg, ov, profile, bg, color_text) in enumerate(data_rows):
    y = 1.10 + i * 0.32
    add_rect(s, 0.30, y, 9.40, 0.32, bg)
    add_text(s, 0.35, y, 2.20, 0.32, conf, size=9, bold=True, color=color_text,
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, 2.50, y, 1.40, 0.32, sub, size=9, color=TXT_DARK,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, 3.90, y, 1.55, 0.32, reg, size=9, color=TXT_DARK,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, 5.45, y, 1.55, 0.32, ov, size=9, color=TXT_DARK,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, 7.00, y, 2.70, 0.32, profile, size=9, italic=True, color=TXT_BODY,
             anchor=MSO_ANCHOR.MIDDLE)

# Strategic reading
add_rect(s, 0.30, 3.10, 9.40, 0.32, BG_CREAM)
add_text(s, 0.30, 3.10, 9.40, 0.32, "  Lecture stratégique pour Blind Spot Paradox",
         size=10, bold=True, color=ORANGE, anchor=MSO_ANCHOR.MIDDLE)
add_paragraphs(s, 0.35, 3.50, 9.30, 1.65, [
    [("• ICDM regular plus sélectif que NeurIPS / ICML overall (11% vs 25–27%) → barre haute en absolu",
      9, False, TXT_BODY)],[("• MAIS volume bien plus faible (604 vs 9 473–15 671) → moindre concurrence absolue · papiers reviewer-vus 2-3×",
      9, False, TXT_BODY)],[("• ICDM = data mining thématique → alignement parfait avec drift detection/streams (vs niche à NeurIPS/ICML)",
      9, False, TXT_BODY)],[("• Format 10 pages strict IEEE = compatible (article v13 fait 10 pages exactes)",
      9, False, TXT_BODY)],[("• ★ Fallback ICDM short paper : 51/604 short en 2024 → second filet de sécurité crédible",
      9, True, GREEN)],
])

footer_refs(s, "Sources : icdm.zhonghuapu.com (10 ans) · NeurIPS Fact Sheet 2024 · ICML 2024 Call (icml.cc) · papercopilot")

# =========================================================================
# SLIDE 11 — Positionnement vs littérature
# =========================================================================
s = prs.slides.add_slide(BLANK)
header_bar(s, "Positionnement vs Littérature ICDM / NeurIPS / ICML", 11)
badge(s, "ANALYSE", color=BLUE, w=1.00)

# Three columns
col_w = 3.13
cols = [
    (TEAL, "ICDM (data mining)",
     [("Précédents drift detection :", 10, True, TXT_DARK),
      ("FAE (2014), DESDD (2019),", 9, False, TXT_BODY),
      ("MDDM (2017), LFR, sdde (2022)", 9, False, TXT_BODY),
      ("", 6, False, TXT_BODY),
      ("Limitation commune :", 10, True, TXT_DARK),
      ("TOUS dans paradigme coopératif", 9, False, TXT_BODY),
      ("détecteur-serve-classifieur", 9, False, TXT_BODY),
      ("", 6, False, TXT_BODY),
      ("Le plus proche en esprit :", 10, True, TXT_DARK),
      ("Stirling et al. (2018) — pas ICDM —", 9, False, TXT_BODY),
      ("internal detector vs accuracy SEUL,", 9, False, TXT_BODY),
      ("pas monitoring reliability", 9, False, TXT_BODY),
      ]),
    (BLUE, "NeurIPS / ICML (ML général)",
     [("Récents en drift / shift :", 10, True, TXT_DARK),
      ("Performative Drift (CB-PDD,", 9, False, TXT_BODY),
      ("ECML-PKDD 2024)", 9, False, TXT_BODY),
      ("Adversarial Attacks for Drift", 9, False, TXT_BODY),
      ("Detection (ESANN 2024)", 9, False, TXT_BODY),
      ("", 6, False, TXT_BODY),
      ("Focus mainstream NeurIPS/ICML :", 10, True, TXT_DARK),
      ("• Out-of-distribution detection", 9, False, TXT_BODY),
      ("• Covariate shift / domain adapt.", 9, False, TXT_BODY),
      ("• Pas streaming online drift", 9, False, TXT_BODY),
      ("", 6, False, TXT_BODY),
      ("→ Race condition interne/externe", 10, True, RED),
      ("   non documentée à ces venues", 9, False, RED)]),
    (GREEN, "Verdict Originalité (ICDM 2026)",
     [("✓ Aucun antécédent direct", 10, True, GREEN),
      ("dans les 3 venues majeures", 9, False, TXT_BODY),
      ("", 6, False, TXT_BODY),
      ("✓ Validation empirique sérieuse", 10, True, GREEN),
      ("2 000 + 360 runs instrumented", 9, False, TXT_BODY),
      ("Multi-seed bootstrap robust", 9, False, TXT_BODY),
      ("", 6, False, TXT_BODY),
      ("✓ Support théorique formel", 10, True, GREEN),
      ("Prop 1 Markov + M_crit + Decoupling", 9, False, TXT_BODY),
      ("", 6, False, TXT_BODY),
      ("✓ Solution constructive", 10, True, GREEN),
      ("Static RF — utilité applicative", 9, False, TXT_BODY),
      ]),
]
for i, (color, title, bullets) in enumerate(cols):
    x = 0.20 + i * (col_w + 0.10)
    add_rect(s, x, 0.75, col_w, 0.32, color)
    add_text(s, x, 0.75, col_w, 0.32, title, size=11, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    paragraphs = [[b] for b in bullets]
    add_paragraphs(s, x + 0.05, 1.15, col_w - 0.10, 3.85, paragraphs)

# Footer conclusion
add_rect(s, 0.30, 4.85, 9.40, 0.27, BG_CREAM)
add_text(s, 0.30, 4.85, 9.40, 0.27,
         "★ Synthèse : papier original + thématique alignée + validation rigoureuse → ICDM 2026 plausible (regular ou short fallback)",
         size=9, bold=True, color=ORANGE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# =========================================================================
# SAVE
# =========================================================================
out = "/home/m53/2026_05_04_Point_Hebdo_light.pptx"
prs.save(out)
print(f"Saved: {out}")
print(f"Total slides: {len(prs.slides)}")