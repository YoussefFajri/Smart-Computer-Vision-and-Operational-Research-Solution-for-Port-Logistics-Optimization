import sys
import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

print("python-pptx version:", pptx.__version__)

def create_presentation(output_path):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # Blank layout

    # Palette : Clean Professional White & Executive Blue/Orange (Design Référence)
    BLUE_MAIN = RGBColor(0, 82, 165)        # Royal Deep Blue #0052A5
    ORANGE_ACCENT = RGBColor(255, 107, 0)   # Vibrant Orange #FF6B00
    DARK_TEXT = RGBColor(30, 41, 59)        # Slate Dark #1E293B
    MUTED_TEXT = RGBColor(148, 163, 184)    # Gray #94A3B8
    CARD_BG = RGBColor(248, 250, 252)       # Light Gray-Blue #F8FAFC
    CARD_BORDER = RGBColor(226, 232, 240)   # Border #E2E8F0
    WHITE = RGBColor(255, 255, 255)
    GREEN_ACCENT = RGBColor(16, 185, 129)

    # Base paths
    base_dir = r"d:\Mersa_pfe\template_D3SI"
    img_dir = os.path.join(base_dir, "images")

    logo_marsa = os.path.join(img_dir, "logo_marsa.png")
    univ_logo = os.path.join(base_dir, "universite.png")
    repport_logo = os.path.join(base_dir, "repport.png")
    faculte_logo = os.path.join(base_dir, "faculte.jpg")
    port_bg = os.path.join(base_dir, "repportbg.png")

    arch_diag = os.path.join(img_dir, "architecture_diagram_white.png")
    if not os.path.exists(arch_diag):
        arch_diag = os.path.join(img_dir, "architecture_diagram.png")

    db_schema = os.path.join(img_dir, "database_schema.png")
    dash_overview = os.path.join(img_dir, "dashboard_overview.png")
    ocr_page = os.path.join(img_dir, "ocr_detection_page.png")
    yard_3d = os.path.join(img_dir, "yard_3d_view.png")

    sections = [
        "Introduction générale",
        "Structure d'accueil",
        "Problématique",
        "Méthodologie & Architecture",
        "Réalisation & Résultats",
        "Conclusion & Perspectives"
    ]

    def add_top_header(slide, section_label, title_text):
        # Background canvas 100% White
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = WHITE
        bg.line.fill.background()

        # Category tracker (e.g. 1 · INTRODUCTION GÉNÉRALE)
        tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(10.0), Inches(0.35))
        tf_cat = tb_cat.text_frame
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = section_label.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = MUTED_TEXT

        # Main Title (Blue)
        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(10.5), Inches(0.6))
        tf_title = tb_title.text_frame
        tf_title.word_wrap = True
        p_t = tf_title.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = BLUE_MAIN

        # Double accent line (Blue + Orange)
        bar_b = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.4), Inches(1.2), Inches(0.06))
        bar_b.fill.solid()
        bar_b.fill.fore_color.rgb = BLUE_MAIN
        bar_b.line.fill.background()

        bar_o = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.4), Inches(0.4), Inches(0.06))
        bar_o.fill.solid()
        bar_o.fill.fore_color.rgb = ORANGE_ACCENT
        bar_o.line.fill.background()

        if os.path.exists(logo_marsa):
            slide.shapes.add_picture(logo_marsa, Inches(11.6), Inches(0.4), height=Inches(0.8))

    def add_bottom_breadcrumb(slide, active_index=0):
        # Footer breadcrumb line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.9), Inches(11.733), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = CARD_BORDER
        line.line.fill.background()

        # Breadcrumb items
        total = len(sections)
        step_w = 11.733 / total
        for i, sec_name in enumerate(sections):
            x = 0.8 + i * step_w
            if i == active_index:
                badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(6.98), Inches(step_w - 0.1), Inches(0.35))
                badge.fill.solid()
                badge.fill.fore_color.rgb = RGBColor(255, 247, 237)
                badge.line.color.rgb = ORANGE_ACCENT
                tf = badge.text_frame
                p = tf.paragraphs[0]
                p.text = sec_name
                p.font.size = Pt(8.5)
                p.font.bold = True
                p.font.color.rgb = ORANGE_ACCENT
                p.alignment = PP_ALIGN.CENTER
            else:
                tb = slide.shapes.add_textbox(Inches(x), Inches(6.98), Inches(step_w - 0.1), Inches(0.35))
                tf = tb.text_frame
                p = tf.paragraphs[0]
                p.text = sec_name
                p.font.size = Pt(8.5)
                p.font.color.rgb = MUTED_TEXT
                p.alignment = PP_ALIGN.CENTER

    def add_card_box(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1)
        return card

    def add_takeaway_banner(slide, text, top=6.2):
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(top), Inches(11.733), Inches(0.5))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.text = text
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.italic = True
        p.font.color.rgb = BLUE_MAIN
        p.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 1: Title Slide (Référence PDF)
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = WHITE
    bg1.line.fill.background()

    # Header University text
    tb_univ = s1.shapes.add_textbox(Inches(2.5), Inches(0.3), Inches(8.333), Inches(0.9))
    tf_u = tb_univ.text_frame
    tf_u.word_wrap = True
    pu = tf_u.paragraphs[0]
    pu.text = "Université Sultan Moulay Slimane\nFaculté Polydisciplinaire de Béni Mellal\nDépartement des technologies nouvelles"
    pu.font.size = Pt(11)
    pu.font.bold = True
    pu.font.color.rgb = DARK_TEXT
    pu.alignment = PP_ALIGN.CENTER

    if os.path.exists(univ_logo):
        s1.shapes.add_picture(univ_logo, Inches(0.8), Inches(0.3), height=Inches(0.8))
    if os.path.exists(faculte_logo):
        s1.shapes.add_picture(faculte_logo, Inches(11.5), Inches(0.3), height=Inches(0.8))

    # Category Subtitle
    tb_sub = s1.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(0.4))
    tf_sub = tb_sub.text_frame
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = "PROJET DE FIN D'ÉTUDES, MASTER EN DATA SCIENCE ET SÉCURITÉ DES SYSTÈMES D'INFORMATION"
    p_sub.font.size = Pt(9.5)
    p_sub.font.bold = True
    p_sub.font.color.rgb = MUTED_TEXT
    p_sub.alignment = PP_ALIGN.CENTER

    # Title Card Box
    c1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.8), Inches(10.933), Inches(2.2))
    c1.fill.solid()
    c1.fill.fore_color.rgb = WHITE
    c1.line.color.rgb = BLUE_MAIN
    c1.line.width = Pt(2)

    tb_t = s1.shapes.add_textbox(Inches(1.4), Inches(1.95), Inches(10.533), Inches(1.9))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True

    pt1 = tf_t.paragraphs[0]
    pt1.text = "Conception et réalisation d'un système intelligent de vision par ordinateur et d'optimisation logistique portuaire"
    pt1.font.size = Pt(20)
    pt1.font.bold = True
    pt1.font.color.rgb = BLUE_MAIN
    pt1.alignment = PP_ALIGN.CENTER

    pt2 = tf_t.add_paragraph()
    pt2.text = "Automatisation de la gestion des conteneurs par IA pour Marsa Maroc"
    pt2.font.size = Pt(14)
    pt2.font.bold = True
    pt2.font.color.rgb = BLUE_MAIN
    pt2.alignment = PP_ALIGN.CENTER
    pt2.space_before = Pt(8)

    # Presenter & Supervisors
    tb_inf = s1.shapes.add_textbox(Inches(1.2), Inches(4.1), Inches(10.933), Inches(0.8))
    tf_inf = tb_inf.text_frame
    p_inf = tf_inf.paragraphs[0]
    p_inf.text = "Présenté par :  FAJRI Youssef                       Sous la direction de :  Pr. KICH Ismail"
    p_inf.font.size = Pt(12)
    p_inf.font.bold = True
    p_inf.font.color.rgb = DARK_TEXT
    p_inf.alignment = PP_ALIGN.CENTER

    # Host Company Box
    c_company = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.5), Inches(4.9), Inches(8.333), Inches(1.3))
    c_company.fill.solid()
    c_company.fill.fore_color.rgb = CARD_BG
    c_company.line.color.rgb = CARD_BORDER

    if os.path.exists(repport_logo):
        s1.shapes.add_picture(repport_logo, Inches(2.8), Inches(5.15), height=Inches(0.8))

    tb_c = s1.shapes.add_textbox(Inches(4.5), Inches(5.15), Inches(6.0), Inches(0.8))
    tf_c = tb_c.text_frame
    pc1 = tf_c.paragraphs[0]
    pc1.text = "Organisme d'accueil : Marsa Maroc"
    pc1.font.size = Pt(11)
    pc1.font.bold = True
    pc1.font.color.rgb = BLUE_MAIN

    pc2 = tf_c.add_paragraph()
    pc2.text = "Encadrant professionnel : M. Mohamed QODSI"
    pc2.font.size = Pt(11)
    pc2.font.color.rgb = DARK_TEXT

    # Year
    tb_yr = s1.shapes.add_textbox(Inches(0.8), Inches(6.5), Inches(11.733), Inches(0.4))
    tf_yr = tb_yr.text_frame
    pyr = tf_yr.paragraphs[0]
    pyr.text = "Année Universitaire 2025 – 2026"
    pyr.font.size = Pt(10)
    pyr.font.color.rgb = MUTED_TEXT
    pyr.alignment = PP_ALIGN.CENTER


    # ==========================================
    # SLIDE 2: Sommaire / Plan (Référence PDF)
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    add_top_header(s2, "SOMMAIRE", "Plan de la présentation")

    plan_items = [
        ("1", "Introduction générale", "Contexte, choix, motivation, présentation du secteur logistique"),
        ("2", "Structure d'accueil", "Marsa Maroc : chiffres-clés et terminaux portuaires"),
        ("3", "Problématique", "Saisie manuelle ISO 6346 & Phénomène de Re-handling"),
        ("4", "Méthodologie & Architecture", "Démarche, YOLOv8/OCR, Kafka, Recuit Simulé & Docker"),
        ("5", "Réalisation & Résultats", "Implémentation, démonstration Jumeau 3D et évaluations"),
        ("6", "Conclusion & Perspectives", "Bilan opérationnel et perspectives Smart Port")
    ]

    for i, (num, title, desc) in enumerate(plan_items):
        col = i % 2
        row = i // 2
        x = 0.8 + col * 6.0
        y = 1.8 + row * 1.5

        # Circle Badge
        badge = s2.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(0.7), Inches(0.7))
        badge.fill.solid()
        badge.fill.fore_color.rgb = BLUE_MAIN
        badge.line.fill.background()
        tf = badge.text_frame
        p = tf.paragraphs[0]
        p.text = num
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

        # Content text
        tb = s2.shapes.add_textbox(Inches(x + 0.9), Inches(y), Inches(4.8), Inches(1.1))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = DARK_TEXT

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = MUTED_TEXT

    add_bottom_breadcrumb(s2, 0)


    # ==========================================
    # SLIDE 3: Contexte & secteur (Référence PDF)
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    add_top_header(s3, "1 · INTRODUCTION GÉNÉRALE", "Contexte & secteur logistique portuaire")

    add_card_box(s3, 0.8, 1.8, 5.6, 3.8)
    tb = s3.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(3.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Le secteur en transformation"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = BLUE_MAIN

    bullets3_1 = [
        "Digitalisation croissante du commerce maritime mondial.",
        "Le conteneur ISO : bien plus qu'une boîte métallique, un flux d'information stratégique.",
        "Impératif de réduction des délais d'escale pour les navires de grande capacité."
    ]
    for b in bullets3_1:
        p = tf.add_paragraph()
        p.text = "▪ " + b
        p.font.size = Pt(11)
        p.font.color.rgb = DARK_TEXT
        p.space_before = Pt(8)

    add_card_box(s3, 6.8, 1.8, 5.733, 3.8)
    tb2 = s3.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.333), Inches(3.4))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = "Le défi opérationnel"
    p2.font.size = Pt(14)
    p2.font.bold = True
    p2.font.color.rgb = BLUE_MAIN

    bullets3_2 = [
        "Volume important de conteneurs EVP traités sous forte contrainte de temps.",
        "Suivi et contrôle d'accès encore largement manuels sous le quai.",
        "Les outils classiques atteignent leurs limites face à la complexité croissante."
    ]
    for b in bullets3_2:
        p = tf2.add_paragraph()
        p.text = "▪ " + b
        p.font.size = Pt(11)
        p.font.color.rgb = DARK_TEXT
        p.space_before = Pt(8)

    add_takeaway_banner(s3, "Un secteur riche en données, mais dont le pilotage reste à automatiser.")
    add_bottom_breadcrumb(s3, 0)


    # ==========================================
    # SLIDE 4: Choix & motivation (Référence PDF)
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    add_top_header(s4, "1 · INTRODUCTION GÉNÉRALE", "Choix & motivation du projet")

    add_card_box(s4, 0.8, 1.8, 5.6, 3.8)
    tb = s4.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(3.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "La motivation"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = BLUE_MAIN

    b4_1 = [
        "Besoin croissant d'automatisation intelligente identifié sous les portiques quai STS.",
        "Saisie manuelle sujette aux erreurs d'inattention et à la mauvaise visibilité nocturne.",
        "Nécessité d'une réactivité accrue face au goulot d'étranglement du stockage au parc."
    ]
    for b in b4_1:
        p = tf.add_paragraph()
        p.text = "▪ " + b
        p.font.size = Pt(11)
        p.font.color.rgb = DARK_TEXT
        p.space_before = Pt(8)

    add_card_box(s4, 6.8, 1.8, 5.733, 3.8)
    tb2 = s4.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.333), Inches(3.4))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = "Le choix retenu"
    p2.font.size = Pt(14)
    p2.font.bold = True
    p2.font.color.rgb = BLUE_MAIN

    b4_2 = [
        "Un système hybride Vision par Ordinateur (YOLOv8/OCR) + Streaming Kafka.",
        "Un moteur combinatoire d'optimisation du placement dans le parc (Recuit Simulé).",
        "Une interface de supervision avec Jumeau 3D (Three.js) et synthèses par LLM local."
    ]
    for b in b4_2:
        p = tf2.add_paragraph()
        p.text = "▪ " + b
        p.font.size = Pt(11)
        p.font.color.rgb = DARK_TEXT
        p.space_before = Pt(8)

    add_takeaway_banner(s4, "De la dispersion de l'information à l'assistance intelligente.")
    add_bottom_breadcrumb(s4, 0)


    # ==========================================
    # SLIDE 5: Structure d'accueil (Référence PDF)
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    add_top_header(s5, "2 · STRUCTURE D'ACCUEIL", "Marsa Maroc")

    add_card_box(s5, 0.8, 1.8, 5.6, 3.8)
    tb = s5.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(3.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Identité"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = BLUE_MAIN

    b5_1 = [
        "Leader national de l'exploitation des terminaux portuaires.",
        "Gestion stratégique de 9 ports clés du Royaume du Maroc.",
        "Plus de 80% du trafic maritime commercial national traité.",
        "Traitements annuels de plusieurs millions d'EVP."
    ]
    for b in b5_1:
        p = tf.add_paragraph()
        p.text = "▪ " + b
        p.font.size = Pt(11)
        p.font.color.rgb = DARK_TEXT
        p.space_before = Pt(8)

    add_card_box(s5, 6.8, 1.8, 5.733, 3.8)
    tb2 = s5.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.333), Inches(3.4))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = "Initiatives technologiques PFE"
    p2.font.size = Pt(14)
    p2.font.bold = True
    p2.font.color.rgb = BLUE_MAIN

    b5_2 = [
        "OCR Vision ISO 6346 : automatisation du pointage sous les portiques STS.",
        "Yard Optimizer : attribution d'emplacement intelligent (EDD + Recuit Simulé).",
        "Supervision 3D & LLM : modélisation du parc en temps réel et synthèses PDF."
    ]
    for b in b5_2:
        p = tf2.add_paragraph()
        p.text = "▪ " + b
        p.font.size = Pt(11)
        p.font.color.rgb = DARK_TEXT
        p.space_before = Pt(8)

    add_takeaway_banner(s5, "PFE réalisé au sein de Marsa Maroc, sous l'encadrement de M. Mohamed QODSI.")
    add_bottom_breadcrumb(s5, 1)


    # ==========================================
    # SLIDE 6: Problématique (Référence PDF)
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    add_top_header(s6, "3 · PROBLÉMATIQUE", "Une question centrale et trois axes")

    # Big Central Question Box
    c_q = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.733), Inches(1.5))
    c_q.fill.solid()
    c_q.fill.fore_color.rgb = WHITE
    c_q.line.color.rgb = BLUE_MAIN
    c_q.line.width = Pt(2)

    tb_q = s6.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(11.333), Inches(1.2))
    tf_q = tb_q.text_frame
    tf_q.word_wrap = True
    pq = tf_q.paragraphs[0]
    pq.text = "Comment concevoir et mettre en œuvre un système intelligent capable d'automatiser l'identification des conteneurs par IA et d'optimiser leur placement au parc pour minimiser le re-handling ?"
    pq.font.size = Pt(15)
    pq.font.bold = True
    pq.font.color.rgb = BLUE_MAIN
    pq.alignment = PP_ALIGN.CENTER

    # 3 Sub-questions Cards
    sub_q = [
        ("1", "Comment automatiser la saisie ?", "Pipeline YOLOv8 + OCR + Regex pour lire les codes ISO 6346 en temps réel sans erreur humaine."),
        ("2", "Comment optimiser le stockage ?", "Algorithme combinatoire (EDD + Recuit Simulé) pour assigner l'emplacement (Bay, Stack, Tier)."),
        ("3", "Comment superviser en temps réel ?", "Jumeau Numérique 3D (Three.js) et synthèses rédigées automatiquement par un LLM local.")
    ]

    for i, (num, title, desc) in enumerate(sub_q):
        x = 0.8 + i * 4.05
        add_card_box(s6, x, 3.6, 3.633, 2.5)

        badge = s6.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x + 1.516), Inches(3.8), Inches(0.6), Inches(0.6))
        badge.fill.solid()
        badge.fill.fore_color.rgb = ORANGE_ACCENT
        badge.line.fill.background()
        tf = badge.text_frame
        p = tf.paragraphs[0]
        p.text = num
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

        tb = s6.shapes.add_textbox(Inches(x + 0.15), Inches(4.5), Inches(3.333), Inches(1.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = DARK_TEXT
        p1.alignment = PP_ALIGN.CENTER

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(10)
        p2.font.color.rgb = MUTED_TEXT
        p2.alignment = PP_ALIGN.CENTER
        p2.space_before = Pt(4)

    add_bottom_breadcrumb(s6, 2)


    # ==========================================
    # SLIDE 7: Méthodologie (Référence PDF)
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    add_top_header(s7, "4 · MÉTHODOLOGIE & ARCHITECTURE", "Une architecture en deux couches")

    # Layer 1: Core System
    c_l1 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.733), Inches(1.6))
    c_l1.fill.solid()
    c_l1.fill.fore_color.rgb = BLUE_MAIN
    c_l1.line.fill.background()

    tb_l1 = s7.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(11.333), Inches(1.3))
    tf_l1 = tb_l1.text_frame
    tf_l1.word_wrap = True
    pl1_cat = tf_l1.paragraphs[0]
    pl1_cat.text = "LE CŒUR DU SYSTÈME"
    pl1_cat.font.size = Pt(9.5)
    pl1_cat.font.bold = True
    pl1_cat.font.color.rgb = ORANGE_ACCENT

    pl1_t = tf_l1.add_paragraph()
    pl1_t.text = "Couche d'Inférence IA & Optimisation Combinatoire"
    pl1_t.font.size = Pt(16)
    pl1_t.font.bold = True
    pl1_t.font.color.rgb = WHITE

    pl1_d = tf_l1.add_paragraph()
    pl1_d.text = "Modèle YOLOv8 (Détection), EasyOCR + Regex (Lecture), Ingestion Kafka et Recuit Simulé (Placement Yard)."
    pl1_d.font.size = Pt(11)
    pl1_d.font.color.rgb = WHITE
    pl1_d.space_before = Pt(4)

    # Connector text
    tb_conn = s7.shapes.add_textbox(Inches(0.8), Inches(3.45), Inches(11.733), Inches(0.4))
    tf_conn = tb_conn.text_frame
    p_conn = tf_conn.paragraphs[0]
    p_conn.text = "s'appuie sur ↓ exposée via API REST Flask & WebSockets"
    p_conn.font.size = Pt(10)
    p_conn.font.bold = True
    p_conn.font.color.rgb = ORANGE_ACCENT
    p_conn.alignment = PP_ALIGN.CENTER

    # Layer 2: Foundation
    c_l2 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(3.9), Inches(11.733), Inches(1.6))
    c_l2.fill.solid()
    c_l2.fill.fore_color.rgb = CARD_BG
    c_l2.line.color.rgb = CARD_BORDER

    tb_l2 = s7.shapes.add_textbox(Inches(1.0), Inches(4.05), Inches(11.333), Inches(1.3))
    tf_l2 = tb_l2.text_frame
    tf_l2.word_wrap = True
    pl2_cat = tf_l2.paragraphs[0]
    pl2_cat.text = "LA FONDATION"
    pl2_cat.font.size = Pt(9.5)
    pl2_cat.font.bold = True
    pl2_cat.font.color.rgb = MUTED_TEXT

    pl2_t = tf_l2.add_paragraph()
    pl2_t.text = "Couche de Données & Supervision 3D"
    pl2_t.font.size = Pt(16)
    pl2_t.font.bold = True
    pl2_t.font.color.rgb = BLUE_MAIN

    pl2_d = tf_l2.add_paragraph()
    pl2_d.text = "Base PostgreSQL (Containers, Passages, Movements), Jumeau Numérique 3D Three.js et Générateur de Rapports LLM PDF."
    pl2_d.font.size = Pt(11)
    pl2_d.font.color.rgb = DARK_TEXT
    pl2_d.space_before = Pt(4)

    add_takeaway_banner(s7, "Séparer la capture temps réel du calcul d'optimisation combinatoire.")
    add_bottom_breadcrumb(s7, 3)


    # ==========================================
    # SLIDE 8: Pipeline Vision & Ingestion (Référence PDF)
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    add_top_header(s8, "4 · MÉTHODOLOGIE & ARCHITECTURE", "Pipeline Vision & Ingestion Temps Réel")

    add_card_box(s8, 0.8, 1.8, 5.6, 4.0)
    tb = s8.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(3.6))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Composants IA Vision & Streaming"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = BLUE_MAIN

    b8 = [
        "Détection YOLOv8 : Localisation instantanée de la Bounding Box du conteneur.",
        "Prétraitement CLAHE : Égalisation d'histogramme adaptative pour éliminer les zones sombres/rouillées.",
        "EasyOCR + Regex : Extraction textuelle du matricule ISO 6346 et vérification du Check Digit.",
        "Apache Kafka : Streaming vidéo événementiel à haut débit sans perte de trames."
    ]
    for item in b8:
        p = tf.add_paragraph()
        p.text = "▪ " + item
        p.font.size = Pt(11)
        p.font.color.rgb = DARK_TEXT
        p.space_before = Pt(8)

    add_card_box(s8, 6.8, 1.8, 5.733, 4.0)
    if os.path.exists(arch_diag):
        s8.shapes.add_picture(arch_diag, Inches(7.0), Inches(2.0), width=Inches(5.333))

    add_takeaway_banner(s8, "Un pipeline d'inférence haute performance atteignant < 250 ms par conteneur.")
    add_bottom_breadcrumb(s8, 3)


    # ==========================================
    # SLIDE 9: Optimisation Yard (Référence PDF)
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    add_top_header(s9, "4 · MÉTHODOLOGIE & ARCHITECTURE", "Optimisation Yard : EDD & Recuit Simulé")

    add_card_box(s9, 0.8, 1.8, 5.6, 4.0)
    tb = s9.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(3.6))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Règle Heuristique EDD"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = BLUE_MAIN

    b9_1 = [
        "Stratification des conteneurs selon la date d'embarquement (Earliest Due Date).",
        "Les conteneurs à départ imminent sont placés en haut de pile.",
        "Élimination du besoin de déplacer des conteneurs supérieurs lors de l'extraction."
    ]
    for item in b9_1:
        p = tf.add_paragraph()
        p.text = "▪ " + item
        p.font.size = Pt(11)
        p.font.color.rgb = DARK_TEXT
        p.space_before = Pt(8)

    add_card_box(s9, 6.8, 1.8, 5.733, 4.0)
    tb2 = s9.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.333), Inches(3.6))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = "2. Recuit Simulé (Metropolis)"
    p2.font.size = Pt(14)
    p2.font.bold = True
    p2.font.color.rgb = BLUE_MAIN

    b9_2 = [
        "Critère d'acceptation probabiliste P = exp(-ΔE / T) pour échapper aux minima locaux.",
        "Recherche de la coordonnée idéale (Bay, Stack, Tier) dans des parcs encombrés (>75%).",
        "Réduction prouvée de 35% du shuffling total des portiques RTG."
    ]
    for item in b9_2:
        p = tf2.add_paragraph()
        p.text = "▪ " + item
        p.font.size = Pt(11)
        p.font.color.rgb = DARK_TEXT
        p.space_before = Pt(8)

    add_takeaway_banner(s9, "Réduire au minimum le re-handling pour économiser carburant et temps d'escale.")
    add_bottom_breadcrumb(s9, 3)


    # ==========================================
    # SLIDE 10: Stack Technique (Référence PDF)
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    add_top_header(s10, "5 · RÉALISATION & RÉSULTATS", "Stack technique retenue")

    stacks = [
        ("Données & Ingestion", "PostgreSQL (BDD relationnelle), Apache Kafka (Streaming vidéo), Docker Compose (Orchestration)."),
        ("IA & Algorithmes", "YOLOv8 (Détection), EasyOCR + CLAHE (Lecture ISO), Recuit Simulé, LLM Ollama/Groq."),
        ("Interface & 3D", "Streamlit (Dashboard Web), Three.js WebGL (Jumeau 3D), API REST Flask.")
    ]

    for i, (title, desc) in enumerate(stacks):
        x = 0.8 + i * 4.05
        add_card_box(s10, x, 1.8, 3.633, 4.0)
        tb = s10.shapes.add_textbox(Inches(x + 0.15), Inches(2.0), Inches(3.333), Inches(3.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = BLUE_MAIN

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = DARK_TEXT
        p2.space_before = Pt(10)

    add_takeaway_banner(s10, "Des briques performantes, simples à déployer en environnement industriel.")
    add_bottom_breadcrumb(s10, 4)


    # ==========================================
    # SLIDE 11: Démonstration 3D & Dashboard (Référence PDF)
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    add_top_header(s11, "5 · RÉALISATION & RÉSULTATS", "Démonstration : Jumeau 3D & Supervision")

    add_card_box(s11, 0.8, 1.8, 5.6, 4.0)
    if os.path.exists(yard_3d):
        s11.shapes.add_picture(yard_3d, Inches(0.9), Inches(2.0), width=Inches(5.4))

    add_card_box(s11, 6.8, 1.8, 5.733, 4.0)
    if os.path.exists(dash_overview):
        s11.shapes.add_picture(dash_overview, Inches(6.9), Inches(2.0), width=Inches(5.533))

    add_takeaway_banner(s11, "Temps de réponse observés en usage : < 250 ms par conteneur.")
    add_bottom_breadcrumb(s11, 4)


    # ==========================================
    # SLIDE 12: Évaluation & KPIs (Référence PDF)
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    add_top_header(s12, "5 · RÉALISATION & RÉSULTATS", "Évaluation & résultats expérimentaux")

    kpis = [
        ("98.5%", "Précision YOLOv8", "mAP@0.5 sur détection quai"),
        ("85.0%", "Succès OCR Global", "EasyOCR + Early Exit Regex"),
        ("-75%", "Réduction Re-handling", "EDD + Recuit Simulé"),
        ("22 ms", "Latence Inférence GPU", "Modèle optimisé RTX 4060")
    ]

    for i, (val, title, desc) in enumerate(kpis):
        x = 0.8 + i * 3.0
        add_card_box(s12, x, 1.8, 2.733, 4.0)
        tb = s12.shapes.add_textbox(Inches(x + 0.1), Inches(2.2), Inches(2.533), Inches(3.2))
        tf = tb.text_frame
        tf.word_wrap = True

        p_v = tf.paragraphs[0]
        p_v.text = val
        p_v.font.size = Pt(28)
        p_v.font.bold = True
        p_v.font.color.rgb = ORANGE_ACCENT if i % 2 == 1 else BLUE_MAIN
        p_v.alignment = PP_ALIGN.CENTER

        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = DARK_TEXT
        p_t.alignment = PP_ALIGN.CENTER
        p_t.space_before = Pt(10)

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = MUTED_TEXT
        p_d.alignment = PP_ALIGN.CENTER
        p_d.space_before = Pt(4)

    add_takeaway_banner(s12, "Une réduction drastique du re-handling même sous forte saturation du parc (90-95%).")
    add_bottom_breadcrumb(s12, 4)


    # ==========================================
    # SLIDE 13: Bilan & Perspectives (Référence PDF)
    # ==========================================
    s13 = prs.slides.add_slide(blank_layout)
    add_top_header(s13, "6 · CONCLUSION & PERSPECTIVES", "Un socle pour la logistique portuaire intelligente")

    add_card_box(s13, 0.8, 1.8, 5.6, 3.8)
    tb = s13.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(3.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Bilan du projet"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = BLUE_MAIN

    b13_1 = [
        "Pipeline de vision par ordinateur opérationnel au quai (YOLOv8 + EasyOCR).",
        "Moteur d'optimisation combinatoire (EDD + Recuit Simulé) opérationnel.",
        "Supervision 3D Three.js et rapports managériaux générés automatiquement par LLM."
    ]
    for b in b13_1:
        p = tf.add_paragraph()
        p.text = "▪ " + b
        p.font.size = Pt(11)
        p.font.color.rgb = DARK_TEXT
        p.space_before = Pt(8)

    add_card_box(s13, 6.8, 1.8, 5.733, 3.8)
    tb2 = s13.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.333), Inches(3.4))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = "Perspectives"
    p2.font.size = Pt(14)
    p2.font.bold = True
    p2.font.color.rgb = BLUE_MAIN

    b13_2 = [
        "Déploiement Edge Computing (GPU NVIDIA Jetson sous les portiques STS).",
        "Extension aux terminaux à conteneurs de Casablanca et Tanger Med.",
        "Intégration directe au TOS (Terminal Operating System) de Marsa Maroc."
    ]
    for b in b13_2:
        p = tf2.add_paragraph()
        p.text = "▪ " + b
        p.font.size = Pt(11)
        p.font.color.rgb = DARK_TEXT
        p.space_before = Pt(8)

    add_takeaway_banner(s13, "Un accès rapide et fiable à l'information, au service de la productivité portuaire.")
    add_bottom_breadcrumb(s13, 5)

    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")

if __name__ == "__main__":
    out_file = r"d:\Mersa_pfe\Marsa_Maroc_PFE_Presentation.pptx"
    create_presentation(out_file)
