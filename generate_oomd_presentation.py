import sys
import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette Definitions
    NAVY = RGBColor(15, 23, 42)       # #0F172A
    DARK_BLUE = RGBColor(30, 41, 59)  # #1E293B
    EMERALD = RGBColor(16, 185, 129)  # #10B981
    TEAL = RGBColor(13, 148, 136)     # #0D9488
    INDIGO = RGBColor(59, 130, 246)   # #3B82F6
    AMBER = RGBColor(245, 158, 11)    # #F59E0B
    WHITE = RGBColor(255, 255, 255)
    BG_LIGHT = RGBColor(248, 250, 252)# #F8FAFC
    CARD_BG = RGBColor(255, 255, 255)
    CARD_BORDER = RGBColor(226, 232, 240) # #E2E8F0
    TEXT_MUTED = RGBColor(100, 116, 139) # #64748B
    TEXT_DARK = RGBColor(30, 41, 59)

    def set_slide_background(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.color.rgb = color
        return bg

    def add_header(slide, badge_text, title_text, subtitle_text):
        # Badge
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.5), Inches(2.2), Inches(0.35))
        badge.fill.solid()
        badge.fill.fore_color.rgb = TEAL
        badge.line.color.rgb = TEAL
        tf_b = badge.text_frame
        tf_b.word_wrap = True
        p_b = tf_b.paragraphs[0]
        p_b.text = badge_text.upper()
        p_b.font.size = Pt(10)
        p_b.font.bold = True
        p_b.font.color.rgb = WHITE
        p_b.alignment = PP_ALIGN.CENTER

        # Title
        tx_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.7), Inches(0.6))
        tf_t = tx_title.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = NAVY

        # Subtitle
        if subtitle_text:
            tx_sub = slide.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(0.35))
            tf_s = tx_sub.text_frame
            tf_s.word_wrap = True
            p_s = tf_s.paragraphs[0]
            p_s.text = subtitle_text
            p_s.font.size = Pt(12)
            p_s.font.color.rgb = TEXT_MUTED

    def add_card(slide, x, y, w, h, bg_color=CARD_BG, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1)
        return card

    def add_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text

    # ==========================================
    # SLIDE 1: TITLE SLIDE
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, NAVY)

    # Accent decorative banner
    banner = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.35), Inches(7.5))
    banner.fill.solid()
    banner.fill.fore_color.rgb = EMERALD
    banner.line.color.rgb = EMERALD

    # Top Pill
    pill = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.0), Inches(4.5), Inches(0.4))
    pill.fill.solid()
    pill.fill.fore_color.rgb = TEAL
    pill.line.color.rgb = TEAL
    p = pill.text_frame.paragraphs[0]
    p.text = "OOMD ASSIGNMENT NO. 8 • SYSTEM DESIGN DOCUMENT"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER

    # Main Title
    tx = s1.shapes.add_textbox(Inches(1.2), Inches(1.6), Inches(11.0), Inches(2.2))
    tf = tx.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "NutriPlate: Integrated System Design Document"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = WHITE

    p2 = tf.add_paragraph()
    p2.text = "Combining Object, Database, Service, and Architecture Layers for Automated Indian Dietary Assessment"
    p2.font.size = Pt(18)
    p2.font.color.rgb = RGBColor(148, 163, 184)

    # Metadata Card
    meta_card = add_card(s1, 1.2, 4.4, 10.9, 2.3, bg_color=DARK_BLUE, border_color=TEAL)
    tx_meta = s1.shapes.add_textbox(Inches(1.5), Inches(4.55), Inches(10.3), Inches(2.0))
    tf_m = tx_meta.text_frame
    tf_m.word_wrap = True

    p_m1 = tf_m.paragraphs[0]
    p_m1.text = "PROJECT METADATA & PRESENTATION DETAILS"
    p_m1.font.size = Pt(12)
    p_m1.font.bold = True
    p_m1.font.color.rgb = EMERALD

    p_m2 = tf_m.add_paragraph()
    p_m2.text = "• Student Name: Adhyayan Goyal  |  PRN: 123B1B072  |  Class: B.Tech (Div: B)"
    p_m2.font.size = Pt(13)
    p_m2.font.color.rgb = WHITE

    p_m3 = tf_m.add_paragraph()
    p_m3.text = "• Core Project: NutriPlate — Edge-Cloud Decoupled Deep Instance Segmentation & Biochemical Synergy"
    p_m3.font.size = Pt(13)
    p_m3.font.color.rgb = RGBColor(226, 232, 240)

    p_m4 = tf_m.add_paragraph()
    p_m4.text = "• Department: Department of Computer Engineering, Pimpri Chinchwad College of Engineering (PCCOE), Pune"
    p_m4.font.size = Pt(13)
    p_m4.font.color.rgb = RGBColor(148, 163, 184)

    p_m5 = tf_m.add_paragraph()
    p_m5.text = "• Project Guide: Dr. K. Rajeswari, Professor, Dept. of Computer Engineering"
    p_m5.font.size = Pt(13)
    p_m5.font.color.rgb = RGBColor(148, 163, 184)

    add_notes(s1, "Good morning faculty and examiners. Today I am presenting Assignment 8 of Object Oriented Modeling and Design for our project NutriPlate. This presentation outlines the complete System Design Document across four unified software engineering layers: the Object Layer with UML designs, the Database Layer with normalized schemas and vector storage, the Service Layer with microservices and REST APIs, and the Architecture Layer detailing our edge-cloud decoupled deployment.")

    # ==========================================
    # SLIDE 2: PROBLEM STATEMENT & MOTIVATION
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, BG_LIGHT)
    add_header(s2, "Domain Analysis", "Problem Statement: Why Standard Vision Fails on Indian Meals", "Traditional Western dietary AI systems fail catastrophically when applied to South Asian culinary scenarios")

    cols = [
        ("1. Fluid Gravies & Amorphous Boundaries", "Dals, sambars, and kormas lack rigid boundaries. They bleed into rice mounds and coat rotis, creating ill-defined non-rigid segmentations that defeat bounding-box detectors.", AMBER),
        ("2. Visual Color-Texture Ambiguity", "Visually identical dishes (e.g., Dal Tadka vs. Kadhi Pakora) exhibit near-identical color spectra while differing drastically in glycemic index, carbohydrate load, and protein density.", INDIGO),
        ("3. Disregard of Biochemical Bioavailability", "Calorie trackers assume a naive 1:1 intake-to-absorption ratio. Indian plant-based meals are rich in chelators (phytates, tannins) that suppress Fe/Zn absorption by up to 70% unless promoters (Vitamin C) are present.", TEAL),
        ("4. Mobile Latency & Thermal Constraints", "Two-stage models (Mask R-CNN) exceed 120 GFLOPs and incur >180 ms latency, causing extreme thermal throttling and battery drain on mobile phones.", NAVY)
    ]

    for idx, (head, body, color) in enumerate(cols):
        col_x = 0.8 + idx * 2.95
        card = add_card(s2, col_x, 1.9, 2.8, 5.0)
        # Top color accent bar
        accent = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(col_x), Inches(1.9), Inches(2.8), Inches(0.12))
        accent.fill.solid()
        accent.fill.fore_color.rgb = color
        accent.line.color.rgb = color

        tx = s2.shapes.add_textbox(Inches(col_x + 0.15), Inches(2.15), Inches(2.5), Inches(4.5))
        tf = tx.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = head
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = NAVY

        p_b = tf.add_paragraph()
        p_b.text = "\n" + body
        p_b.font.size = Pt(12)
        p_b.font.color.rgb = TEXT_DARK

    add_notes(s2, "In our problem analysis, we identified four major bottlenecks that standard computer vision algorithms face with Indian food. First, curries and gravies are amorphous fluids that infiltrate flatbreads and rice, making rigid bounding boxes useless. Second, yellow dal and kadhi look the same visually but have completely different nutritional profiles. Third, current calorie trackers ignore biological bioavailability—phytates in lentils bind iron unless Vitamin C is present. And fourth, heavy cloud segmentation causes latency and mobile overheating.")

    # ==========================================
    # SLIDE 3: REQUIREMENTS SPECIFICATION
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, BG_LIGHT)
    add_header(s3, "Requirements Engineering", "System Requirements: Functional & Non-Functional Specifications", "Explicitly decoupled between real-time mobile edge processing and cloud analytical intelligence")

    # Left Card: Functional Requirements
    add_card(s3, 0.8, 1.9, 5.75, 5.0)
    tx_fr = s3.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(5.35), Inches(4.7))
    tf_fr = tx_fr.text_frame
    tf_fr.word_wrap = True
    p = tf_fr.paragraphs[0]
    p.text = "FUNCTIONAL REQUIREMENTS (CORE FEATURES)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEAL

    fr_items = [
        ("FR-01: Thali Rim Calibration", "Calibrate pixel-to-metric dimensions via plate ellipse/convex hull relative to standard 28 cm thali reference."),
        ("FR-02: Real-Time Edge Segmentation", "Segment food instances on-device using PANet + ProtoNet in <25 ms."),
        ("FR-03: Monocular Portion Mass", "Estimate portion weight (g) from pixel area, bulk density, depth, and shape factors."),
        ("FR-04: 412 Indian Food Classes", "Classify across 412 distinct culinary items covering gravies, breads, rice, and sabzis."),
        ("FR-05: IFCT 2017 Composition", "Retrieve macro/micronutrient compositions based on ICMR-NIN IFCT tables."),
        ("FR-06: Biochemical Bioavailability", "Model promoter-chelator saturation kinetics to compute bioavailable Fe and Zn yields."),
        ("FR-07: Clamped Health Score", "Calculate meal quality score S_plate in [10, 100] based on ICMR-NIN DGI 2024 guidelines."),
        ("FR-08: Active Learning Verification", "Prompt user when entropy H > 0.65; index 576-D MobileNetV3 visual vectors.")
    ]
    for code, desc in fr_items:
        p_item = tf_fr.add_paragraph()
        p_item.text = f"• {code}: {desc}"
        p_item.font.size = Pt(10.5)
        p_item.font.color.rgb = TEXT_DARK

    # Right Card: Non-Functional Requirements
    add_card(s3, 6.75, 1.9, 5.75, 5.0)
    tx_nfr = s3.shapes.add_textbox(Inches(6.95), Inches(2.05), Inches(5.35), Inches(4.7))
    tf_nfr = tx_nfr.text_frame
    tf_nfr.word_wrap = True
    p2 = tf_nfr.paragraphs[0]
    p2.text = "NON-FUNCTIONAL REQUIREMENTS (SYSTEM ATTRIBUTES)"
    p2.font.size = Pt(13)
    p2.font.bold = True
    p2.font.color.rgb = INDIGO

    nfr_items = [
        ("NFR-01: Ultra-Low Edge Latency", "Inference and mask synthesis must execute in <30 ms (benchmark: 24.8 ms on Snapdragon 8 Gen 2)."),
        ("NFR-02: Strict Thermal & Battery Budget", "Edge power consumption must remain <=450 mW (benchmark: 420 mW) without thermal throttling."),
        ("NFR-03: High Accuracy Threshold", "Achieve >=88% Box mAP@50 across 412 Indian classes and volumetric portion MAPE <10% (achieved 8.8%)."),
        ("NFR-04: High Availability", "Cloud microservices (IFCT lookup, scoring, vector gallery) maintain 99.9% operational uptime."),
        ("NFR-05: Horizontal Elastic Scalability", "Containerized Kubernetes pods scale dynamically based on request concurrency."),
        ("NFR-06: Privacy-Preserving Edge Compute", "Raw camera image buffers are processed purely in-memory on the phone and never stream to the cloud."),
        ("NFR-07: Offline Fault Resilience", "Edge client caches food segmentations locally when offline, syncing analytical telemetry upon reconnection.")
    ]
    for code, desc in nfr_items:
        p_item = tf_nfr.add_paragraph()
        p_item.text = f"• {code}: {desc}"
        p_item.font.size = Pt(10.5)
        p_item.font.color.rgb = TEXT_DARK

    add_notes(s3, "On this slide, we formalize the system requirements. Key functional requirements include on-device plate rim calibration, anchor-free ProtoNet segmentation within 25 ms, portion mass estimation using category morphometric factors, IFCT 2017 nutritional lookup, biochemical bioavailability modeling, and DGI 2024 health scoring. For non-functional requirements, we maintain sub-30ms latency on Snapdragon hardware, a 420 mW power budget, and strict privacy by running computer vision in-memory on the edge.")

    # ==========================================
    # SLIDE 4: ARCHITECTURE OVERVIEW (4-TIER)
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, BG_LIGHT)
    add_header(s4, "Software Architecture", "Selected Architecture: 4-Tier Decoupled Edge-Cloud Topology", "Separating high-frequency visual perception on mobile hardware from analytical metabolic intelligence in the cloud")

    tiers = [
        ("Tier 1: Presentation & Client UI", "Runs on Android/iOS mobile client", [
            "Camera Viewfinder with plate boundary overlay",
            "Real-time food segmentation mask visualization",
            "Calorie, macronutrient, and bioavailable mineral cards",
            "Interactive Active Learning verification prompt modal"
        ], TEAL),
        ("Tier 2: Edge Vision Inference Engine", "Executes locally on Snapdragon 8 Gen 2 NPU/GPU", [
            "Anchor-Free YOLOv8-Nano Backbone with PANet",
            "ProtoNet Head: 32 prototype masks in 24.8 ms",
            "Monocular Calibrator: Ellipse fitting (28 cm thali reference)",
            "MobileNetV3 576-D feature embedding extractor"
        ], INDIGO),
        ("Tier 3: Cloud Analytics Microservices", "Containerized Docker / Kubernetes pods", [
            "API Gateway with JWT authentication & rate limiting",
            "IFCT 2017 Knowledge Service (412 recipe decompositions)",
            "Biochemical Synergy Engine (promoter/chelator kinetics)",
            "ICMR-NIN DGI 2024 Clamped Health Scoring Engine"
        ], AMBER),
        ("Tier 4: Data, Caching & Vector Layer", "Persistent enterprise database infrastructure", [
            "PostgreSQL: Relational storage for users, sessions, food logs",
            "Redis: In-memory cache for ultra-fast IFCT food profile lookups",
            "pgvector / FAISS: 576-D embedding index for active learning",
            "Automated time-series table partitioning for dietary logs"
        ], NAVY)
    ]

    for idx, (title, sub, items, col) in enumerate(tiers):
        card_y = 1.9 + idx * 1.3
        add_card(s4, 0.8, card_y, 11.7, 1.18)
        # Left indicator bar
        bar = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(card_y), Inches(0.15), Inches(1.18))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.color.rgb = col

        tx_t = s4.shapes.add_textbox(Inches(1.1), Inches(card_y + 0.05), Inches(4.0), Inches(1.0))
        tf_t = tx_t.text_frame
        p_t = tf_t.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = NAVY
        p_s = tf_t.add_paragraph()
        p_s.text = sub
        p_s.font.size = Pt(10)
        p_s.font.color.rgb = TEXT_MUTED

        tx_b = s4.shapes.add_textbox(Inches(5.2), Inches(card_y + 0.05), Inches(7.2), Inches(1.0))
        tf_b = tx_b.text_frame
        for it in items:
            p_it = tf_b.add_paragraph() if tf_b.paragraphs[0].text else tf_b.paragraphs[0]
            p_it.text = f"• {it}"
            p_it.font.size = Pt(10)
            p_it.font.color.rgb = TEXT_DARK

    add_notes(s4, "Our software architecture is organized into four distinct tiers. Tier 1 is the mobile UI. Tier 2 is our edge inference engine, running directly on the smartphone NPU in 24.8 ms. Tier 3 is the cloud microservices layer that handles the heavy domain logic—IFCT lookups, Michaelis-Menten bioavailability calculations, and DGI 2024 health scoring. Tier 4 is our data layer combining PostgreSQL for structured relational records, Redis for caching, and pgvector for active learning embeddings.")

    # ==========================================
    # SLIDE 5: USE CASE MODELING
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, BG_LIGHT)
    add_header(s5, "Object-Oriented Analysis", "Use Case Modeling: Actor Interactions & System Boundaries", "Streamlined around the consumer mobile experience and autonomous machine perception agents")

    # Left: Actors
    add_card(s5, 0.8, 1.9, 3.6, 5.0)
    tx_act = s5.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(3.2), Inches(4.7))
    tf_act = tx_act.text_frame
    tf_act.word_wrap = True
    p = tf_act.paragraphs[0]
    p.text = "SYSTEM ACTORS"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = TEAL

    actors = [
        ("👤 App User (Primary Human)", "Interacts with mobile app to capture meals, view nutritional breakdown, track health goals, and verify uncertain dishes."),
        ("🤖 Edge Vision Agent (System)", "Autonomous on-device agent executing ProtoNet inference, mask generation, plate ellipse fitting, and portion mass estimation."),
        ("☁️ Cloud Analytics Service (System)", "Backend microservice coordinating IFCT composition queries, biochemical cross-talk matrix calculations, and DGI scoring.")
    ]
    for act, desc in actors:
        p_a = tf_act.add_paragraph()
        p_a.text = f"\n{act}"
        p_a.font.size = Pt(11)
        p_a.font.bold = True
        p_a.font.color.rgb = NAVY
        p_d = tf_act.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = TEXT_DARK

    # Right: Use Cases Table
    add_card(s5, 4.6, 1.9, 7.9, 5.0)
    tx_uc = s5.shapes.add_textbox(Inches(4.8), Inches(2.05), Inches(7.5), Inches(4.7))
    tf_uc = tx_uc.text_frame
    tf_uc.word_wrap = True
    p = tf_uc.paragraphs[0]
    p.text = "CORE USE CASE SPECIFICATIONS"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = INDIGO

    use_cases = [
        ("UC-01: Capture Meal Image", "App User", "User aligns smartphone camera over dining thali and triggers image capture."),
        ("UC-02: Segment Food Instances", "Edge Vision Agent", "<<include>> Runs ProtoNet to generate pixel masks for distinct items within 24.8 ms."),
        ("UC-03: Calibrate Plate & Estimate Portions", "Edge Vision Agent", "<<include>> Fits 28 cm thali ellipse, maps pixel occupancy to gram mass (m_i)."),
        ("UC-04: Evaluate Bioavailable Nutrition", "Cloud Analytics", "<<include>> Fetches IFCT 2017 profiles and computes promoter-chelator yields."),
        ("UC-05: Generate Smart Health Score", "Cloud Analytics", "<<include>> Evaluates ICMR-NIN DGI 2024 score S_plate clamped in [10, 100]."),
        ("UC-06: Verify Uncertain Classification", "App User", "<<extend>> Triggered when entropy H_K > 0.65; user confirms correct dish."),
        ("UC-07: Update Visual Embedding Gallery", "Cloud Analytics", "<<extend>> Stores 576-D MobileNetV3 vector for zero-retraining personalized matching.")
    ]
    for uc, act, desc in use_cases:
        p_u = tf_uc.add_paragraph()
        p_u.text = f"• {uc} [{act}]: {desc}"
        p_u.font.size = Pt(10.5)
        p_u.font.color.rgb = TEXT_DARK

    add_notes(s5, "In our use case model, we focus strictly on the core NutriPlate workflow. We have two primary actors: the human App User and the autonomous machine agents—the Edge Vision Agent and Cloud Analytics Service. Core use cases include image capture, real-time segmentation, plate calibration, portion estimation, bioavailability evaluation, and DGI health scoring. When the model encounters visual ambiguity, an extend relationship triggers user label verification to update our 576-dimensional embedding gallery.")

    # ==========================================
    # SLIDE 6: CLASS DIAGRAM 1 - EDGE VISION
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, BG_LIGHT)
    add_header(s6, "Object Layer", "Class Diagram 1: Edge Computer Vision & Volume Calibration", "Decomposing on-device image capture, anchor-free coordinate regression, and prototypical mask synthesis")

    edge_classes = [
        ("RGBImage", "Attributes:\n• imageId: String\n• timestamp: DateTime\n• rawWidth, rawHeight: Int\n• buffer: Byte[]\nMethods:\n+ normalize(): Float[][][]"),
        ("PlateCalibrator", "Attributes:\n• defaultPlateDiameterCm: 28.0\nMethods:\n+ fitEllipse(frame): Ellipse\n+ computeRefArea(ellipse): Double\n+ computePixelToCmRatio(): Double"),
        ("ProtoNetHead", "Attributes:\n• prototypeCount: Int = 32\n• inputResolution: 640x640\nMethods:\n+ generatePrototypes(P3): Matrix[32]\n+ forward(): FeatureMaps"),
        ("DetectionHead", "Attributes:\n• numClasses: Int = 412\nMethods:\n+ regressOffsets(P3-P5): BoxOffset[]\n+ computeCoefficients(P3-P5): CoeffVec[]"),
        ("MaskSynthesizer", "Attributes:\n• sigmoidThreshold: 0.5\nMethods:\n+ linearCombine(protos, coeffs)\n+ applySigmoid(): Float[][]\n+ cropToBox(box): SegmentedMask"),
        ("VolumetricEstimator", "Attributes:\n• standardRimDepthCm: 2.5\nMethods:\n+ lookupDensity(foodId): Double\n+ getShapeFactor(classId): Double\n+ estimateMass(mask, refArea): Grams")
    ]

    for idx, (cname, cbody) in enumerate(edge_classes):
        row = idx // 3
        col = idx % 3
        cx = 0.8 + col * 3.95
        cy = 1.9 + row * 2.55
        add_card(s6, cx, cy, 3.8, 2.4)

        # Header bar
        hbar = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(cx), Inches(cy), Inches(3.8), Inches(0.4))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = TEAL
        hbar.line.color.rgb = TEAL
        p = hbar.text_frame.paragraphs[0]
        p.text = f"<<Class>> {cname}"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

        tx = s6.shapes.add_textbox(Inches(cx + 0.1), Inches(cy + 0.42), Inches(3.6), Inches(1.9))
        tf = tx.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = cbody
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_DARK

    add_notes(s6, "Here is our first UML Class Diagram representing the edge vision pipeline. RGBImage ingests the camera tensor. PlateCalibrator fits an ellipse over the 28 cm thali to determine reference surface area. ProtoNetHead generates 32 prototypical feature bases, while DetectionHead predicts boundary offsets and 32 linear coefficients. MaskSynthesizer linearly combines them to yield instance masks. Finally, VolumetricEstimator converts mask area into mass in grams using category bulk density and shape factors.")

    # ==========================================
    # SLIDE 7: CLASS DIAGRAM 2 - CLOUD NUTRITION
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, BG_LIGHT)
    add_header(s7, "Object Layer", "Class Diagram 2: Cloud Biochemical Synergy, Scoring & Active Learning", "Modeling nutritional knowledge lookup, non-linear biochemical cross-talk, and clamped DGI meal scoring")

    cloud_classes = [
        ("FoodCompositionRepo", "Attributes:\n• totalClasses: 412\n• ifctVersion: 'IFCT 2017'\nMethods:\n+ getNutrientVector(classId): NutrientVec\n+ getBulkDensity(classId): Double\n+ getRecipeIngredients(classId): List"),
        ("BiochemicalEngine", "Attributes:\n• interactionMatrix: Matrix[M x M]\n• saturationConstants: Dict[K_jk]\nMethods:\n+ computePromoters(iron, vitC): Double\n+ computeChelation(iron, phytate): Double\n+ getBioavailableYield(rawVec): BioYield"),
        ("DGIScoringEngine", "Attributes:\n• baseScore: Double = 100.0\n• calorieLimits: Dict[MealType, Int]\nMethods:\n+ computeCaloriePenalty(E, target)\n+ computePEBonus(peRatio)\n+ computeNocturnalPenalty(carbPct, meal)\n+ calculatePlateScore(): S_plate"),
        ("NutrientVector", "Attributes:\n• energyKcal, proteinG, carbG, fatG\n• fiberG: Double\n• nonHemeIronMg, zincMg: Double\n• phyticAcidMg, ascorbicAcidMg: Double\nMethods:\n+ scaleByPortionMass(grams): NutrientVec"),
        ("ActiveLearningManager", "Attributes:\n• entropyThreshold: Double = 0.65\n• cosineThreshold: Double = 0.76\nMethods:\n+ evaluateEntropy(probs): Double\n+ queryGallery(vec576): MatchResult\n+ insertVerifiedEmbedding(vec576, classId)"),
        ("MealScoreResult", "Attributes:\n• grossCalories: Double\n• bioavailableIronMg, bioavailableZincMg\n• peRatio: Double\n• finalPlateScore: Int [10, 100]\n• auditPenalties: Dict[String, Double]")
    ]

    for idx, (cname, cbody) in enumerate(cloud_classes):
        row = idx // 3
        col = idx % 3
        cx = 0.8 + col * 3.95
        cy = 1.9 + row * 2.55
        add_card(s7, cx, cy, 3.8, 2.4)

        hbar = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(cx), Inches(cy), Inches(3.8), Inches(0.4))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = INDIGO
        hbar.line.color.rgb = INDIGO
        p = hbar.text_frame.paragraphs[0]
        p.text = f"<<Class>> {cname}"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

        tx = s7.shapes.add_textbox(Inches(cx + 0.1), Inches(cy + 0.42), Inches(3.6), Inches(1.9))
        tf = tx.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = cbody
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_DARK

    add_notes(s7, "Our second Class Diagram covers the cloud metabolic intelligence. FoodCompositionRepository manages the 412 IFCT food items. BiochemicalEngine executes our Biochemical Interaction Matrix using Michaelis-Menten kinetics to calculate true bioavailable iron and zinc. DGIScoringEngine enforces ICMR-NIN 2024 dietary guidelines, clamping the score between 10 and 100. ActiveLearningManager handles top-5 entropy calculations and queries our 576-dimensional embedding gallery.")

    # ==========================================
    # SLIDE 8: DATABASE LAYER - RELATIONAL SCHEMA
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, BG_LIGHT)
    add_header(s8, "Database Layer", "Relational Schema: Normalized Data Dictionary (Tables 1 to 5)", "Cleaned enterprise relational schema capturing user profiles, IFCT food catalog, sessions, and segmented food items")

    tables_info = [
        ("Table 1: USERS", "Stores user identities and account authentication credentials", [
            ("user_id", "INT (PK)", "Unique user identifier"),
            ("email", "VARCHAR(120) (Unique)", "Registered login email"),
            ("password_hash", "VARCHAR(255)", "BCrypt salted credential hash"),
            ("full_name", "VARCHAR(100)", "User full name"),
            ("created_at", "TIMESTAMP", "Account creation timestamp")
        ]),
        ("Table 2: USER_PROFILES", "Captures personalized dietary targets and health preferences", [
            ("profile_id", "INT (PK)", "Unique profile identifier"),
            ("user_id", "INT (FK -> USERS)", "Associated user reference"),
            ("age, gender", "INT, VARCHAR(10)", "Demographic basal metabolic indicators"),
            ("target_calorie_budget", "INT", "Prescribed daily caloric ceiling (kcal)"),
            ("health_goal", "VARCHAR(50)", "Wellness target (e.g., Glycemic Control)")
        ]),
        ("Table 3: IFCT_FOOD_MASTER", "Nutritional catalog for 412 Indian food items from ICMR-NIN IFCT 2017", [
            ("food_id", "INT (PK)", "Unique culinary item ID"),
            ("class_name", "VARCHAR(100) (Unique)", "Culinary and scientific dish name"),
            ("regional_category", "VARCHAR(50)", "Regional origin (North, South, East, West)"),
            ("bulk_density_g_cm3", "FLOAT", "Food density (rho_i) for mass calculation"),
            ("shape_coefficient", "FLOAT", "Morphology shape factor (xi_i in [0.4, 1.2])"),
            ("macros & minerals", "FLOAT columns", "Energy, Protein, Carbs, Fat, Fiber, Fe, Zn, Phytates, Vit C")
        ]),
        ("Table 4: MEAL_SESSIONS", "Maintains meal capture events and environmental telemetry", [
            ("session_id", "VARCHAR(64) (PK)", "UUID string for meal capture event"),
            ("user_id", "INT (FK -> USERS)", "Owner user ID"),
            ("meal_type", "VARCHAR(20)", "BREAKFAST, LUNCH, DINNER, SNACK"),
            ("captured_at", "TIMESTAMP", "Exact meal photograph timestamp"),
            ("plate_diameter_ratio", "FLOAT", "Pixel-to-metric ratio from ellipse fitting"),
            ("edge_latency_ms", "FLOAT", "On-device ProtoNet execution runtime")
        ]),
        ("Table 5: FOOD_INSTANCES", "Stores individually segmented food items detected on each plate", [
            ("instance_id", "BIGINT (PK)", "Unique segmented entity identifier"),
            ("session_id", "VARCHAR(64) (FK)", "Associated meal session"),
            ("food_id", "INT (FK -> IFCT)", "Identified food item from IFCT catalog"),
            ("mask_pixel_area", "INT", "Segmented pixel count (A_mask)"),
            ("estimated_mass_g", "FLOAT", "Portion weight calculated via Eq. (13)"),
            ("prediction_entropy", "FLOAT", "Classification uncertainty value H_K(x)"),
            ("user_verified", "BOOLEAN", "True if confirmed or corrected by user")
        ])
    ]

    for idx, (tname, tdesc, trows) in enumerate(tables_info):
        row = idx // 3 if idx < 3 else 1
        col = idx % 3 if idx < 3 else (idx - 3) * 1.5
        w = 3.8 if idx < 3 else 5.75
        cx = 0.8 + (idx % 3) * 3.95 if idx < 3 else (0.8 if idx == 3 else 6.75)
        cy = 1.9 if idx < 3 else 4.45
        ch = 2.45 if idx < 3 else 2.45
        add_card(s8, cx, cy, w, ch)

        hbar = s8.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(cx), Inches(cy), Inches(w), Inches(0.35))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = TEAL if idx < 3 else DARK_BLUE
        hbar.line.color.rgb = TEAL if idx < 3 else DARK_BLUE
        p = hbar.text_frame.paragraphs[0]
        p.text = tname
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE

        tx = s8.shapes.add_textbox(Inches(cx + 0.1), Inches(cy + 0.38), Inches(w - 0.2), Inches(2.0))
        tf = tx.text_frame
        tf.word_wrap = True
        p_sub = tf.paragraphs[0]
        p_sub.text = tdesc
        p_sub.font.size = Pt(9.5)
        p_sub.font.bold = True
        p_sub.font.color.rgb = TEXT_MUTED

        for col_name, col_type, col_desc in trows:
            p_r = tf.add_paragraph()
            p_r.text = f"• {col_name} ({col_type}): {col_desc}"
            p_r.font.size = Pt(8.5)
            p_r.font.color.rgb = TEXT_DARK

    add_notes(s8, "In the database design layer, we defined a normalized relational schema. Table 1 stores core user authentication. Table 2 stores dietary profiles and daily calorie targets. Table 3 is our IFCT Food Master catalog, containing bulk density and shape coefficients alongside macro and micronutrient profiles. Table 4 records meal sessions and edge latency, and Table 5 stores individually segmented food instances, including pixel mask areas and estimated mass.")

    # ==========================================
    # SLIDE 9: DATABASE LAYER - BIOCHEMISTRY & VECTORS
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, BG_LIGHT)
    add_header(s9, "Database Layer", "Relational Schema: Biochemical Kinetics & Vector Database (Tables 6 to 8)", "Modeling kinetic interaction matrices, final meal scores, and high-dimensional 576-D vector embeddings")

    tables_info_2 = [
        ("Table 6: BIOCHEMICAL_INTERACTION_MATRIX", "Maintains kinetic cross-talk coefficients between nutrient pairs", [
            ("interaction_id", "INT (PK)", "Unique interaction pair identifier"),
            ("target_nutrient", "VARCHAR(50)", "Target cation (e.g., Non-Heme Iron, Zinc)"),
            ("interacting_agent", "VARCHAR(50)", "Active agent (e.g., Ascorbic Acid, Phytic Acid)"),
            ("interaction_type", "VARCHAR(20)", "PROMOTER (+), CHELATOR (-), ORTHOGONAL (0)"),
            ("kinetic_weight", "FLOAT (alpha_jk)", "Interaction multiplier (e.g., +2.1 for Vit C -> Fe)"),
            ("half_saturation_k", "FLOAT (K_jk)", "Michaelis-Menten half-saturation constant in mg")
        ], TEAL),
        ("Table 7: MEAL_NUTRITIONAL_ANALYSES", "Stores biological nutrient absorption yields and ICMR-NIN DGI 2024 scores", [
            ("analysis_id", "BIGINT (PK)", "Unique analysis record identifier"),
            ("session_id", "VARCHAR(64) (FK)", "Associated meal session"),
            ("total_calories_kcal", "FLOAT", "Aggregated gross caloric content"),
            ("effective_iron_mg", "FLOAT", "Bioavailable non-heme iron yield (N_iron^eff)"),
            ("effective_zinc_mg", "FLOAT", "Bioavailable zinc yield (N_zinc^eff)"),
            ("pe_ratio", "FLOAT", "Protein-to-Energy percentage (PE_meal)"),
            ("plate_health_score", "INT", "Clamped meal score S_plate in [10, 100]"),
            ("nocturnal_penalty", "FLOAT", "Late dinner carbohydrate deduction (delta_noct)")
        ], INDIGO),
        ("Table 8: ACTIVE_LEARNING_GALLERY", "Stores high-dimensional visual embeddings for zero-training personalization", [
            ("embedding_id", "BIGINT (PK)", "Unique embedding entry identifier"),
            ("user_id", "INT (FK -> USERS)", "User who verified the culinary dish"),
            ("food_id", "INT (FK -> IFCT)", "True verified culinary class from catalog"),
            ("embedding_vector", "VECTOR(576)", "576-D L2-normalized MobileNetV3 visual vector"),
            ("similarity_hits", "INT", "Number of successful cosine matches (>=0.76)"),
            ("created_at", "TIMESTAMP", "Embedding indexing timestamp in pgvector")
        ], AMBER)
    ]

    for idx, (tname, tdesc, trows, col) in enumerate(tables_info_2):
        cx = 0.8 + idx * 3.95
        cy = 1.9
        add_card(s9, cx, cy, 3.8, 5.0)

        hbar = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(cx), Inches(cy), Inches(3.8), Inches(0.4))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = col
        hbar.line.color.rgb = col
        p = hbar.text_frame.paragraphs[0]
        p.text = tname
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = WHITE

        tx = s9.shapes.add_textbox(Inches(cx + 0.15), Inches(cy + 0.45), Inches(3.5), Inches(4.4))
        tf = tx.text_frame
        tf.word_wrap = True
        p_sub = tf.paragraphs[0]
        p_sub.text = tdesc
        p_sub.font.size = Pt(11)
        p_sub.font.bold = True
        p_sub.font.color.rgb = NAVY

        for col_name, col_type, col_desc in trows:
            p_r = tf.add_paragraph()
            p_r.text = f"• {col_name} ({col_type}):\n  {col_desc}"
            p_r.font.size = Pt(9.5)
            p_r.font.color.rgb = TEXT_DARK

    add_notes(s9, "Continuing our database layer, Table 6 represents our Biochemical Interaction Matrix, storing interaction pairs such as Ascorbic Acid promoting Iron with alpha=+2.1, and Phytate chelating Iron with alpha=-0.65. Table 7 stores calculated biological yields, protein ratios, and the final clamped DGI health score. Table 8 is our pgvector vector database table storing 576-dimensional MobileNetV3 embeddings for zero-retraining active learning.")

    # ==========================================
    # SLIDE 10: ENTITY-RELATIONSHIP (ER) DIAGRAM
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10, BG_LIGHT)
    add_header(s10, "Database Layer", "Entity-Relationship (ER) Diagram: Conceptual Data Architecture", "1:N cardinalities and foreign key dependencies connecting users, meal sessions, food instances, and nutritional models")

    # Visual representation of ER relationships
    er_boxes = [
        ("USERS", "PK: user_id\nemail, password_hash", 0.8, 2.0, 2.6, 1.2, NAVY),
        ("USER_PROFILES", "PK: profile_id\nFK: user_id\ncalorie_budget, pe_target", 0.8, 3.6, 2.6, 1.2, TEAL),
        ("MEAL_SESSIONS", "PK: session_id\nFK: user_id\nmeal_type, captured_at", 4.2, 2.0, 2.8, 1.4, INDIGO),
        ("FOOD_INSTANCES", "PK: instance_id\nFK: session_id, food_id\nmask_area, mass_g", 4.2, 4.0, 2.8, 1.5, AMBER),
        ("IFCT_FOOD_MASTER", "PK: food_id\nclass_name, density, xi\nenergy, macros, Fe, Zn", 8.0, 4.0, 2.8, 1.5, TEAL),
        ("MEAL_NUTRITIONAL_ANALYSES", "PK: analysis_id\nFK: session_id\ntotal_kcal, plate_score", 4.2, 5.8, 2.8, 1.3, DARK_BLUE),
        ("BIOCHEM_MATRIX", "PK: interaction_id\ntarget, agent, alpha, K", 8.0, 2.0, 2.8, 1.3, NAVY),
        ("ACTIVE_LEARNING_GALLERY", "PK: embedding_id\nFK: user_id, food_id\nvector(576)", 0.8, 5.2, 2.6, 1.4, AMBER)
    ]

    for title, desc, bx, by, bw, bh, col in er_boxes:
        add_card(s10, bx, by, bw, bh)
        hbar = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(bx), Inches(by), Inches(bw), Inches(0.3))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = col
        hbar.line.color.rgb = col
        p = hbar.text_frame.paragraphs[0]
        p.text = title
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

        tx = s10.shapes.add_textbox(Inches(bx + 0.1), Inches(by + 0.32), Inches(bw - 0.2), Inches(bh - 0.35))
        tf = tx.text_frame
        p = tf.paragraphs[0]
        p.text = desc
        p.font.size = Pt(8.5)
        p.font.color.rgb = TEXT_DARK

    # Summary box
    summary_card = add_card(s10, 8.0, 5.8, 4.5, 1.3, bg_color=DARK_BLUE, border_color=TEAL)
    tx_sum = s10.shapes.add_textbox(Inches(8.1), Inches(5.85), Inches(4.3), Inches(1.2))
    tf_s = tx_sum.text_frame
    p_s1 = tf_s.paragraphs[0]
    p_s1.text = "KEY CARDINALITY RELATIONSHIPS"
    p_s1.font.size = Pt(11)
    p_s1.font.bold = True
    p_s1.font.color.rgb = EMERALD

    p_s2 = tf_s.add_paragraph()
    p_s2.text = "• USERS (1) ── (1) USER_PROFILES"
    p_s2.font.size = Pt(9.5)
    p_s2.font.color.rgb = WHITE

    p_s3 = tf_s.add_paragraph()
    p_s3.text = "• USERS (1) ── (N) MEAL_SESSIONS ── (1) MEAL_ANALYSIS"
    p_s3.font.size = Pt(9.5)
    p_s3.font.color.rgb = WHITE

    p_s4 = tf_s.add_paragraph()
    p_s4.text = "• MEAL_SESSIONS (1) ── (N) FOOD_INSTANCES (N) ── (1) IFCT_MASTER"
    p_s4.font.size = Pt(9.5)
    p_s4.font.color.rgb = WHITE

    add_notes(s10, "This slide visualizes our Entity-Relationship diagram. A User has one Profile and multiple Meal Sessions. Each Meal Session contains one overall Nutritional Analysis and multiple Food Instances detected on the thali plate. Food Instances reference the IFCT Food Master catalog, which is also cross-referenced by the Biochemical Interaction Matrix and the Active Learning Gallery. All relationships are strictly normalized in 3NF.")

    # ==========================================
    # SLIDE 11: SERVICE LAYER & MICROSERVICES
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11, BG_LIGHT)
    add_header(s11, "Service Layer", "Microservices Inventory: Decoupled Service Contracts", "Containerized microservice ecosystem governing edge inference, nutritional translation, and active learning")

    services = [
        ("1. API Gateway & Auth Service", "Authenticates mobile requests via JWT, enforces rate limiting, and proxies requests to backend microservices.", "Bearer JWT Token", "Decoded user claims & routed proxy"),
        ("2. Edge Vision Runtime", "Executes PANet + ProtoNet instance segmentation locally on Snapdragon 8 hardware in 24.8 ms.", "640x640x3 RGB frame", "32 proto-masks, box offsets, coeff vectors"),
        ("3. Monocular Geometry Calibrator", "Fits ellipse on dining plate rim and translates pixel mask area into gram mass (m_i) via Eq. (13).", "Binary mask + 28 cm rim hull", "Calibrated portion mass in grams"),
        ("4. IFCT Knowledge Service", "Manages nutritional composition mappings for 412 Indian food items based on ICMR-NIN IFCT 2017.", "Food Class IDs + mass (g)", "Raw nutrient vector n in R^M"),
        ("5. Biochemical Synergy Engine", "Applies Michaelis-Menten saturation kinetics over Interaction Matrix A to calculate bioavailable yields.", "Nutrient vector n + Matrix A", "Bioavailable yields (N_Fe^eff, N_Zn^eff)"),
        ("6. ICMR-NIN DGI Scoring Engine", "Computes composite meal health score S_plate clamped in [10, 100] factoring in calories, PE ratio, and fiber.", "Nutrient yields + Meal type", "Clamped score S_plate in [10, 100]"),
        ("7. Active Learning Vector Service", "Gates predictions by entropy H_K > 0.65, performs HNSW cosine search, and indexes user-corrected dishes.", "576-D vector + dish label", "Similarity match / gallery confirmation")
    ]

    for idx, (sname, sresp, sinp, sout) in enumerate(services):
        sy = 1.9 + idx * 0.74
        add_card(s11, 0.8, sy, 11.7, 0.68)
        # Left tag
        tag = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(sy), Inches(0.12), Inches(0.68))
        tag.fill.solid()
        tag.fill.fore_color.rgb = TEAL if idx % 2 == 0 else INDIGO
        tag.line.color.rgb = TEAL if idx % 2 == 0 else INDIGO

        tx = s11.shapes.add_textbox(Inches(1.0), Inches(sy + 0.02), Inches(3.6), Inches(0.64))
        tf = tx.text_frame
        p = tf.paragraphs[0]
        p.text = sname
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p_sub = tf.add_paragraph()
        p_sub.text = sresp
        p_sub.font.size = Pt(8.5)
        p_sub.font.color.rgb = TEXT_DARK

        tx_io = s11.shapes.add_textbox(Inches(4.8), Inches(sy + 0.02), Inches(7.5), Inches(0.64))
        tf_io = tx_io.text_frame
        p_in = tf_io.paragraphs[0]
        p_in.text = f"Input: {sinp}"
        p_in.font.size = Pt(9)
        p_in.font.color.rgb = TEXT_MUTED
        p_out = tf_io.add_paragraph()
        p_out.text = f"Output: {sout}"
        p_out.font.size = Pt(9)
        p_out.font.bold = True
        p_out.font.color.rgb = TEAL if idx % 2 == 0 else INDIGO

    add_notes(s11, "Our service layer is designed around 7 specialized microservices. The API Gateway handles authentication and traffic routing. The Edge Vision Runtime and Monocular Geometry Calibrator execute locally on the phone. The cloud hosts the IFCT Knowledge Service, the Biochemical Synergy Engine, the DGI Scoring Engine, and the Active Learning Vector Service. This microservices split ensures that heavy knowledge queries never block client-side rendering.")

    # ==========================================
    # SLIDE 12: SEQUENCE DIAGRAM (MESSAGE FLOW)
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12, BG_LIGHT)
    add_header(s12, "Interaction Modeling", "Sequence Diagram: End-to-End Image Capture to Metabolic Scoring", "Trace of inter-object messages during image acquisition, edge segmentation, cloud biochemical scoring, and active learning")

    steps = [
        ("Step 1: Capture Trigger", "App User -> Edge Camera", "User snaps meal frame; camera passes raw RGB bitmap buffer to edge vision memory."),
        ("Step 2: On-Device ProtoNet Segmentation", "Edge Vision -> Mobile NPU", "PANet backbone + ProtoNet generates 32 prototype masks and coefficients in 24.8 ms."),
        ("Step 3: Plate Hull & Portion Approximation", "Edge Calibrator -> Local Storage", "Fits 28 cm thali ellipse, applies Eq. (13) to calculate dish portion mass (m_i in grams)."),
        ("Step 4: Payload Telemetry Dispatch", "Mobile App -> Cloud API Gateway", "POST /api/v1/meals/evaluate with food class IDs, portion masses, and 576-D vector."),
        ("Step 5: IFCT Nutrient Retrieval", "API Gateway -> IFCT Microservice", "Queries relational food master to retrieve unadjusted macro and micronutrient vectors n."),
        ("Step 6: Biochemical Bioavailability Calculation", "IFCT Service -> Biochemical Engine", "Executes Eq. (15) with Michaelis-Menten kinetics to calculate bioavailable Fe and Zn yields."),
        ("Step 7: Clamped DGI Health Scoring", "Biochem Engine -> DGI Scoring Engine", "Evaluates Eq. (16)-(21) for calorie deviation, PE ratio, and nocturnal carbs -> S_plate in [10, 100]."),
        ("Step 8: Uncertainty Check & Active Learning", "DGI Engine -> Mobile Client UI", "If entropy H_K > 0.65, prompts user for confirmation; verified 576-D vector indexed in pgvector."),
        ("Step 9: Real-Time Results Render", "Mobile App -> App User", "Displays color-coded segmented thali, portion masses, bioavailable minerals, and health score.")
    ]

    for idx, (stitle, spaths, sdesc) in enumerate(steps):
        sy = 1.9 + idx * 0.57
        add_card(s12, 0.8, sy, 11.7, 0.52)
        # Step number pill
        pill = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(sy + 0.08), Inches(1.8), Inches(0.35))
        pill.fill.solid()
        pill.fill.fore_color.rgb = TEAL if idx < 4 else (INDIGO if idx < 7 else AMBER)
        pill.line.color.rgb = pill.fill.fore_color.rgb
        p = pill.text_frame.paragraphs[0]
        p.text = stitle.split(":")[0]
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

        tx = s12.shapes.add_textbox(Inches(2.8), Inches(sy + 0.05), Inches(3.2), Inches(0.42))
        tf = tx.text_frame
        p = tf.paragraphs[0]
        p.text = spaths
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = NAVY

        tx_d = s12.shapes.add_textbox(Inches(6.1), Inches(sy + 0.05), Inches(6.3), Inches(0.42))
        tf_d = tx_d.text_frame
        p_d = tf_d.paragraphs[0]
        p_d.text = sdesc
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_DARK

    add_notes(s12, "This sequence diagram details our execution pipeline from start to finish. When the user snaps a photo, edge segmentation and portion estimation finish on the phone within 25 ms. The phone dispatches a tiny JSON payload with class IDs and gram masses to the Cloud API Gateway. The cloud queries IFCT 2017, calculates Michaelis-Menten bioavailability, and computes the clamped health score. If uncertainty is detected, the user confirms the dish label and our vector gallery updates instantly.")

    # ==========================================
    # SLIDE 13: COMPONENT DIAGRAM
    # ==========================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13, BG_LIGHT)
    add_header(s13, "Architecture Layer", "Component Diagram: Modular Subsystems & Interface Dependencies", "Structural breakdown of edge mobile modules, cloud microservices, and storage adapters")

    c_left = [
        ("📱 Edge Vision Core Component", [
            "Provided Interface: ICameraCapture, ISegmenter, IPortionCalibrator",
            "Required Interface: IHardwareNPU, ILocalStoreAdapter",
            "Sub-modules: PANet Feature Extractor, ProtoNet Mask Head, Convex Hull Plate Fitter, MobileNetV3 576-D Vectorizer"
        ]),
        ("🌐 Edge Telemetry Dispatcher Component", [
            "Provided Interface: ITelemetryBuffer, IOfflineSync",
            "Required Interface: ICloudRESTGateway (HTTPS/JSON)",
            "Sub-modules: In-Memory Frame Buffer, JSON Serialization, Offline SQLite Queue"
        ])
    ]

    c_right = [
        ("☁️ Cloud Analytical Processor Component", [
            "Provided Interface: IMealEvaluator, IBiochemService, ISmartScoreService",
            "Required Interface: IIFCTRepository, IVectorSearchEngine",
            "Sub-modules: Michaelis-Menten Kinetic Solver, ICMR-NIN DGI Clamped Scoring Engine, Predictive Entropy Calculator"
        ]),
        ("🗄️ Storage & Knowledge Adapter Component", [
            "Provided Interface: IRelationalStore, ICacheStore, IVectorIndex",
            "Required Interface: PostgreSQL Driver, Redis Driver, pgvector Extension",
            "Sub-modules: IFCT 2017 Master Table, Redis Cache Manager, HNSW Vector Index"
        ])
    ]

    for idx, (title, items) in enumerate(c_left):
        cy = 1.9 + idx * 2.55
        add_card(s13, 0.8, cy, 5.75, 2.4)
        hbar = s13.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(cy), Inches(5.75), Inches(0.35))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = TEAL
        hbar.line.color.rgb = TEAL
        p = hbar.text_frame.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE

        tx = s13.shapes.add_textbox(Inches(0.95), Inches(cy + 0.4), Inches(5.45), Inches(1.9))
        tf = tx.text_frame
        for it in items:
            p_it = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
            p_it.text = f"• {it}"
            p_it.font.size = Pt(10)
            p_it.font.color.rgb = TEXT_DARK

    for idx, (title, items) in enumerate(c_right):
        cy = 1.9 + idx * 2.55
        add_card(s13, 6.75, cy, 5.75, 2.4)
        hbar = s13.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.75), Inches(cy), Inches(5.75), Inches(0.35))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = INDIGO
        hbar.line.color.rgb = INDIGO
        p = hbar.text_frame.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE

        tx = s13.shapes.add_textbox(Inches(6.9), Inches(cy + 0.4), Inches(5.45), Inches(1.9))
        tf = tx.text_frame
        for it in items:
            p_it = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
            p_it.text = f"• {it}"
            p_it.font.size = Pt(10)
            p_it.font.color.rgb = TEXT_DARK

    add_notes(s13, "Our Component Diagram illustrates the internal modules and interface dependencies. On the edge side, Edge Vision Core exposes segmentation and portion calibration interfaces, utilizing the hardware NPU. On the cloud side, the Analytical Processor component requires the IFCT Repository and Vector Search Engine, which are fulfilled by our Storage & Knowledge Adapter connecting to PostgreSQL, Redis, and pgvector.")

    # ==========================================
    # SLIDE 14: DEPLOYMENT DIAGRAM
    # ==========================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14, BG_LIGHT)
    add_header(s14, "Architecture Layer", "Deployment Diagram: Physical Hardware Nodes & Execution Environments", "Mapping software components to Qualcomm Snapdragon mobile hardware and cloud Kubernetes clusters")

    dep_nodes = [
        ("Node 1: Mobile Device (Edge Client)", "Hardware: Qualcomm Snapdragon 8 Gen 2 Mobile Platform\nOS: Android 14 / iOS 17\nExecution Environment:\n• TFLite Runtime with Adreno GPU / Hexagon NPU Delegate\n• NutriPlate Mobile App Shell (Flutter / Kotlin)\n• In-Memory Camera Tensor Buffer (Volatile RAM)\n• Offline Cache: SQLite encrypted meal buffer", 0.8, 1.9, 5.75, 5.0, TEAL),
        ("Node 2: Cloud Infrastructure (Kubernetes)", "Cloud Platform: AWS / GCP Kubernetes Cluster\nNetwork Gateway: NGINX Ingress Controller (TLS 1.3 / HTTPS)\nExecution Pods (Docker Containers):\n• Pod 1: API Gateway & JWT Auth Service (Node.js/Go)\n• Pod 2: IFCT 2017 Service & Redis Cache Adapter\n• Pod 3: Biochemical Synergy & DGI Scoring Engine (Python)\n• Pod 4: Active Learning & pgvector Service (Python/FastAPI)\nDatabase Node:\n• PostgreSQL 16 + pgvector extension\n• Redis In-Memory Cluster for IFCT Caching", 6.75, 1.9, 5.75, 5.0, NAVY)
    ]

    for title, desc, nx, ny, nw, nh, col in dep_nodes:
        add_card(s14, nx, ny, nw, nh)
        hbar = s14.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(nx), Inches(ny), Inches(nw), Inches(0.4))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = col
        hbar.line.color.rgb = col
        p = hbar.text_frame.paragraphs[0]
        p.text = title
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = WHITE

        tx = s14.shapes.add_textbox(Inches(nx + 0.15), Inches(ny + 0.45), Inches(nw - 0.3), Inches(nh - 0.55))
        tf = tx.text_frame
        tf.word_wrap = True
        lines = desc.split("\n")
        for idx_l, l in enumerate(lines):
            p_l = tf.add_paragraph() if idx_l > 0 else tf.paragraphs[0]
            p_l.text = l
            p_l.font.size = Pt(10.5)
            if "Hardware:" in l or "Cloud Platform:" in l or "Execution" in l or "Database" in l:
                p_l.font.bold = True
                p_l.font.color.rgb = NAVY
            else:
                p_l.font.color.rgb = TEXT_DARK

    add_notes(s14, "Here is our Deployment Diagram showing physical execution environments. The edge node is a smartphone equipped with a Qualcomm Snapdragon 8 Gen 2 processor, executing our TFLite FP16 model using the Hexagon NPU. The cloud node runs in a Kubernetes cluster with containerized microservice pods fronted by an NGINX ingress controller with TLS 1.3 encryption. Database nodes host PostgreSQL with pgvector and Redis in-memory cache.")

    # ==========================================
    # SLIDE 15: RESTFUL API DESIGN
    # ==========================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15, BG_LIGHT)
    add_header(s15, "Service Contracts", "RESTful API Specification: Service Endpoints & Data Payloads", "Clean REST contracts connecting the edge mobile client to cloud analytical microservices")

    api_endpoints = [
        ("POST", "/api/v1/auth/login", "{ email, password }", "{ accessToken, expiresIn }", "Authenticates user and issues signed JWT bearer token.", TEAL),
        ("POST", "/api/v1/meals/session", "{ userId, mealType, plateRatio }", "{ sessionId, status }", "Initializes a meal capture session and records plate calibration ratio.", TEAL),
        ("POST", "/api/v1/meals/evaluate", "{ sessionId, items: [{ classId, maskArea, massGgrams }], embedding576 }", "{ calories, bioavailableYields: { Fe, Zn }, plateScore, requiresVerification }", "Core endpoint: evaluates nutritional intake, biochemical yields, and DGI score.", INDIGO),
        ("POST", "/api/v1/active-learning/feedback", "{ sessionId, instanceId, correctedClassId, embedding576 }", "{ status, galleryMatchCount }", "Ingests user-corrected dish labels into the pgvector embedding gallery.", AMBER),
        ("GET", "/api/v1/nutrition/items/{id}", "None", "{ foodId, className, calories, proteins, phytates, vitC }", "Retrieves baseline IFCT 2017 nutritional compositional metadata.", NAVY),
        ("GET", "/api/v1/biochem/matrix", "None", "{ matrixDimensions: 412x412, interactions: [...] }", "Fetches biochemical kinetic interaction parameters and half-saturation constants.", NAVY)
    ]

    for idx, (mth, ep, req, resp, purp, col) in enumerate(api_endpoints):
        ay = 1.9 + idx * 0.85
        add_card(s15, 0.8, ay, 11.7, 0.78)

        # Method Pill
        m_pill = s15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(ay + 0.15), Inches(0.9), Inches(0.48))
        m_pill.fill.solid()
        m_pill.fill.fore_color.rgb = col
        m_pill.line.color.rgb = col
        p = m_pill.text_frame.paragraphs[0]
        p.text = mth
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

        # Endpoint & Purpose
        tx = s15.shapes.add_textbox(Inches(1.9), Inches(ay + 0.05), Inches(4.5), Inches(0.68))
        tf = tx.text_frame
        p = tf.paragraphs[0]
        p.text = ep
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p_sub = tf.add_paragraph()
        p_sub.text = purp
        p_sub.font.size = Pt(8.5)
        p_sub.font.color.rgb = TEXT_DARK

        # Payloads
        tx_p = s15.shapes.add_textbox(Inches(6.5), Inches(ay + 0.05), Inches(5.8), Inches(0.68))
        tf_p = tx_p.text_frame
        p_req = tf_p.paragraphs[0]
        p_req.text = f"Request: {req}"
        p_req.font.size = Pt(8.5)
        p_req.font.color.rgb = TEXT_MUTED
        p_resp = tf_p.add_paragraph()
        p_resp.text = f"Response: {resp}"
        p_resp.font.size = Pt(8.5)
        p_resp.font.bold = True
        p_resp.font.color.rgb = TEAL if mth == "POST" else NAVY

    add_notes(s15, "Here is our RESTful API specification. All communications are secured with JWT tokens. The mobile app calls /meals/session to start logging, then dispatches segmented food IDs, portions, and visual vectors to /meals/evaluate. When a user corrects a label, /active-learning/feedback indexes the embedding vector. We also provide read endpoints for IFCT nutritional metadata and the biochemical interaction matrix.")

    # ==========================================
    # SLIDE 16: SECURITY, PRIVACY & PERFORMANCE
    # ==========================================
    s16 = prs.slides.add_slide(blank_layout)
    set_slide_background(s16, BG_LIGHT)
    add_header(s16, "Non-Functional Design", "Security, Privacy & Performance Architecture", "Safeguarding user dietary data and optimizing hardware runtime efficiency")

    sec_cards = [
        ("🔐 Authentication & Authorization", [
            "OAuth 2.0 with asymmetric RS256 JSON Web Tokens (JWT).",
            "Stateless authentication enables horizontal cloud microservice scaling.",
            "Token expiration (15-min access, 7-day refresh) mitigates credential replay."
        ], TEAL),
        ("🛡️ On-Device Privacy Protection", [
            "Camera frames are processed strictly in-memory on the mobile device.",
            "Raw image bitmaps are discarded immediately after feature extraction.",
            "Only non-PII numerical data (class IDs, mass in grams, 576-D vectors) leave the phone."
        ], INDIGO),
        ("🔒 Encryption & Data Security", [
            "Data in transit across edge and cloud is enforced with TLS 1.3 HTTPS.",
            "Data at rest (dietary history, user targets) is encrypted using AES-256.",
            "Database backups and sensitive credentials secured via AWS KMS / HashiCorp Vault."
        ], NAVY),
        ("⚡ High-Speed Caching & Sub-5ms Vectors", [
            "Redis In-Memory Cache stores 412 static IFCT food composition profiles.",
            "HNSW indexing over 576-D embeddings yields sub-5 ms cosine similarity lookups.",
            "24.8 ms mobile execution at 420 mW prevents thermal throttling and saves battery."
        ], AMBER)
    ]

    for idx, (head, items, col) in enumerate(sec_cards):
        row = idx // 2
        col_idx = idx % 2
        cx = 0.8 + col_idx * 5.95
        cy = 1.9 + row * 2.55
        add_card(s16, cx, cy, 5.75, 2.4)

        hbar = s16.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(cx), Inches(cy), Inches(5.75), Inches(0.35))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = col
        hbar.line.color.rgb = col
        p = hbar.text_frame.paragraphs[0]
        p.text = head
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE

        tx = s16.shapes.add_textbox(Inches(cx + 0.15), Inches(cy + 0.4), Inches(5.45), Inches(1.9))
        tf = tx.text_frame
        for it in items:
            p_it = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
            p_it.text = f"• {it}"
            p_it.font.size = Pt(10)
            p_it.font.color.rgb = TEXT_DARK

    add_notes(s16, "Security and performance are central to our design. First, user privacy is safeguarded by running the computer vision pipeline strictly in-memory on the phone—raw camera frames are never transmitted to the cloud. Second, all REST traffic uses TLS 1.3 and database records are encrypted with AES-256. For performance, Redis caches the 412 IFCT food items, and HNSW indexing ensures sub-5ms vector matching.")

    # ==========================================
    # SLIDE 17: SYSTEM ADVANTAGES & BENCHMARKS
    # ==========================================
    s17 = prs.slides.add_slide(blank_layout)
    set_slide_background(s17, BG_LIGHT)
    add_header(s17, "Engineering Outcomes", "System Advantages: Empirical Benchmarks & Clinical Impact", "Quantified achievements of the NutriPlate architecture against traditional dietary baselines")

    adv_cards = [
        ("⚡ 24.8 ms Edge Execution", "7.5x faster than Mask R-CNN (186.4 ms). Operates within real-time (>30 FPS) mobile latency budget without cloud video streaming costs.", TEAL),
        ("🥣 Amorphous Fluid Segmentation", "ProtoNet head synthesizes continuous prototype masks, accurately decomposing overlapping curries and gravies where bounding boxes fail.", INDIGO),
        ("⚖️ 8.8% Portion Mass Error (MAPE)", "Calibrated against standard 28 cm thali reference and culinary morphometric shape factors xi in [0.4, 1.2], outperforming bounding boxes (23.4%).", AMBER),
        ("🔬 Non-Linear Bioavailability", "Models promoter-chelator kinetics (Vitamin C promoting Fe by +210%, phytates binding Zn). Correlates with serum iron at r = 0.81 (vs. r = 0.42 raw).", NAVY),
        ("🥗 ICMR-NIN DGI 2024 Scoring", "Implements meal-context calorie budgets, protein adequacy (PE >= 10%), nocturnal carbohydrate penalties, and fiber incentives clamped in [10, 100].", TEAL),
        ("🔄 Zero-Retraining Adaptation", "576-D MobileNetV3 visual embeddings allow instant on-the-fly personalization to regional recipes upon user verification without network retraining.", INDIGO)
    ]

    for idx, (ahead, abody, acol) in enumerate(adv_cards):
        row = idx // 3
        col_idx = idx % 3
        cx = 0.8 + col_idx * 3.95
        cy = 1.9 + row * 2.55
        add_card(s17, cx, cy, 3.8, 2.4)

        hbar = s17.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(cx), Inches(cy), Inches(3.8), Inches(0.35))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = acol
        hbar.line.color.rgb = acol
        p = hbar.text_frame.paragraphs[0]
        p.text = ahead
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE

        tx = s17.shapes.add_textbox(Inches(cx + 0.15), Inches(cy + 0.45), Inches(3.5), Inches(1.85))
        tf = tx.text_frame
        tf.word_wrap = True
        p_b = tf.paragraphs[0]
        p_b.text = abody
        p_b.font.size = Pt(10)
        p_b.font.color.rgb = TEXT_DARK

    add_notes(s17, "Here are our key engineering advantages and benchmark results. NutriPlate achieves 24.8 ms edge execution, 7.5 times faster than Mask R-CNN. It solves amorphous gravy boundaries using ProtoNet prototypes. Our calibrated monocular portion approximation reduces mass error to 8.8% MAPE. Our biochemical interaction matrix improves predictive correlation with serum iron to r=0.81, and active learning enables zero-retraining regional adaptation.")

    # ==========================================
    # SLIDE 18: CONCLUSION & FUTURE ROADMAP
    # ==========================================
    s18 = prs.slides.add_slide(blank_layout)
    set_slide_background(s18, NAVY)

    # Accent decorative banner
    banner = s18.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.35), Inches(7.5))
    banner.fill.solid()
    banner.fill.fore_color.rgb = EMERALD
    banner.line.color.rgb = EMERALD

    pill = s18.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(0.8), Inches(3.0), Inches(0.4))
    pill.fill.solid()
    pill.fill.fore_color.rgb = TEAL
    pill.line.color.rgb = TEAL
    p = pill.text_frame.paragraphs[0]
    p.text = "CONCLUSION & FUTURE SCOPE"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER

    tx_c = s18.shapes.add_textbox(Inches(1.2), Inches(1.4), Inches(11.0), Inches(1.2))
    tf_c = tx_c.text_frame
    p_c1 = tf_c.paragraphs[0]
    p_c1.text = "Summary of OOMD System Design Achievements"
    p_c1.font.size = Pt(28)
    p_c1.font.bold = True
    p_c1.font.color.rgb = WHITE

    # Left Card: Summary
    card_sum = add_card(s18, 1.2, 2.7, 5.2, 4.0, bg_color=DARK_BLUE, border_color=TEAL)
    tx_s = s18.shapes.add_textbox(Inches(1.4), Inches(2.85), Inches(4.8), Inches(3.7))
    tf_s = tx_s.text_frame
    tf_s.word_wrap = True
    p = tf_s.paragraphs[0]
    p.text = "SYSTEM DESIGN DOCUMENT SUMMARY"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = EMERALD

    summary_bullets = [
        "Unified Object, Database, Service, and Architecture layers into a coherent software engineering architecture.",
        "Decoupled edge-cloud topology separates high-frequency on-device computer vision from heavy nutritional reasoning.",
        "Normalized 3NF relational schema and 576-D vector database support scalable dietary logging across 412 food classes.",
        "Rigorous UML modeling (Use Case, Class, Sequence, Component, Deployment) delivers full multi-layer traceability."
    ]
    for b in summary_bullets:
        p_b = tf_s.add_paragraph()
        p_b.text = f"• {b}"
        p_b.font.size = Pt(10.5)
        p_b.font.color.rgb = WHITE

    # Right Card: Future Scope
    card_fut = add_card(s18, 6.8, 2.7, 5.2, 4.0, bg_color=DARK_BLUE, border_color=INDIGO)
    tx_f = s18.shapes.add_textbox(Inches(7.0), Inches(2.85), Inches(4.8), Inches(3.7))
    tf_f = tx_f.text_frame
    tf_f.word_wrap = True
    p = tf_f.paragraphs[0]
    p.text = "FUTURE RESEARCH & ENGINEERING ROADMAP"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = INDIGO

    future_bullets = [
        "Time-of-Flight (ToF) Depth Sensor Fusion: Integrating smartphone 3D ToF sensors for direct dense point-cloud volume reconstruction.",
        "Continuous Glucose Monitor (CGM) Telemetry: Feeding real-time postprandial glycemic excursions into personalized scoring models.",
        "Cross-Lingual Voice Logging: Multilingual Indian speech interfaces for conversational dish verification and dietary tracking.",
        "Edge INT8 Quantization: Lowering mobile latency from 24.8 ms to sub-15 ms via INT8 quantization on edge NPUs."
    ]
    for b in future_bullets:
        p_b = tf_f.add_paragraph()
        p_b.text = f"• {b}"
        p_b.font.size = Pt(10.5)
        p_b.font.color.rgb = WHITE

    add_notes(s18, "In conclusion, this System Design Document successfully bridges object-oriented modeling with deep learning and biochemical science. We unified our object, database, service, and architectural layers to create a scalable platform tailored specifically for Indian cuisine. In the future, we plan to fuse Time-of-Flight depth sensors and integrate Continuous Glucose Monitor telemetry for personalized glycemic management. Thank you, and I am now ready for questions.")

    out_path = r"c:\Users\ADMIN\Downloads\SEProject\NutriPlate_OOMD_Presentation.pptx"
    prs.save(out_path)
    print(f"Presentation successfully saved to {out_path} with {len(prs.slides)} slides!")

if __name__ == "__main__":
    create_deck()
