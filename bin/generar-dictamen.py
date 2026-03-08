#!/usr/bin/env python3
"""
Generador de Dictamen de Clasificación Arancelaria en PDF.

Uso:
  python3 generar-dictamen.py dictamen.json [output.pdf]
  echo '{"producto": "...", ...}' | python3 generar-dictamen.py - [output.pdf]

El JSON de entrada debe tener la estructura DictamenData (ver abajo).
"""

import json
import sys
import os
from datetime import datetime
from fpdf import FPDF

# ============================================================================
# DATA MODEL
# ============================================================================

EJEMPLO_JSON = {
    "id_tramite": "CLF-2026-0042",
    "fecha": "2026-03-08",
    "producto": {
        "descripcion": "Notebook portátil con pantalla de 15.6 pulgadas, procesador Intel i7, 16GB RAM, 512GB SSD",
        "origen": "China",
        "uso": "Procesamiento de datos, uso personal y profesional"
    },
    "clasificacion": {
        "ncm": "8471.30.19",
        "sim": "8471.30.19.000U",
        "descripcion_oficial": "Máquinas automáticas para tratamiento o procesamiento de datos, portátiles, de peso inferior o igual a 10 kg, que estén constituidas, al menos, por una unidad central de proceso, un teclado y un visualizador - Las demás"
    },
    "fundamento": {
        "rgi": [
            {
                "regla": "RGI 1",
                "aplicacion": "El texto de la partida 84.71 describe literalmente 'Máquinas automáticas para tratamiento o procesamiento de datos'. El producto es una notebook que cumple esta función."
            },
            {
                "regla": "RGI 6",
                "aplicacion": "A nivel subpartida, 8471.30 corresponde a máquinas portátiles de peso <= 10 kg con CPU + teclado + pantalla. La notebook cumple todos los criterios."
            }
        ],
        "notas_consultadas": [
            {
                "tipo": "Sección XVI",
                "contenido": "Sin exclusiones aplicables al producto."
            },
            {
                "tipo": "Capítulo 84, Nota 6",
                "contenido": "Define 'máquina automática para tratamiento de datos' como aquella que puede almacenar el programa de tratamiento, ser programada por el usuario, y ejecutar operaciones aritméticas."
            },
            {
                "tipo": "Nota Explicativa 84.71",
                "contenido": "Incluye computadoras portátiles (laptops, notebooks) con unidad central, teclado y pantalla integrados."
            }
        ],
        "precedentes": [
            {
                "dictamen": "DI-2024-1234",
                "descripcion": "Notebook marca similar clasificada en 8471.30.19"
            }
        ]
    },
    "exclusiones": [
        {
            "codigo": "8528.52",
            "motivo": "Monitores/pantallas - Descartado porque el producto no es solo un monitor sino una máquina completa de procesamiento de datos (Nota 6 Cap. 84)"
        },
        {
            "codigo": "8471.41",
            "motivo": "Máquinas con unidad de proceso + E/S - Descartado por RGI 3a: 8471.30 es más específica para portátiles < 10 kg"
        }
    ],
    "aranceles": {
        "die": "14%",
        "tasa_estadistica": "3%",
        "iva": "21%",
        "iva_adicional": "20%",
        "iibb": "2.5%",
        "antidumping": None,
        "intervenciones": [],
        "licencias": None
    },
    "confianza": 85
}


# ============================================================================
# PDF GENERATOR
# ============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
LOGO_PATH = os.path.join(PROJECT_DIR, "assets", "logo-tarifar.png")


class DictamenPDF(FPDF):
    """PDF generator for classification dictamen."""

    MARGIN = 20
    BLUE = (22, 33, 62)       # #16213e
    ORANGE = (233, 147, 46)   # Tarifar orange
    RED = (200, 60, 60)
    GRAY = (140, 140, 140)
    LIGHT_GRAY = (200, 200, 200)
    LIGHT_BG = (248, 248, 248)
    WHITE = (255, 255, 255)
    BLACK = (40, 40, 40)

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(self.MARGIN, self.MARGIN, self.MARGIN)

    def header(self):
        if self.page_no() == 1:
            return
        # Minimal header for subsequent pages
        logo_path = LOGO_PATH
        if os.path.exists(logo_path):
            self.image(logo_path, x=self.MARGIN, y=8, h=8)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*self.GRAY)
        self.cell(0, 8, f"Pagina {self.page_no()}", align="R")
        self.set_y(20)
        self.set_draw_color(*self.LIGHT_GRAY)
        self.set_line_width(0.3)
        self.line(self.MARGIN, 18, self.w - self.MARGIN, 18)
        self.ln(3)

    def footer(self):
        self.set_draw_color(*self.LIGHT_GRAY)
        self.set_line_width(0.3)
        self.line(self.MARGIN, self.h - 15, self.w - self.MARGIN, self.h - 15)
        self.set_y(-13)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*self.GRAY)
        self.cell(0, 5, "tarifar.com", align="L")
        self.cell(0, 5, f"{self.page_no()} / {{nb}}", align="R")

    def title_block(self, data):
        """Draw the title block on page 1 — minimal white background."""
        # Logo - left aligned, generous size
        logo_path = LOGO_PATH
        if os.path.exists(logo_path):
            self.image(logo_path, x=self.MARGIN, y=15, h=15)

        # Thin line separator
        self.set_draw_color(*self.LIGHT_GRAY)
        self.set_line_width(0.3)
        self.line(self.MARGIN, 35, self.w - self.MARGIN, 35)

        # Title
        self.set_y(40)
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(*self.BLUE)
        self.cell(0, 10, "Dictamen de Clasificacion", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 22)
        self.set_text_color(*self.BLACK)
        self.cell(0, 10, "Arancelaria", new_x="LMARGIN", new_y="NEXT")

        # Reference and date - right aligned, subtle
        id_tramite = data.get("id_tramite", "S/N")
        fecha = data.get("fecha", datetime.now().strftime("%Y-%m-%d"))
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*self.GRAY)
        self.set_y(40)
        self.cell(0, 6, f"Ref: {id_tramite}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, f"Fecha: {fecha}", align="R", new_x="LMARGIN", new_y="NEXT")

        self.set_y(65)

    def section_title(self, number, title):
        """Draw a section title — minimal style."""
        self.ln(5)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*self.ORANGE)
        self.cell(8, 7, f"{number}")
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*self.BLUE)
        self.cell(0, 7, title.upper(), new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def label_value(self, label, value, bold_value=False):
        """Draw a label: value pair."""
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*self.GRAY)
        self.cell(45, 6, f"{label}:", align="R")
        self.set_font("Helvetica", "B" if bold_value else "", 9)
        self.set_text_color(*self.BLACK)
        self.multi_cell(0, 6, f"  {value}", new_x="LMARGIN", new_y="NEXT")

    def body_text(self, text, indent=0):
        """Draw body text."""
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*self.BLACK)
        if indent:
            self.set_x(self.MARGIN + indent)
            self.multi_cell(self.w - 2 * self.MARGIN - indent, 5, text, new_x="LMARGIN", new_y="NEXT")
        else:
            self.multi_cell(0, 5, text, new_x="LMARGIN", new_y="NEXT")

    def bullet(self, text, indent=10):
        """Draw a bullet point."""
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*self.BLACK)
        self.set_x(self.MARGIN + indent)
        self.cell(5, 5, "-")
        self.multi_cell(self.w - 2 * self.MARGIN - indent - 5, 5, text, new_x="LMARGIN", new_y="NEXT")

    def highlight_box(self, text, bg_color=None):
        """Draw a highlighted box — minimal with left accent."""
        x = self.MARGIN
        y = self.get_y()
        w = self.w - 2 * self.MARGIN
        # Left accent bar
        self.set_fill_color(*self.ORANGE)
        self.rect(x, y, 2, 14, style="F")
        # Light background
        self.set_fill_color(*self.LIGHT_BG)
        self.rect(x + 2, y, w - 2, 14, style="F")
        # Text
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*self.BLUE)
        self.set_xy(x + 8, y + 3)
        self.cell(w - 12, 8, text)
        self.set_y(y + 18)

    def exclusion_item(self, codigo, motivo):
        """Draw an exclusion item — minimal."""
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*self.RED)
        self.set_x(self.MARGIN + 5)
        self.cell(25, 5, codigo)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*self.GRAY)
        self.multi_cell(0, 5, motivo, new_x="LMARGIN", new_y="NEXT")

    def confidence_bar(self, percentage):
        """Draw a confidence percentage — minimal circular style."""
        x = self.MARGIN + 5
        y = self.get_y() + 2

        # Simple: large number + thin bar
        self.set_font("Helvetica", "B", 28)
        if percentage >= 70:
            self.set_text_color(39, 174, 96)
        elif percentage >= 50:
            self.set_text_color(*self.ORANGE)
        else:
            self.set_text_color(*self.RED)
        self.set_xy(x, y)
        self.cell(30, 15, f"{percentage}%")

        # Label
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*self.GRAY)
        self.set_xy(x + 32, y + 4)
        self.cell(40, 8, "confianza")

        # Thin bar
        bar_x = x + 65
        bar_w = 80
        bar_h = 3
        bar_y = y + 7
        self.set_fill_color(235, 235, 235)
        self.rect(bar_x, bar_y, bar_w, bar_h, style="F")
        if percentage >= 70:
            self.set_fill_color(39, 174, 96)
        elif percentage >= 50:
            self.set_fill_color(*self.ORANGE)
        else:
            self.set_fill_color(*self.RED)
        self.rect(bar_x, bar_y, bar_w * percentage / 100, bar_h, style="F")

        self.set_y(y + 20)


def generate_dictamen(data, output_path):
    """Generate the dictamen PDF from structured data."""
    pdf = DictamenPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    # ===== TITLE =====
    pdf.title_block(data)

    # ===== 1. PRODUCTO =====
    pdf.section_title("1", "PRODUCTO")
    producto = data.get("producto", {})
    pdf.label_value("Descripcion", producto.get("descripcion", "N/A"))
    pdf.label_value("Origen", producto.get("origen", "No especificado"))
    pdf.label_value("Uso / Destino", producto.get("uso", "N/A"))

    # ===== 2. CLASIFICACION =====
    pdf.section_title("2", "CLASIFICACION SUGERIDA")
    clasif = data.get("clasificacion", {})
    ncm = clasif.get("ncm", "N/A")
    sim = clasif.get("sim", "")

    pdf.highlight_box(f"NCM: {ncm}" + (f"  |  SIM: {sim}" if sim else ""))
    pdf.label_value("Descripcion oficial", clasif.get("descripcion_oficial", "N/A"))

    # ===== 3. FUNDAMENTO LEGAL =====
    pdf.section_title("3", "FUNDAMENTO LEGAL")
    fundamento = data.get("fundamento", {})

    # 3.1 RGI
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*pdf.BLUE)
    pdf.cell(0, 7, "3.1 Reglas Generales Interpretativas (RGI)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    for rgi in fundamento.get("rgi", []):
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*pdf.BLACK)
        pdf.set_x(pdf.MARGIN + 5)
        pdf.cell(0, 5, rgi.get("regla", ""), new_x="LMARGIN", new_y="NEXT")
        pdf.body_text(rgi.get("aplicacion", ""), indent=10)
        pdf.ln(2)

    # 3.2 Notas
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*pdf.BLUE)
    pdf.cell(0, 7, "3.2 Notas Legales y Explicativas Consultadas", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    for nota in fundamento.get("notas_consultadas", []):
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*pdf.BLUE)
        pdf.set_x(pdf.MARGIN + 5)
        pdf.cell(0, 5, nota.get("tipo", ""), new_x="LMARGIN", new_y="NEXT")
        pdf.body_text(nota.get("contenido", ""), indent=10)
        pdf.ln(1)

    # 3.3 Precedentes
    precedentes = fundamento.get("precedentes", [])
    if precedentes:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*pdf.BLUE)
        pdf.cell(0, 7, "3.3 Precedentes (Resoluciones de Clasificacion)", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        for prec in precedentes:
            pdf.bullet(f"{prec.get('dictamen', 'N/A')}: {prec.get('descripcion', '')}")

    # ===== 4. EXCLUSIONES =====
    pdf.section_title("4", "POSICIONES DESCARTADAS")
    exclusiones = data.get("exclusiones", [])
    if exclusiones:
        for exc in exclusiones:
            pdf.exclusion_item(exc.get("codigo", ""), exc.get("motivo", ""))
            pdf.ln(1)
    else:
        pdf.body_text("No se documentaron exclusiones.")

    # ===== 5. INFORMACION ARANCELARIA =====
    pdf.section_title("5", "INFORMACION ARANCELARIA")
    aranceles = data.get("aranceles", {})

    arancel_items = [
        ("DIE (Derecho Import. Extrazona)", aranceles.get("die", "N/A")),
        ("Tasa Estadistica", aranceles.get("tasa_estadistica", "N/A")),
        ("IVA", aranceles.get("iva", "21%")),
        ("IVA Adicional", aranceles.get("iva_adicional", "N/A")),
        ("IIBB (Ingresos Brutos)", aranceles.get("iibb", "N/A")),
    ]

    for label, value in arancel_items:
        if value and value != "N/A":
            pdf.label_value(label, value)

    antidumping = aranceles.get("antidumping")
    if antidumping:
        pdf.label_value("Derecho Antidumping", antidumping, bold_value=True)

    intervenciones = aranceles.get("intervenciones", [])
    if intervenciones:
        pdf.label_value("Intervenciones", ", ".join(intervenciones))

    licencias = aranceles.get("licencias")
    if licencias:
        pdf.label_value("Licencias", licencias)

    # ===== 6. CONFIANZA =====
    pdf.section_title("6", "NIVEL DE CONFIANZA")
    confianza = data.get("confianza", 0)
    pdf.confidence_bar(confianza)

    # ===== 7. DISCLAIMER =====
    pdf.section_title("7", "AVISO LEGAL")
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(*pdf.GRAY)
    disclaimer = (
        "Este dictamen es una sugerencia tecnica basada en la informacion proporcionada y las fuentes "
        "consultadas (Tarifar MCP, Nomenclatura Comun del Mercosur, Sistema Armonizado de la OMA, "
        "Notas Explicativas del SA). NO constituye una clasificacion oficial ni vinculante. "
        "Se recomienda verificacion con un despachante de aduanas matriculado y/o consulta vinculante "
        "ante la Direccion General de Aduanas (ARCA).\n\n"
        "La informacion arancelaria corresponde a la vigente al momento de la consulta y puede estar "
        "sujeta a modificaciones por normativa posterior."
    )
    pdf.multi_cell(0, 4, disclaimer, new_x="LMARGIN", new_y="NEXT")

    # Save
    pdf.output(output_path)
    return output_path


# ============================================================================
# CLI
# ============================================================================

def main():
    if len(sys.argv) < 2:
        print(f"Uso: {sys.argv[0]} <dictamen.json | -> [output.pdf]")
        print(f"\nEjemplo JSON:\n{json.dumps(EJEMPLO_JSON, indent=2, ensure_ascii=False)}")
        sys.exit(1)

    input_path = sys.argv[1]
    
    if input_path == "-":
        data = json.load(sys.stdin)
    else:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    # Output path
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        id_tramite = data.get("id_tramite", "dictamen")
        fecha = data.get("fecha", datetime.now().strftime("%Y-%m-%d"))
        output_path = f"/tmp/dictamen-{id_tramite}-{fecha}.pdf"

    result = generate_dictamen(data, output_path)
    print(result)


if __name__ == "__main__":
    main()
