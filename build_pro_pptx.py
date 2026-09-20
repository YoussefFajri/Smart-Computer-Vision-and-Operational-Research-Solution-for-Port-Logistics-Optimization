import sys
import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml import parse_xml

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Human Executive Designer Palette (Swiss Modern Corporate Architecture)
    NAVY_PRIMARY = RGBColor(10, 37, 64)       # #0A2540 Deep Corporate Navy
    BLUE_SECONDARY = RGBColor(0, 102, 204)    # #0066CC Executive Accent Blue
    SLATE_DARK = RGBColor(30, 41, 59)         # #1E293B Slate Dark Text
    SLATE_MUTED = RGBColor(100, 116, 139)     # #64748B Subtitle Gray
    CANVAS_BG = RGBColor(250, 250, 250)       # #FAFAFA Clean Warm Off-White
    CARD_BG = RGBColor(255, 255, 255)         # #FFFFFF Pure White Card
    BORDER_COLOR = RGBColor(203, 213, 225)    # #CBD5E1 Clean Border
    WHITE = RGBColor(255, 255, 255)
    
    RED_ACCENT = RGBColor(190, 18, 60)        # #BE123C Crimson Accent
    AMBER_ACCENT = RGBColor(180, 83, 9)       # #B45309 Amber Gold Accent
    GREEN_ACCENT = RGBColor(15, 118, 110)     # #0F766E Emerald Accent

    # Paths
    public_dir = r"d:\Mersa_pfe\slidev_presentation\public"
    logo_marsa = os.path.join(public_dir, "logo_marsa.png")
    univ_logo = os.path.join(public_dir, "universite.png")
    faculte_logo = os.path.join(public_dir, "faculte.jpg")
    arch_diag = os.path.join(public_dir, "architecture_diagram.png")
    yard_3d = os.path.join(public_dir, "yard_3d_view.png")

    sections = [
        "Contexte & Problématique",
        "État de l'Art",
        "Architecture & Conception",
        "Implémentation & Algorithmes",
        "Résultats & Évaluations",
        "Conclusion & Perspectives"
    ]

    def add_slide_transition(slide):
        tr_xml = parse_xml(r'<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" speed="med"><p:fade/></p:transition>')
        slide.element.append(tr_xml)

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = CANVAS_BG
        bg.line.fill.background()

    def add_top_header(slide, section_tag, title_text):
        set_slide_background(slide)
        add_slide_transition(slide)

        # Section Tag Badge (12pt Bold)
        tb_tag = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(10.0), Inches(0.35))
        tf_tag = tb_tag.text_frame
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = section_tag.upper()
        p_tag.font.name = 'Arial'
        p_tag.font.size = Pt(11)
        p_tag.font.bold = True
        p_tag.font.color.rgb = BLUE_SECONDARY

        # Main Title (BIG FONT 26pt)
        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(10.5), Inches(0.7))
        tf_title = tb_title.text_frame
        tf_title.word_wrap = True
        p_t = tf_title.paragraphs[0]
        p_t.text = title_text
        p_t.font.name = 'Arial'
        p_t.font.size = Pt(25)
        p_t.font.bold = True
        p_t.font.color.rgb = NAVY_PRIMARY

        # Underline Bar
        bar_b = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.45), Inches(1.5), Inches(0.06))
        bar_b.fill.solid()
        bar_b.fill.fore_color.rgb = NAVY_PRIMARY
        bar_b.line.fill.background()

        bar_s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.45), Inches(0.5), Inches(0.06))
        bar_s.fill.solid()
        bar_s.fill.fore_color.rgb = BLUE_SECONDARY
        bar_s.line.fill.background()

        if os.path.exists(logo_marsa):
            slide.shapes.add_picture(logo_marsa, Inches(11.4), Inches(0.35), height=Inches(0.85))

    def add_bottom_breadcrumb(slide, active_index=0):
        # Footer Divider Line
        div = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.8), Inches(11.733), Inches(0.02))
        div.fill.solid()
        div.fill.fore_color.rgb = BORDER_COLOR
        div.line.fill.background()

        tb_left = slide.shapes.add_textbox(Inches(0.8), Inches(6.88), Inches(4.2), Inches(0.4))
        p_l = tb_left.text_frame.paragraphs[0]
        p_l.text = "Soutenance PFE — Master D3SI"
        p_l.font.name = 'Arial'
        p_l.font.size = Pt(10)
        p_l.font.color.rgb = SLATE_MUTED

        # Navbar Badges
        total = len(sections)
        step_w = 7.3 / total
        for i, sec_name in enumerate(sections):
            x = 5.2 + i * step_w
            if i == active_index:
                badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(6.88), Inches(step_w - 0.08), Inches(0.35))
                badge.fill.solid()
                badge.fill.fore_color.rgb = RGBColor(235, 245, 255)
                badge.line.color.rgb = BLUE_SECONDARY
                p = badge.text_frame.paragraphs[0]
                p.text = sec_name
                p.font.name = 'Arial'
                p.font.size = Pt(8.5)
                p.font.bold = True
                p.font.color.rgb = BLUE_SECONDARY
                p.alignment = PP_ALIGN.CENTER
            else:
                tb = slide.shapes.add_textbox(Inches(x), Inches(6.88), Inches(step_w - 0.08), Inches(0.35))
                p = tb.text_frame.paragraphs[0]
                p.text = sec_name
                p.font.name = 'Arial'
                p.font.size = Pt(8.5)
                p.font.color.rgb = SLATE_MUTED
                p.alignment = PP_ALIGN.CENTER

    def add_card(slide, left, top, width, height, accent_color=NAVY_PRIMARY):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_COLOR
        card.line.width = Pt(1.5)

        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(0.08))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = accent_color
        top_bar.line.fill.background()
        return card

    def add_takeaway_banner(slide, text, top=6.05):
        banner = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(top), Inches(10.933), Inches(0.55))
        banner.fill.solid()
        banner.fill.fore_color.rgb = WHITE
        banner.line.color.rgb = BORDER_COLOR
        banner.line.width = Pt(1.5)

        tf = banner.text_frame
        p = tf.paragraphs[0]
        p.text = text
        p.font.name = 'Arial'
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.italic = True
        p.font.color.rgb = NAVY_PRIMARY
        p.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 1: COVER SLIDE
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)
    add_slide_transition(s1)

    if os.path.exists(univ_logo):
        s1.shapes.add_picture(univ_logo, Inches(0.8), Inches(0.4), height=Inches(0.9))
    if os.path.exists(faculte_logo):
        s1.shapes.add_picture(faculte_logo, Inches(11.4), Inches(0.4), height=Inches(0.9))

    tb_u = s1.shapes.add_textbox(Inches(2.5), Inches(0.4), Inches(8.333), Inches(0.9))
    tf_u = tb_u.text_frame
    p_u = tf_u.paragraphs[0]
    p_u.text = "Université Sultan Moulay Slimane\nFaculté Polydisciplinaire de Béni Mellal\nDépartement de Mathématiques et Informatique"
    p_u.font.name = 'Arial'
    p_u.font.size = Pt(12)
    p_u.font.bold = True
    p_u.font.color.rgb = SLATE_DARK
    p_u.alignment = PP_ALIGN.CENTER

    # Master Badge
    badge_m = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.8), Inches(1.5), Inches(9.733), Inches(0.42))
    badge_m.fill.solid()
    badge_m.fill.fore_color.rgb = RGBColor(235, 245, 255)
    badge_m.line.color.rgb = BLUE_SECONDARY
    p_bm = badge_m.text_frame.paragraphs[0]
    p_bm.text = "PROJET DE FIN D'ÉTUDES · MASTER DATA SCIENCE ET SÉCURITÉ DES SYSTÈMES D'INFORMATION"
    p_bm.font.name = 'Arial'
    p_bm.font.size = Pt(10)
    p_bm.font.bold = True
    p_bm.font.color.rgb = BLUE_SECONDARY
    p_bm.alignment = PP_ALIGN.CENTER

    # Main Title Card
    c_title = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(2.1), Inches(11.333), Inches(2.2))
    c_title.fill.solid()
    c_title.fill.fore_color.rgb = WHITE
    c_title.line.color.rgb = NAVY_PRIMARY
    c_title.line.width = Pt(2)

    tb_t = s1.shapes.add_textbox(Inches(1.2), Inches(2.25), Inches(10.933), Inches(1.9))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True

    p_t1 = tf_t.paragraphs[0]
    p_t1.text = "Solution Intelligente Logistique Portuaire"
    p_t1.font.name = 'Arial'
    p_t1.font.size = Pt(26)
    p_t1.font.bold = True
    p_t1.font.color.rgb = NAVY_PRIMARY
    p_t1.alignment = PP_ALIGN.CENTER

    p_t2 = tf_t.add_paragraph()
    p_t2.text = "Automatisation de la Gestion des Conteneurs par IA pour Marsa Maroc"
    p_t2.font.name = 'Arial'
    p_t2.font.size = Pt(16)
    p_t2.font.bold = True
    p_t2.font.color.rgb = BLUE_SECONDARY
    p_t2.alignment = PP_ALIGN.CENTER
    p_t2.space_before = Pt(12)

    # Presenter & Supervisors
    tb_pres = s1.shapes.add_textbox(Inches(1.0), Inches(4.5), Inches(11.333), Inches(0.8))
    tf_pres = tb_pres.text_frame
    p_p = tf_pres.paragraphs[0]
    p_p.text = "Présenté par :  FAJRI Youssef                      Sous la direction de :  Pr. KICH Ismail"
    p_p.font.name = 'Arial'
    p_p.font.size = Pt(14)
    p_p.font.bold = True
    p_p.font.color.rgb = SLATE_DARK
    p_p.alignment = PP_ALIGN.CENTER

    # Host Company Card
    c_comp = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.5), Inches(5.35), Inches(8.333), Inches(1.25))
    c_comp.fill.solid()
    c_comp.fill.fore_color.rgb = WHITE
    c_comp.line.color.rgb = BORDER_COLOR

    if os.path.exists(logo_marsa):
        s1.shapes.add_picture(logo_marsa, Inches(2.8), Inches(5.55), height=Inches(0.85))

    tb_comp = s1.shapes.add_textbox(Inches(4.5), Inches(5.55), Inches(6.0), Inches(0.85))
    tf_comp = tb_comp.text_frame
    pc1 = tf_comp.paragraphs[0]
    pc1.text = "Organisme d'accueil : Marsa Maroc"
    pc1.font.name = 'Arial'
    pc1.font.size = Pt(13)
    pc1.font.bold = True
    pc1.font.color.rgb = NAVY_PRIMARY

    pc2 = tf_comp.add_paragraph()
    pc2.text = "Encadrant professionnel : M. Mohamed QODSI"
    pc2.font.name = 'Arial'
    pc2.font.size = Pt(12)
    pc2.font.color.rgb = SLATE_DARK

    # Year Footer
    tb_y = s1.shapes.add_textbox(Inches(0.8), Inches(6.75), Inches(11.733), Inches(0.4))
    p_y = tb_y.text_frame.paragraphs[0]
    p_y.text = "Devant le Jury : Pr. KICH Ismail, Pr. Jury 2, Pr. Jury 3  ·  Année Universitaire 2025 – 2026"
    p_y.font.name = 'Arial'
    p_y.font.size = Pt(10.5)
    p_y.font.color.rgb = SLATE_MUTED
    p_y.alignment = PP_ALIGN.CENTER


    # ==========================================
    # SLIDE 2: SOMMAIRE
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    add_top_header(s2, "SOMMAIRE", "Plan de la Présentation")

    plan_items = [
        ("01", "Contexte & Problématique", "Enjeux logistiques, Marsa Maroc et analyse SWOT"),
        ("02", "État de l'Art & Mathématiques", "Convolution 2D, YOLOv8, OCR CRAFT/CRNN, Recuit Simulé"),
        ("03", "Architecture & Conception", "Microservices Apache Kafka, Flask REST, PostgreSQL"),
        ("04", "Implémentation & Algorithmes", "Segment-and-Stitch, Early Exit, Backpressure"),
        ("05", "Résultats & Évaluations", "Précision mAP 96.1%, OCR 85%, Re-handling ≤ 12%"),
        ("06", "Conclusion & Perspectives", "Synthèse opérationnelle et roadmap Smart Port")
    ]

    for i, (num, title, desc) in enumerate(plan_items):
        col = i % 2
        row = i // 2
        x = 0.8 + col * 6.0
        y = 1.75 + row * 1.55

        c_plan = add_card(s2, x, y, 5.7, 1.4, accent_color=NAVY_PRIMARY)

        # Number Badge (14pt Bold)
        badge = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x + 0.25), Inches(y + 0.3), Inches(0.8), Inches(0.8))
        badge.fill.solid()
        badge.fill.fore_color.rgb = NAVY_PRIMARY
        badge.line.fill.background()
        p_b = badge.text_frame.paragraphs[0]
        p_b.text = num
        p_b.font.name = 'Arial'
        p_b.font.size = Pt(16)
        p_b.font.bold = True
        p_b.font.color.rgb = WHITE
        p_b.alignment = PP_ALIGN.CENTER

        # Title & Desc (BIG FONT 14pt title, 11pt desc)
        tb = s2.shapes.add_textbox(Inches(x + 1.2), Inches(y + 0.2), Inches(4.3), Inches(1.0))
        tf = tb.text_frame
        tf.word_wrap = True
        pt = tf.paragraphs[0]
        pt.text = title
        pt.font.name = 'Arial'
        pt.font.size = Pt(14)
        pt.font.bold = True
        pt.font.color.rgb = NAVY_PRIMARY

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.name = 'Arial'
        pd.font.size = Pt(11)
        pd.font.color.rgb = SLATE_MUTED
        pd.space_before = Pt(4)

    add_bottom_breadcrumb(s2, 0)


    # ==========================================
    # SLIDE 3: CONTEXTE LOGISTIQUE
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    add_top_header(s3, "1 · CONTEXTE & PROBLÉMATIQUE", "Contexte : Marsa Maroc & Flux Logistique")

    c3_1 = add_card(s3, 0.8, 1.75, 5.7, 4.0, accent_color=NAVY_PRIMARY)
    tb = s3.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Leader National de l'Exploitation Portuaire"
    p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY

    p2 = tf.add_paragraph()
    p2.text = "• Réseau Majeur : Management des terminaux portuaires sur 9 ports stratégiques du Royaume."
    p2.font.size = Pt(13); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(14)

    p3 = tf.add_paragraph()
    p3.text = "• Enjeu Stratégique : Réduction du temps d'escale des navires et optimisation de la manutention."
    p3.font.size = Pt(13); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(12)

    c3_2 = add_card(s3, 6.833, 1.75, 5.7, 4.0, accent_color=BLUE_SECONDARY)
    tb = s3.shapes.add_textbox(Inches(7.033), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Le Transit du Conteneur"
    p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = BLUE_SECONDARY

    p2 = tf.add_paragraph()
    p2.text = "• Étape Quai (STS) : Déchargement et identification des conteneurs ISO 6346 sous le portique STS."
    p2.font.size = Pt(13); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(14)

    p3 = tf.add_paragraph()
    p3.text = "• Étape Yard (Parc) : Transfert et gerbage temporaire par portiques de parc RTG (Rubber Tyred Gantry)."
    p3.font.size = Pt(13); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(12)

    add_takeaway_banner(s3, "Un leader portuaire national au cœur des échanges internationaux.")
    add_bottom_breadcrumb(s3, 0)


    # ==========================================
    # SLIDE 4: PROBLÉMATIQUES
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    add_top_header(s4, "1 · CONTEXTE & PROBLÉMATIQUE", "Problématiques : Saisie Manuelle & Re-handling")

    c4_1 = add_card(s4, 0.8, 1.75, 5.7, 4.0, accent_color=RED_ACCENT)
    tb = s4.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Pointage Manuel au Quai (STS)"
    p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = RED_ACCENT

    p2 = tf.add_paragraph()
    p2.text = "• Saisie manuelle visuelle par des agents pointeurs sous les portiques STS."
    p2.font.size = Pt(13); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(12)

    p3 = tf.add_paragraph()
    p3.text = "• 4,8% d'erreurs logiques observées, fatigue des agents et ralentissement des flux."
    p3.font.size = Pt(13); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(12)

    sp1 = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(4.75), Inches(5.3), Inches(0.75))
    sp1.fill.solid(); sp1.fill.fore_color.rgb = RGBColor(254, 242, 242)
    sp1.line.color.rgb = RGBColor(252, 165, 165)
    p_sp = sp1.text_frame.paragraphs[0]
    p_sp.text = "4,8% d'erreurs logiques observées"
    p_sp.font.size = Pt(14); p_sp.font.bold = True; p_sp.font.color.rgb = RED_ACCENT
    p_sp.alignment = PP_ALIGN.CENTER

    c4_2 = add_card(s4, 6.833, 1.75, 5.7, 4.0, accent_color=AMBER_ACCENT)
    tb = s4.shapes.add_textbox(Inches(7.033), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Congestion & Re-handling au Parc"
    p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = AMBER_ACCENT

    p2 = tf.add_paragraph()
    p2.text = "• Placement non optimisé (ex: conteneur urgent bloqué sous d'autres boîtes)."
    p2.font.size = Pt(13); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(12)

    p3 = tf.add_paragraph()
    p3.text = "• Taux élevé de double manipulation (39,5% observé à Casablanca), surconsommation et retards."
    p3.font.size = Pt(13); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(12)

    sp2 = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.033), Inches(4.75), Inches(5.3), Inches(0.75))
    sp2.fill.solid(); sp2.fill.fore_color.rgb = RGBColor(254, 243, 199)
    sp2.line.color.rgb = RGBColor(253, 230, 138)
    p_sp2 = sp2.text_frame.paragraphs[0]
    p_sp2.text = "39,5% de taux de re-handling au Yard"
    p_sp2.font.size = Pt(14); p_sp2.font.bold = True; p_sp2.font.color.rgb = AMBER_ACCENT
    p_sp2.alignment = PP_ALIGN.CENTER

    add_takeaway_banner(s4, "Des inefficacités opérationnelles impactant le coût et le temps d'escale.")
    add_bottom_breadcrumb(s4, 0)


    # ==========================================
    # SLIDE 5: SWOT MATRIX
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    add_top_header(s5, "1 · CONTEXTE & PROBLÉMATIQUE", "Analyse Stratégique : SWOT")

    swot_data = [
        ("Forces (Strengths)", ["• Automatisation du pointage STS (gain de temps).", "• Algorithmes d'optimisation temps réel robustes.", "• Jumeau Numérique 3D pour la supervision."], GREEN_ACCENT, 0.8, 1.75),
        ("Faiblesses (Weaknesses)", ["• Dépendance à la qualité de la capture vidéo.", "• Sensibilité au calibrage des paramètres du recuit."], RED_ACCENT, 6.833, 1.75),
        ("Opportunités (Opportunities)", ["• Intégration au TOS (Terminal Operating System).", "• Modernisation technologique de Marsa Maroc.", "• Déploiement Edge (Jetson) sur portiques."], NAVY_PRIMARY, 0.8, 3.9),
        ("Menaces (Threats)", ["• Coûts de maintenance du matériel IA et IoT.", "• Vulnérabilités de cybersécurité (flux Kafka/API)."], AMBER_ACCENT, 6.833, 3.9)
    ]

    for title, items, color, x, y in swot_data:
        card = add_card(s5, x, y, 5.7, 1.95, accent_color=color)
        tb = s5.shapes.add_textbox(Inches(x + 0.2), Inches(y + 0.15), Inches(5.3), Inches(1.65))
        tf = tb.text_frame; tf.word_wrap = True
        pt = tf.paragraphs[0]
        pt.text = title
        pt.font.size = Pt(14); pt.font.bold = True; pt.font.color.rgb = color

        for item in items:
            pi = tf.add_paragraph()
            pi.text = item
            pi.font.size = Pt(11.5); pi.font.color.rgb = SLATE_DARK
            pi.space_before = Pt(4)

    add_bottom_breadcrumb(s5, 0)


    # ==========================================
    # SLIDE 6: OBJECTIFS
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    add_top_header(s6, "1 · CONTEXTE & PROBLÉMATIQUE", "Objectifs & Solution Proposée")

    c6_1 = add_card(s6, 0.8, 1.75, 5.7, 4.0, accent_color=NAVY_PRIMARY)
    tb = s6.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Vision par Ordinateur & Traitement IA"
    p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY

    p2 = tf.add_paragraph()
    p2.text = "• Détecter les conteneurs et les plaques matricules ISO via le modèle YOLOv8."
    p2.font.size = Pt(13); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(14)

    p3 = tf.add_paragraph()
    p3.text = "• Transcrire automatiquement les identifiants par un pipeline EasyOCR optimisé."
    p3.font.size = Pt(13); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(12)

    c6_2 = add_card(s6, 6.833, 1.75, 5.7, 4.0, accent_color=BLUE_SECONDARY)
    tb = s6.shapes.add_textbox(Inches(7.033), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "2. Optimisation & Aide à la Décision"
    p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = BLUE_SECONDARY

    p2 = tf.add_paragraph()
    p2.text = "• Moteur combinatoire (Recuit Simulé) pour l'allocation optimale en Yard."
    p2.font.size = Pt(13); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(14)

    p3 = tf.add_paragraph()
    p3.text = "• Dashboard avec Jumeau Numérique 3D (Three.js) et reporting automatique."
    p3.font.size = Pt(13); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(12)

    add_takeaway_banner(s6, "Une plateforme intelligente intégrée pour automatiser le pointage et optimiser le placement.")
    add_bottom_breadcrumb(s6, 0)


    # ==========================================
    # SLIDE 7: YOLOv8 & CNN
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    add_top_header(s7, "2 · ÉTAT DE L'ART & MATHÉMATIQUES", "Détection : YOLOv8 & CNN")

    c7_1 = add_card(s7, 0.8, 1.75, 5.7, 4.0, accent_color=NAVY_PRIMARY)
    tb = s7.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Extraction de Caractéristiques Spatiales (CNN)"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY

    p2 = tf.add_paragraph()
    p2.text = "Les réseaux de neurones convolutifs extraient des motifs via la convolution 2D :"
    p2.font.size = Pt(12.5); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(10)

    # Formula Box
    fbox = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(3.3), Inches(5.3), Inches(1.1))
    fbox.fill.solid(); fbox.fill.fore_color.rgb = RGBColor(241, 245, 249)
    fbox.line.color.rgb = BORDER_COLOR
    pf = fbox.text_frame.paragraphs[0]
    pf.text = "S(i, j) = (I * K)(i, j) = ∑ ∑ I(i-m, j-n) K(m, n)"
    pf.font.name = 'Arial'
    pf.font.size = Pt(13); pf.font.bold = True; pf.font.color.rgb = NAVY_PRIMARY
    pf.alignment = PP_ALIGN.CENTER

    c7_2 = add_card(s7, 6.833, 1.75, 5.7, 4.0, accent_color=BLUE_SECONDARY)
    tb = s7.shapes.add_textbox(Inches(7.033), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Détecteur YOLOv8 (Single-Stage)"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = BLUE_SECONDARY

    p2 = tf.add_paragraph()
    p2.text = "• Backbone & Neck : CSPDarknet et PANet extrayant et fusionnant les cartes de features multi-échelles."
    p2.font.size = Pt(12.5); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(12)

    p3 = tf.add_paragraph()
    p3.text = "• Head Découplée : Prédiction de classe et régression de boîte englobante Anchor-Free."
    p3.font.size = Pt(12.5); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(12)

    add_takeaway_banner(s7, "L'extraction et la localisation rapide des conteneurs en une seule passe.")
    add_bottom_breadcrumb(s7, 1)


    # ==========================================
    # SLIDE 8: MATH YOLO
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    add_top_header(s8, "2 · ÉTAT DE L'ART & MATHÉMATIQUES", "Mathématiques : Détection YOLOv8")

    c8_1 = add_card(s8, 0.8, 1.75, 5.7, 1.95, accent_color=NAVY_PRIMARY)
    tb = s8.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(5.3), Inches(1.7))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Activation SiLU"; p.font.size = Pt(14); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY
    p2 = tf.add_paragraph(); p2.text = "SiLU(x) = x · σ(x) = x / (1 + e^-x)"; p2.font.name = 'Arial'; p2.font.size = Pt(13); p2.font.bold = True; p2.space_before = Pt(4)
    p3 = tf.add_paragraph(); p3.text = "Dérivable partout, éliminant les limites du gradient mourant (ReLU)."; p3.font.size = Pt(11); p3.font.color.rgb = SLATE_MUTED; p3.space_before = Pt(4)

    c8_2 = add_card(s8, 6.833, 1.75, 5.7, 1.95, accent_color=BLUE_SECONDARY)
    tb = s8.shapes.add_textbox(Inches(7.033), Inches(1.85), Inches(5.3), Inches(1.7))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Perte CIoU (Complete IoU)"; p.font.size = Pt(14); p.font.bold = True; p.font.color.rgb = BLUE_SECONDARY
    p2 = tf.add_paragraph(); p2.text = "L_CIoU = 1 - IoU + (ρ^2 / c^2) + α·v"; p2.font.name = 'Arial'; p2.font.size = Pt(13); p2.font.bold = True; p2.space_before = Pt(4)
    p3 = tf.add_paragraph(); p3.text = "Pénalise la distance des centres, l'IoU et le ratio d'aspect des boîtes."; p3.font.size = Pt(11); p3.font.color.rgb = SLATE_MUTED; p3.space_before = Pt(4)

    c8_3 = add_card(s8, 0.8, 3.85, 11.733, 2.0, accent_color=NAVY_PRIMARY)
    tb = s8.shapes.add_textbox(Inches(1.0), Inches(4.0), Inches(11.333), Inches(1.7))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Perte DFL (Distribution Focal Loss)"; p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY
    p2 = tf.add_paragraph(); p2.text = "L_DFL(Si, Si+1) = - [ (y_{i+1} - y) log Si + (y - y_i) log S_{i+1} ]"; p2.font.name = 'Arial'; p2.font.size = Pt(13.5); p2.font.bold = True; p2.space_before = Pt(6)
    p3 = tf.add_paragraph(); p3.text = "Modélise de façon continue la distribution des frontières floues de détection."; p3.font.size = Pt(11.5); p3.font.color.rgb = SLATE_MUTED; p3.space_before = Pt(6)

    add_bottom_breadcrumb(s8, 1)


    # ==========================================
    # SLIDE 9: OCR CRAFT & CRNN
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    add_top_header(s9, "2 · ÉTAT DE L'ART & MATHÉMATIQUES", "Reconnaissance : OCR CRAFT & CRNN")

    c9_1 = add_card(s9, 0.8, 1.75, 5.7, 4.0, accent_color=NAVY_PRIMARY)
    tb = s9.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "1. Détection de Textes (CRAFT)"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY
    p2 = tf.add_paragraph(); p2.text = "• Localise les caractères individuellement (Region Score) et analyse les liaisons de mots (Affinity Score)."; p2.font.size = Pt(13); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(12)
    p3 = tf.add_paragraph(); p3.text = "• Idéal pour les conteneurs où l'espacement et l'orientation des caractères varient grandement."; p3.font.size = Pt(13); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(12)

    c9_2 = add_card(s9, 6.833, 1.75, 5.7, 4.0, accent_color=BLUE_SECONDARY)
    tb = s9.shapes.add_textbox(Inches(7.033), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "2. Transcription (CRNN)"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = BLUE_SECONDARY
    p2 = tf.add_paragraph(); p2.text = "• CNN : Extrait les caractéristiques de l'image textuelle."; p2.font.size = Pt(13); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(14)
    p3 = tf.add_paragraph(); p3.text = "• Bi-LSTM : Modélise la séquence chronologique et prédit la probabilité de chaque lettre."; p3.font.size = Pt(13); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(12)

    add_takeaway_banner(s9, "La localisation et l'analyse séquentielle du matricule de conteneur.")
    add_bottom_breadcrumb(s9, 1)


    # ==========================================
    # SLIDE 10: CTC
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    add_top_header(s10, "2 · ÉTAT DE L'ART & MATHÉMATIQUES", "Décodage CTC (Connectionist Temporal Classification)")

    c10_1 = add_card(s10, 0.8, 1.75, 5.7, 4.0, accent_color=NAVY_PRIMARY)
    tb = s10.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Alignement Séquentiel"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY
    p2 = tf.add_paragraph(); p2.text = "• Évite l'alignement manuel fastidieux image-caractère."; p2.font.size = Pt(13); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(14)
    p3 = tf.add_paragraph(); p3.text = "• Le réseau analyse de courtes tranches d'image, produisant des doublons temporels et des blancs (ε)."; p3.font.size = Pt(13); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(12)

    c10_2 = add_card(s10, 6.833, 1.75, 5.7, 4.0, accent_color=BLUE_SECONDARY)
    tb = s10.shapes.add_textbox(Inches(7.033), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Règles de Décodage"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = BLUE_SECONDARY
    p2 = tf.add_paragraph(); p2.text = "1. Fusionner les caractères consécutifs identiques."; p2.font.size = Pt(13); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(12)
    p3 = tf.add_paragraph(); p3.text = "2. Éliminer les blancs ε."; p3.font.size = Pt(13); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(10)

    demobox = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.033), Inches(4.5), Inches(5.3), Inches(0.9))
    demobox.fill.solid(); demobox.fill.fore_color.rgb = RGBColor(241, 245, 249)
    demobox.line.color.rgb = BORDER_COLOR
    p_d = demobox.text_frame.paragraphs[0]
    p_d.text = "M-S-S-C-U-U-ε   ➜   M-S-C-U   ➜   \"MSCU\""
    p_d.font.name = 'Arial'; p_d.font.size = Pt(13); p_d.font.bold = True; p_d.font.color.rgb = NAVY_PRIMARY
    p_d.alignment = PP_ALIGN.CENTER

    add_takeaway_banner(s10, "Le décodage robuste des duplications temporelles sans alignement manuel.")
    add_bottom_breadcrumb(s10, 1)


    # ==========================================
    # SLIDE 11: RECUIT SIMULÉ
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    add_top_header(s11, "2 · ÉTAT DE L'ART & MATHÉMATIQUES", "Optimisation : Stacking & Recuit Simulé")

    c11_1 = add_card(s11, 0.8, 1.75, 5.7, 4.0, accent_color=NAVY_PRIMARY)
    tb = s11.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Règles Métier de Placement (Yard)"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY
    p2 = tf.add_paragraph(); p2.text = "• EDD (Earliest Due Date) : Le conteneur du dessus doit partir avant celui du dessous : D(c_new) ≥ D(c_top)."; p2.font.size = Pt(13); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(14)
    p3 = tf.add_paragraph(); p3.text = "• Stabilité : Le conteneur du dessus doit être plus léger : W(c_new) ≤ W(c_top)."; p3.font.size = Pt(13); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(12)

    c11_2 = add_card(s11, 6.833, 1.75, 5.7, 4.0, accent_color=BLUE_SECONDARY)
    tb = s11.shapes.add_textbox(Inches(7.033), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Recuit Simulé (Metropolis)"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = BLUE_SECONDARY
    p2 = tf.add_paragraph(); p2.text = "• Résout le problème NP-difficile d'allocation en minimisant E(s)."; p2.font.size = Pt(13); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(14)
    p3 = tf.add_paragraph(); p3.text = "• Critère de Metropolis : P(acceptation) = exp(-ΔE / T). Acceptation d'une moins bonne transition."; p3.font.size = Pt(13); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(12)

    add_takeaway_banner(s11, "L'ordonnancement optimal du placement sous contraintes physiques.")
    add_bottom_breadcrumb(s11, 1)


    # ==========================================
    # SLIDE 12: SCHÉMA RECUIT
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    add_top_header(s12, "2 · ÉTAT DE L'ART & MATHÉMATIQUES", "Schéma & Calibrage du Recuit")

    c12_1 = add_card(s12, 0.8, 1.75, 5.7, 4.0, accent_color=NAVY_PRIMARY)
    tb = s12.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Refroidissement Géométrique"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY
    p2 = tf.add_paragraph(); p2.text = "Tk+1 = α · Tk   (avec α = 0.90)"; p2.font.name = 'Arial'; p2.font.size = Pt(14); p2.font.bold = True; p2.space_before = Pt(12)
    p3 = tf.add_paragraph(); p3.text = "Assure une exploration large au début et une convergence vers le minimum global à la fin."; p3.font.size = Pt(13); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(12)

    c12_2 = add_card(s12, 6.833, 1.75, 5.7, 4.0, accent_color=BLUE_SECONDARY)
    tb = s12.shapes.add_textbox(Inches(7.033), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Hyperparamètres de Réglage"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = BLUE_SECONDARY
    p2 = tf.add_paragraph(); p2.text = "• Température Initiale (T₀) : Fixée à 100."; p2.font.size = Pt(13); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(12)
    p3 = tf.add_paragraph(); p3.text = "• Nombre d'itérations (N_iter) : 1000 itérations par cycle."; p3.font.size = Pt(13); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(10)
    p4 = tf.add_paragraph(); p4.text = "• Coordonnées Spatiales : Baie × Stack × Tier."; p4.font.size = Pt(13); p4.font.color.rgb = SLATE_DARK; p4.space_before = Pt(10)

    add_bottom_breadcrumb(s12, 1)


    # ==========================================
    # SLIDE 13: ARCHITECTURE MICROSERVICES
    # ==========================================
    s13 = prs.slides.add_slide(blank_layout)
    add_top_header(s13, "3 · ARCHITECTURE & CONCEPTION", "Conception : Architecture & Base de Données")

    c13_1 = add_card(s13, 0.8, 1.75, 5.7, 4.0, accent_color=NAVY_PRIMARY)
    tb = s13.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Architecture Microservices Asynchrone"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY
    p2 = tf.add_paragraph(); p2.text = "• Ingestion temps réel : Publication asynchrone des images Edge vers Apache Kafka."; p2.font.size = Pt(13); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(12)
    p3 = tf.add_paragraph(); p3.text = "• Découplage IA / API : Un worker consomme Kafka pour exécuter YOLO/OCR sans bloquer l'API."; p3.font.size = Pt(13); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(12)

    c13_2 = add_card(s13, 6.833, 1.75, 5.7, 4.0, accent_color=BLUE_SECONDARY)
    tb = s13.shapes.add_textbox(Inches(7.033), Inches(1.95), Inches(5.3), Inches(2.2))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Structure Relationnelle & REST"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = BLUE_SECONDARY
    p2 = tf.add_paragraph(); p2.text = "• Tables (Postgres) : Containers, Manifests et YardState."; p2.font.size = Pt(12.5); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(8)
    p3 = tf.add_paragraph(); p3.text = "• API Flask : Points d'accès GET/POST pour la détection et l'optimisation."; p3.font.size = Pt(12.5); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(8)

    if os.path.exists(arch_diag):
        s13.shapes.add_picture(arch_diag, Inches(7.5), Inches(4.0), height=Inches(1.6))

    add_bottom_breadcrumb(s13, 2)


    # ==========================================
    # SLIDE 14: SEGMENT-AND-STITCH
    # ==========================================
    s14 = prs.slides.add_slide(blank_layout)
    add_top_header(s14, "4 · IMPLÉMENTATION & ALGORITHMES", "Algorithme \"Segment-and-Stitch\" (OCR Vertical)")

    c14_1 = add_card(s14, 0.8, 1.75, 5.7, 4.0, accent_color=RED_ACCENT)
    tb = s14.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Le Problème de l'OCR Vertical"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = RED_ACCENT
    p2 = tf.add_paragraph(); p2.text = "• Les matricules de conteneurs sont souvent imprimés verticaux."; p2.font.size = Pt(13); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(12)
    p3 = tf.add_paragraph(); p3.text = "• Les moteurs OCR standards échouent car ils s'attendent à une lecture horizontale."; p3.font.size = Pt(13); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(12)

    c14_2 = add_card(s14, 6.833, 1.75, 5.7, 4.0, accent_color=GREEN_ACCENT)
    tb = s14.shapes.add_textbox(Inches(7.033), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Les Étapes Clés de Résolution"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = GREEN_ACCENT
    p2 = tf.add_paragraph(); p2.text = "1. Segmentation : Détection de contours et seuillage adaptatif d'Otsu."; p2.font.size = Pt(12.5); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(10)
    p3 = tf.add_paragraph(); p3.text = "2. Tri Y : Alignement des caractères de haut en bas."; p3.font.size = Pt(12.5); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(8)
    p4 = tf.add_paragraph(); p4.text = "3. Stitching : Découpage et réassemblage horizontal dans le bon ordre."; p4.font.size = Pt(12.5); p4.font.color.rgb = SLATE_DARK; p4.space_before = Pt(8)

    add_takeaway_banner(s14, "La reconstruction horizontale des matricules verticaux pour l'OCR.")
    add_bottom_breadcrumb(s14, 3)


    # ==========================================
    # SLIDE 15: EARLY EXIT
    # ==========================================
    s15 = prs.slides.add_slide(blank_layout)
    add_top_header(s15, "4 · IMPLÉMENTATION & ALGORITHMES", "OCR Optimisé : Early Exit & Kafka Worker")

    c15_1 = add_card(s15, 0.8, 1.75, 5.7, 4.0, accent_color=NAVY_PRIMARY)
    tb = s15.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Early Exit & Multi-pipelines"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY
    p2 = tf.add_paragraph(); p2.text = "• Application successive de 6 filtres d'images."; p2.font.size = Pt(13); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(12)
    p3 = tf.add_paragraph(); p3.text = "• Dès qu'un code valide regex (ex: MSCU 1234567) est lu avec confiance > 25%, le pipeline s'arrête."; p2.font.size = Pt(13); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(10)
    p4 = tf.add_paragraph(); p4.text = "• Gain : Latence moyenne réduite de 8.0s à 1.3s par conteneur."; p4.font.size = Pt(13); p4.font.bold = True; p4.font.color.rgb = GREEN_ACCENT; p4.space_before = Pt(10)

    c15_2 = add_card(s15, 6.833, 1.75, 5.7, 4.0, accent_color=BLUE_SECONDARY)
    tb = s15.shapes.add_textbox(Inches(7.033), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Multi-Threading & Backpressure"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = BLUE_SECONDARY
    p2 = tf.add_paragraph(); p2.text = "• Un thread lit Kafka en continu, un second exécute l'IA."; p2.font.size = Pt(13); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(14)
    p3 = tf.add_paragraph(); p3.text = "• Contre-pression : Si la file interne sature, les trames vidéo obsolètes sont automatiquement rejetées."; p3.font.size = Pt(13); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(12)

    add_takeaway_banner(s15, "Une réduction drastique de latence de 8s à 1.3s par conteneur.")
    add_bottom_breadcrumb(s15, 3)


    # ==========================================
    # SLIDE 16: JUMEAU 3D
    # ==========================================
    s16 = prs.slides.add_slide(blank_layout)
    add_top_header(s16, "4 · IMPLÉMENTATION & ALGORITHMES", "Jumeau Numérique 3D & Supervision")

    c16_1 = add_card(s16, 0.8, 1.75, 5.7, 4.0, accent_color=NAVY_PRIMARY)
    tb = s16.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "WebGL Interactive (Three.js)"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY
    p2 = tf.add_paragraph(); p2.text = "• Canvas WebGL intégré dans Streamlit via une iframe sécurisée."; p2.font.size = Pt(13); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(12)
    p3 = tf.add_paragraph(); p3.text = "• Instanciation dynamique de boîtes 3D (BoxGeometry) modélisant l'état du parc."; p3.font.size = Pt(13); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(12)
    p4 = tf.add_paragraph(); p4.text = "• Guidage visuel interactif en temps réel pour le placement de Yard."; p4.font.size = Pt(13); p4.font.color.rgb = SLATE_DARK; p4.space_before = Pt(12)

    c16_2 = add_card(s16, 6.833, 1.75, 5.7, 4.0, accent_color=BLUE_SECONDARY)
    tb = s16.shapes.add_textbox(Inches(7.033), Inches(1.95), Inches(5.3), Inches(0.8))
    tf = tb.text_frame; p = tf.paragraphs[0]; p.text = "Supervision du Parc en Temps Réel"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = BLUE_SECONDARY

    if os.path.exists(yard_3d):
        s16.shapes.add_picture(yard_3d, Inches(7.15), Inches(2.6), height=Inches(2.9))

    add_bottom_breadcrumb(s16, 3)


    # ==========================================
    # SLIDE 17: RÉSULTATS EXPERIMENTAUX (BIG FONT KPI)
    # ==========================================
    s17 = prs.slides.add_slide(blank_layout)
    add_top_header(s17, "5 · RÉSULTATS & ÉVALUATIONS", "Résultats Expérimentaux")

    kpis = [
        ("96,1%", "Précision mAP@0.5", "(Détection YOLOv8)", NAVY_PRIMARY, 0.8),
        ("85%", "Taux de réussite OCR", "(Horizontal + Vertical)", BLUE_SECONDARY, 4.8),
        ("≤ 12%", "Taux de Re-handling", "(À 95% de remplissage)", GREEN_ACCENT, 8.8)
    ]

    for val, label, sub, color, x in kpis:
        c_k = add_card(s17, x, 1.9, 3.733, 3.8, accent_color=color)
        tb = s17.shapes.add_textbox(Inches(x + 0.2), Inches(2.3), Inches(3.333), Inches(2.8))
        tf = tb.text_frame; tf.word_wrap = True
        pv = tf.paragraphs[0]; pv.text = val; pv.font.name = 'Arial'; pv.font.size = Pt(48); pv.font.bold = True; pv.font.color.rgb = color; pv.alignment = PP_ALIGN.CENTER
        pl = tf.add_paragraph(); pl.text = label; pl.font.size = Pt(15); pl.font.bold = True; pl.font.color.rgb = NAVY_PRIMARY; pl.alignment = PP_ALIGN.CENTER; pl.space_before = Pt(14)
        ps = tf.add_paragraph(); ps.text = sub; ps.font.size = Pt(12); ps.font.color.rgb = SLATE_MUTED; ps.alignment = PP_ALIGN.CENTER; ps.space_before = Pt(6)

    add_takeaway_banner(s17, "Réduction de plus de 75% des doubles manipulations comparé au système manuel existant.")
    add_bottom_breadcrumb(s17, 4)


    # ==========================================
    # SLIDE 18: DOCKER
    # ==========================================
    s18 = prs.slides.add_slide(blank_layout)
    add_top_header(s18, "5 · RÉSULTATS & ÉVALUATIONS", "Déploiement Conteneurisé (Docker)")

    c18_1 = add_card(s18, 0.8, 1.75, 5.7, 4.0, accent_color=NAVY_PRIMARY)
    tb = s18.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Architecture des Conteneurs"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY
    p2 = tf.add_paragraph(); p2.text = "• Services Isolés : 5 conteneurs Docker orchestrés via Docker Compose."; p2.font.size = Pt(13); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(10)
    p3 = tf.add_paragraph(); p3.text = "• Postgres : Persistance des données relationnelles."; p3.font.size = Pt(13); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(8)
    p4 = tf.add_paragraph(); p4.text = "• Kafka & Zookeeper : Streaming vidéo et messages temps réel."; p4.font.size = Pt(13); p4.font.color.rgb = SLATE_DARK; p4.space_before = Pt(8)
    p5 = tf.add_paragraph(); p5.text = "• Flask API & Worker IA : Inférence et logique métier."; p5.font.size = Pt(13); p5.font.color.rgb = SLATE_DARK; p5.space_before = Pt(8)

    c18_2 = add_card(s18, 6.833, 1.75, 5.7, 4.0, accent_color=GREEN_ACCENT)
    tb = s18.shapes.add_textbox(Inches(7.033), Inches(1.95), Inches(5.3), Inches(3.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Avantages Industriels"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = GREEN_ACCENT
    p2 = tf.add_paragraph(); p2.text = "• Isolation Complète : Évite les conflits de dépendances CUDA/Python."; p2.font.size = Pt(13); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(12)
    p3 = tf.add_paragraph(); p3.text = "• Scalabilité et Portabilité : Déploiement facile et réplication des workers IA selon la charge du port."; p3.font.size = Pt(13); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(12)

    add_takeaway_banner(s18, "Une portabilité et scalabilité totales via Docker Compose.")
    add_bottom_breadcrumb(s18, 4)


    # ==========================================
    # SLIDE 19: CONCLUSION
    # ==========================================
    s19 = prs.slides.add_slide(blank_layout)
    add_top_header(s19, "6 · CONCLUSION & PERSPECTIVES", "Conclusion & Perspectives")

    c19_1 = add_card(s19, 0.8, 1.75, 5.7, 4.2, accent_color=GREEN_ACCENT)
    tb = s19.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.3), Inches(3.8))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Bilan des Réalisations"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = GREEN_ACCENT
    p2 = tf.add_paragraph(); p2.text = "• Pipeline de vision par ordinateur YOLOv8 + EasyOCR opérationnel."; p2.font.size = Pt(12.5); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(10)
    p3 = tf.add_paragraph(); p3.text = "• Moteur combinatoire (Recuit Simulé) validé et fonctionnel."; p3.font.size = Pt(12.5); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(8)
    p4 = tf.add_paragraph(); p4.text = "• Architecture Kafka + Flask résiliente et temps réel."; p4.font.size = Pt(12.5); p4.font.color.rgb = SLATE_DARK; p4.space_before = Pt(8)
    p5 = tf.add_paragraph(); p5.text = "• Supervision Jumeau Numérique 3D Streamlit & Three.js."; p5.font.size = Pt(12.5); p5.font.color.rgb = SLATE_DARK; p5.space_before = Pt(8)

    c19_2 = add_card(s19, 6.833, 1.75, 5.7, 4.2, accent_color=NAVY_PRIMARY)
    tb = s19.shapes.add_textbox(Inches(7.033), Inches(1.95), Inches(5.3), Inches(3.8))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Perspectives & Remerciements"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY
    p2 = tf.add_paragraph(); p2.text = "• Edge Computing : Déploiement sur cartes NVIDIA Jetson sur portiques."; p2.font.size = Pt(12.5); p2.font.color.rgb = SLATE_DARK; p2.space_before = Pt(10)
    p3 = tf.add_paragraph(); p3.text = "• Modèle OCR Personnalisé : Entraînement CRNN dédié aux conteneurs."; p3.font.size = Pt(12.5); p3.font.color.rgb = SLATE_DARK; p3.space_before = Pt(8)
    p4 = tf.add_paragraph(); p4.text = "• Intégration TOS : Synchronisation directe avec le TOS de Marsa Maroc."; p4.font.size = Pt(12.5); p4.font.color.rgb = SLATE_DARK; p4.space_before = Pt(8)
    p5 = tf.add_paragraph(); p5.text = "• Remerciements à mon encadrant académique Pr. Ismail Kich et professionnel M. Mohamed Qodsi."; p5.font.size = Pt(12.5); p5.font.bold = True; p5.font.color.rgb = NAVY_PRIMARY; p5.space_before = Pt(8)

    add_bottom_breadcrumb(s19, 5)


    # ==========================================
    # SLIDE 20: MERCI (Q&A)
    # ==========================================
    s20 = prs.slides.add_slide(blank_layout)
    set_slide_background(s20)
    add_slide_transition(s20)

    c20 = s20.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.4), Inches(10.933), Inches(4.7))
    c20.fill.solid(); c20.fill.fore_color.rgb = WHITE
    c20.line.color.rgb = NAVY_PRIMARY
    c20.line.width = Pt(2)

    tb = s20.shapes.add_textbox(Inches(1.5), Inches(1.8), Inches(10.333), Inches(3.8))
    tf = tb.text_frame; tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "SOUTENANCE DE PROJET DE FIN D'ÉTUDES"
    p.font.name = 'Arial'; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = BLUE_SECONDARY; p.alignment = PP_ALIGN.CENTER

    p2 = tf.add_paragraph()
    p2.text = "Merci de votre attention"
    p2.font.name = 'Arial'; p2.font.size = Pt(32); p2.font.bold = True; p2.font.color.rgb = NAVY_PRIMARY; p2.alignment = PP_ALIGN.CENTER; p2.space_before = Pt(16)

    p3 = tf.add_paragraph()
    p3.text = "Avez-vous des questions ?"
    p3.font.name = 'Arial'; p3.font.size = Pt(18); p3.font.bold = True; p3.font.color.rgb = BLUE_SECONDARY; p3.alignment = PP_ALIGN.CENTER; p3.space_before = Pt(12)

    p4 = tf.add_paragraph()
    p4.text = "FAJRI Youssef — Master D3SI — USMS / FPBM — Marsa Maroc (2025-2026)"
    p4.font.name = 'Arial'; p4.font.size = Pt(12); p4.font.color.rgb = SLATE_MUTED; p4.alignment = PP_ALIGN.CENTER; p4.space_before = Pt(28)

    add_bottom_breadcrumb(s20, 5)

    output_path = r"d:\Mersa_pfe\Marsa_Maroc_PFE_Presentation.pptx"
    prs.save(output_path)
    print(f"Human-designed 20-min Presentation successfully created at: {output_path}")

if __name__ == "__main__":
    create_presentation()
