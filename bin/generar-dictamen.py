#!/usr/bin/env python3
"""
Generador de Dictamen de Clasificacion Arancelaria en PDF.
Diseno minimalista con logo Tarifar. Estructura completa de 7 secciones.

Uso:
  python3 generar-dictamen.py dictamen.json [output.pdf]
  echo '{ ... }' | python3 generar-dictamen.py - [output.pdf]
"""

import json
import sys
import os
from datetime import datetime
from fpdf import FPDF

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
LOGO_PATH = os.path.join(PROJECT_DIR, "assets", "logo-tarifar.png")


class DictamenPDF(FPDF):
    MARGIN = 18
    BLUE = (22, 33, 62)
    ORANGE = (233, 147, 46)
    GREEN = (39, 174, 96)
    RED = (200, 60, 60)
    GRAY = (130, 130, 130)
    LIGHT_GRAY = (210, 210, 210)
    LIGHT_BG = (247, 248, 250)
    BLACK = (40, 40, 40)
    WHITE = (255, 255, 255)

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(self.MARGIN, self.MARGIN, self.MARGIN)

    def header(self):
        if self.page_no() == 1:
            return
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, x=self.MARGIN, y=8, h=7)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*self.GRAY)
        self.cell(0, 8, f"Pagina {self.page_no()}", align="R")
        self.set_draw_color(*self.LIGHT_GRAY)
        self.set_line_width(0.2)
        self.line(self.MARGIN, 17, self.w - self.MARGIN, 17)
        self.set_y(20)

    def footer(self):
        self.set_draw_color(*self.LIGHT_GRAY)
        self.set_line_width(0.2)
        self.line(self.MARGIN, self.h - 14, self.w - self.MARGIN, self.h - 14)
        self.set_y(-12)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*self.GRAY)
        self.cell(0, 5, "Tarifar Bot  --  tarifar.com", align="L")
        self.cell(0, 5, f"Pagina {self.page_no()} / {{nb}}", align="R")

    # ── Layout helpers ──

    def title_block(self, data):
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, x=self.MARGIN, y=12, h=14)
        self.set_draw_color(*self.LIGHT_GRAY)
        self.set_line_width(0.2)
        self.line(self.MARGIN, 30, self.w - self.MARGIN, 30)
        self.set_y(34)
        self.set_font("Helvetica", "B", 20)
        self.set_text_color(*self.BLUE)
        self.cell(0, 9, "Informe de Clasificacion", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 20)
        self.set_text_color(*self.BLACK)
        self.cell(0, 9, "Arancelaria", new_x="LMARGIN", new_y="NEXT")
        # Ref + date right-aligned
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*self.GRAY)
        self.set_y(34)
        ref = data.get("id_tramite", "S/N")
        fecha = data.get("fecha", datetime.now().strftime("%Y-%m-%d"))
        self.cell(0, 5, f"Ref: {ref}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, f"Fecha: {fecha}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_y(56)

    def section(self, num, title):
        self.ln(4)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*self.ORANGE)
        self.cell(7, 7, str(num))
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*self.BLUE)
        self.cell(0, 7, title.upper(), new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def subsection(self, title):
        self.ln(2)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*self.BLUE)
        self.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def lv(self, label, value, bold_val=False):
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*self.GRAY)
        self.cell(42, 5, label, align="R")
        self.set_font("Helvetica", "B" if bold_val else "", 9)
        self.set_text_color(*self.BLACK)
        self.multi_cell(0, 5, f"  {value}", new_x="LMARGIN", new_y="NEXT")

    def text(self, t, indent=0, size=9):
        self.set_font("Helvetica", "", size)
        self.set_text_color(*self.BLACK)
        if indent:
            self.set_x(self.MARGIN + indent)
            self.multi_cell(self.w - 2 * self.MARGIN - indent, 5, t, new_x="LMARGIN", new_y="NEXT")
        else:
            self.multi_cell(0, 5, t, new_x="LMARGIN", new_y="NEXT")

    def accent_box(self, t, accent_color=None):
        if accent_color is None:
            accent_color = self.ORANGE
        x, y = self.MARGIN, self.get_y()
        w = self.w - 2 * self.MARGIN
        self.set_fill_color(*accent_color)
        self.rect(x, y, 2, 14, style="F")
        self.set_fill_color(*self.LIGHT_BG)
        self.rect(x + 2, y, w - 2, 14, style="F")
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*self.BLUE)
        self.set_xy(x + 8, y + 3)
        self.cell(w - 12, 8, t)
        self.set_y(y + 17)

    def table_header(self, cols, widths):
        self.set_fill_color(*self.LIGHT_BG)
        self.set_font("Helvetica", "B", 7)
        self.set_text_color(*self.GRAY)
        for i, col in enumerate(cols):
            self.cell(widths[i], 6, col.upper(), border=0, fill=True, align="L" if i == 0 else "C")
        self.ln()

    def table_row(self, values, widths, bold=False, color=None, wrap_last=False):
        self.set_font("Helvetica", "B" if bold else "", 8)
        self.set_text_color(*(color or self.BLACK))
        if wrap_last and len(values) >= 2:
            # Fixed columns + wrapping last column
            x0 = self.get_x()
            y0 = self.get_y()
            for i in range(len(values) - 1):
                self.set_xy(x0 + sum(widths[:i]), y0)
                txt = str(values[i])[:50]
                self.cell(widths[i], 5, txt, align="L" if i == 0 else "C")
            last_i = len(values) - 1
            self.set_xy(x0 + sum(widths[:last_i]), y0)
            self.multi_cell(widths[last_i], 5, str(values[last_i]), align="L", new_x="LMARGIN", new_y="NEXT")
            if self.get_y() <= y0 + 5:
                self.set_y(y0 + 5)
        else:
            # Simple single-line row (all cells)
            for i, val in enumerate(values):
                txt = str(val)
                # Truncate to fit in cell width roughly (1 char ~ 2pt at size 8)
                max_chars = int(widths[i] / 2) if widths[i] > 0 else 80
                if len(txt) > max_chars:
                    txt = txt[:max_chars - 2] + ".."
                self.cell(widths[i], 5, txt, align="L" if i == 0 else "C")
            self.ln()

    def confidence_display(self, pct):
        x, y = self.MARGIN + 5, self.get_y() + 2
        self.set_font("Helvetica", "B", 26)
        c = self.GREEN if pct >= 70 else self.ORANGE if pct >= 50 else self.RED
        self.set_text_color(*c)
        self.set_xy(x, y)
        self.cell(28, 14, f"{pct}%")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*self.GRAY)
        self.set_xy(x + 30, y + 4)
        self.cell(30, 6, "confianza")
        bx, by, bw, bh = x + 63, y + 7, 80, 3
        self.set_fill_color(235, 235, 235)
        self.rect(bx, by, bw, bh, style="F")
        self.set_fill_color(*c)
        self.rect(bx, by, bw * pct / 100, bh, style="F")
        self.set_y(y + 18)


def generate(data, out):
    pdf = DictamenPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.title_block(data)

    prod = data.get("producto", {})
    clasif = data.get("clasificacion", {})
    fund = data.get("fundamento", {})
    excl = data.get("exclusiones", [])
    aran = data.get("aranceles", {})
    conf = data.get("confianza", 0)
    jerarquia = data.get("jerarquia", [])
    marcha = data.get("marcha_clasificatoria", [])
    comparativo = data.get("comparativo", [])
    observaciones = data.get("observaciones", [])
    cif = data.get("calculo_cif", {})

    # ── 1. CLASIFICACION PROPUESTA ──
    pdf.section(1, "Clasificacion Propuesta")
    ncm = clasif.get("ncm", "N/A")
    sim = clasif.get("sim", "")
    label = f"NCM: {ncm}"
    if sim:
        label += f"   |   SIM: {sim}"
    pdf.accent_box(label, pdf.GREEN)
    pdf.text(clasif.get("descripcion_oficial", ""), size=8)
    pdf.ln(2)

    # Jerarquia NCM table
    if jerarquia:
        col1_w = 38
        col2_w = pdf.w - 2 * pdf.MARGIN - col1_w
        ws = [col1_w, col2_w]
        pdf.table_header(["Nivel", "Detalle"], ws)
        for j in jerarquia:
            pdf.table_row([j.get("nivel", ""), j.get("detalle", "")], ws, wrap_last=True)
        pdf.ln(2)

    # Confidence
    pdf.confidence_display(conf)

    # ── 2. ANALISIS DEL PRODUCTO ──
    pdf.section(2, "Analisis del Producto")
    pdf.lv("Descripcion", prod.get("descripcion", "N/A"))
    pdf.lv("Origen", prod.get("origen", "No especificado"))
    pdf.lv("Uso / Destino", prod.get("uso", "N/A"))
    # Extra characteristics
    for k, v in prod.get("caracteristicas", {}).items():
        pdf.lv(k, v)

    # ── 3. FUNDAMENTO DE LA CLASIFICACION ──
    pdf.section(3, "Fundamento de la Clasificacion")

    # 3.1 RGI
    pdf.subsection("3.1 Reglas Generales Interpretativas (RGI)")
    for rgi in fund.get("rgi", []):
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*pdf.BLACK)
        pdf.set_x(pdf.MARGIN + 5)
        pdf.cell(0, 5, rgi.get("regla", ""), new_x="LMARGIN", new_y="NEXT")
        pdf.text(rgi.get("aplicacion", ""), indent=10, size=8)
        pdf.ln(1)

    # 3.2 Notas consultadas
    pdf.subsection("3.2 Notas Legales y Explicativas Consultadas")
    for n in fund.get("notas_consultadas", []):
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*pdf.BLUE)
        pdf.set_x(pdf.MARGIN + 5)
        pdf.cell(0, 5, n.get("tipo", ""), new_x="LMARGIN", new_y="NEXT")
        pdf.text(n.get("contenido", ""), indent=10, size=8)
        pdf.ln(1)

    # 3.3 Marcha clasificatoria
    if marcha:
        pdf.subsection("3.3 Marcha Clasificatoria Completa")
        for i, paso in enumerate(marcha, 1):
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(*pdf.ORANGE)
            pdf.set_x(pdf.MARGIN + 5)
            titulo = paso.get("titulo", f"Paso {i}")
            pdf.cell(0, 5, f"Paso {i} -- {titulo}", new_x="LMARGIN", new_y="NEXT")
            pdf.text(paso.get("detalle", ""), indent=10, size=8)
            pdf.ln(1)

    # ── 4. PRECEDENTES VINCULANTES ──
    precedentes = fund.get("precedentes", [])
    if precedentes:
        pdf.section(4, "Precedentes Vinculantes")
        for p in precedentes:
            x, y = pdf.MARGIN, pdf.get_y()
            w = pdf.w - 2 * pdf.MARGIN
            # Card with left orange accent
            pdf.set_fill_color(*pdf.ORANGE)
            pdf.rect(x, y, 2, 16)
            pdf.set_fill_color(*pdf.LIGHT_BG)
            pdf.rect(x + 2, y, w - 2, 16, style="F")
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(*pdf.BLUE)
            pdf.set_xy(x + 6, y + 2)
            pdf.cell(0, 5, p.get("dictamen", ""))
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(*pdf.BLACK)
            pdf.set_xy(x + 6, y + 8)
            desc = p.get("descripcion", "")[:120]
            pdf.cell(w - 12, 5, desc)
            pdf.set_y(y + 19)

    # ── 5. ARANCELES E IMPUESTOS ──
    pdf.section(5, "Aranceles e Impuestos a la Importacion")

    tributos = [
        ("DIE (Der. Import. Extrazona)", aran.get("die", "N/A")),
        ("Tasa Estadistica", aran.get("tasa_estadistica", "N/A")),
        ("IVA", aran.get("iva", "21%")),
        ("IVA Adicional", aran.get("iva_adicional", "")),
        ("IIBB (Ingresos Brutos)", aran.get("iibb", "")),
        ("Antic. Ganancias", aran.get("ganancias", "")),
    ]
    ws = [55, 25]
    pdf.table_header(["Tributo", "Alicuota"], ws)
    for label, val in tributos:
        if val and val != "N/A":
            pdf.table_row([label, val], ws)

    ad = aran.get("antidumping")
    if ad:
        pdf.table_row(["Derecho Antidumping", ad], ws, bold=True, color=pdf.RED)

    lic = aran.get("licencias")
    if lic:
        pdf.ln(1)
        pdf.lv("Licencias", lic)

    interv = aran.get("intervenciones", [])
    if interv:
        pdf.lv("Intervenciones", ", ".join(interv))

    # CIF calculation
    if cif:
        pdf.subsection(f"Carga tributaria estimada sobre CIF USD {cif.get('valor_cif', 'N/A')}")
        items_cif = cif.get("desglose", [])
        ws_cif = [55, 20, 25]
        pdf.table_header(["Concepto", "Alicuota", "Monto USD"], ws_cif)
        for item in items_cif:
            pdf.table_row([item.get("concepto",""), item.get("alicuota",""), item.get("monto","")], ws_cif)
        total = cif.get("total_tributos", "")
        costo = cif.get("costo_total", "")
        if total:
            pdf.ln(1)
            pdf.table_row(["TOTAL TRIBUTOS", "", f"$ {total}"], ws_cif, bold=True, color=pdf.BLUE)
        if costo:
            pdf.table_row(["COSTO TOTAL ESTIMADO", "", f"$ {costo}"], ws_cif, bold=True, color=pdf.GREEN)

    # ── 6. ANALISIS COMPARATIVO ──
    if comparativo or excl:
        pdf.section(6, "Posiciones Descartadas")
        if comparativo:
            total_w = pdf.w - 2 * pdf.MARGIN
            ws_comp = [32, int(total_w - 32 - 15 - 15 - 28), 15, 15, 28]
            pdf.table_header(["Posicion", "Descripcion", "DIE", "IVA", "Resultado"], ws_comp)
            for c in comparativo:
                res = c.get("resultado", "")
                color = pdf.GREEN if "SELECCIONADA" in res.upper() else pdf.RED
                pdf.table_row([
                    c.get("posicion", ""),
                    c.get("descripcion", ""),
                    c.get("die", ""),
                    c.get("iva", ""),
                    res
                ], ws_comp, color=color, wrap_last=True)
        elif excl:
            for e in excl:
                pdf.set_font("Helvetica", "B", 8)
                pdf.set_text_color(*pdf.RED)
                pdf.set_x(pdf.MARGIN + 5)
                pdf.cell(25, 5, e.get("codigo", ""))
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(*pdf.GRAY)
                pdf.multi_cell(0, 5, e.get("motivo", ""), new_x="LMARGIN", new_y="NEXT")
                pdf.ln(1)

    # ── 7. OBSERVACIONES ──
    if observaciones:
        pdf.section(7, "Observaciones y Requisitos")
        for obs in observaciones:
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(*pdf.BLACK)
            pdf.set_x(pdf.MARGIN + 5)
            pdf.cell(0, 5, f"- {obs.get('titulo', '')}", new_x="LMARGIN", new_y="NEXT")
            if obs.get("detalle"):
                pdf.text(obs["detalle"], indent=10, size=8)
            pdf.ln(1)

    # ── DISCLAIMER ──
    pdf.ln(5)
    pdf.set_draw_color(*pdf.LIGHT_GRAY)
    pdf.line(pdf.MARGIN, pdf.get_y(), pdf.w - pdf.MARGIN, pdf.get_y())
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*pdf.GRAY)
    pdf.multi_cell(0, 4,
        "Este informe es orientativo y no constituye una consulta vinculante ante la DGA/ARCA. "
        "Para clasificacion con fuerza legal: solicitar Consulta de Clasificacion Arancelaria "
        "ante la DGA (Art. 1100, Ley 22.415). La informacion arancelaria corresponde a la "
        "vigente al momento de la consulta y puede estar sujeta a modificaciones.",
        new_x="LMARGIN", new_y="NEXT")

    pdf.output(out)
    return out


EJEMPLO = {
    "id_tramite": "TAR-2026-03-0042",
    "fecha": "2026-03-08",
    "producto": {
        "descripcion": "Smartwatch (Reloj Inteligente) tipo Apple Watch con pantalla tactil OLED, sensores biometricos, WiFi y Bluetooth",
        "origen": "China (Assembled in China)",
        "uso": "Comunicacion, monitoreo biometrico, procesamiento de datos",
        "caracteristicas": {
            "Conectividad": "WiFi 2.4 GHz / Bluetooth 5.x",
            "Pantalla": "OLED/LTPO tactil",
            "Alimentacion": "Bateria ion-litio recargable",
            "Sensores": "FC, SpO2, ECG, acelerometro, giroscopio"
        }
    },
    "clasificacion": {
        "ncm": "8517.62.72",
        "sim": "8517.62.72.900 U",
        "descripcion_oficial": "Emisor con receptor incorporado, digital, frec. < 15 GHz y tasa <= 34 Mbits/s, excepto intercomunicadores - Los demas"
    },
    "jerarquia": [
        {"nivel": "Seccion XVI", "detalle": "Maquinas y aparatos, material electrico y sus partes"},
        {"nivel": "Capitulo 85", "detalle": "Maquinas, aparatos y material electrico y sus partes"},
        {"nivel": "Partida 8517", "detalle": "Telefonos inteligentes; demas aparatos de emision/transmision/recepcion"},
        {"nivel": "Subpartida 8517.62", "detalle": "Aparatos para recepcion, conversion, emision de datos"},
        {"nivel": "Item NCM 8517.62.72", "detalle": "Frec. < 15 GHz y tasa <= 34 Mbits/s"},
        {"nivel": "Sub-item SIM .900 U", "detalle": "Los demas"}
    ],
    "fundamento": {
        "rgi": [
            {"regla": "RGI 1", "aplicacion": "Texto de la partida 8517 + Notas Legales de Seccion XVI y Cap. 85. Nota 1 del Cap. 91 excluye el producto de relojeria."},
            {"regla": "RGI 6", "aplicacion": "A nivel subpartida, 8517.62.72 corresponde a emisores con receptor digital, frec. < 15 GHz, tasa <= 34 Mbits/s."}
        ],
        "notas_consultadas": [
            {"tipo": "Nota 1 Cap. 91 (Relojeria)", "contenido": "Excluye productos que pueden clasificarse en otras partidas. El smartwatch clasifica en 8517."},
            {"tipo": "Seccion XVI", "contenido": "Sin exclusiones aplicables."},
            {"tipo": "Capitulo 85", "contenido": "Sin exclusiones aplicables al producto."},
            {"tipo": "Nota Explicativa 85.17", "contenido": "Comprende aparatos de emision/transmision/recepcion de datos en redes inalambricas."}
        ],
        "precedentes": [
            {"dictamen": "Criterio OMA - DAT 2017", "descripcion": "Dispositivo utilizado en la muneca denominado Smart Watch. PA: 8517.62"},
            {"dictamen": "Dictamen 07/2017 - AFIP 4068/2017", "descripcion": "Dispositivo portatil de muneca, emisor con receptor digital, 2.4 GHz. PA: 8517.62.72"},
            {"dictamen": "Dictamen 89/2025 - DGA 5813/2026", "descripcion": "Smart Watch con funcionalidad de telefonia celular. Relevante si tiene LTE."}
        ]
    },
    "marcha_clasificatoria": [
        {"titulo": "Analisis del producto", "detalle": "Dispositivo electronico portatil de muneca con procesador, pantalla tactil, sensores, GPS, WiFi/BT."},
        {"titulo": "Seccion y Capitulo", "detalle": "Seccion XVI -> Capitulo 85. Nota 1 Cap. 91 excluye el producto de relojeria."},
        {"titulo": "Notas Explicativas", "detalle": "Partida 8517 comprende aparatos de emision/transmision/recepcion de datos inalambricos."},
        {"titulo": "Busqueda en DB", "detalle": "Verificadas posiciones 8517.13, 8517.62.72, 8517.62.99. La 8517.62.72 coincide tecnicamente."},
        {"titulo": "Verificacion de codigos", "detalle": "SIM 8517.62.72.900 U confirmado vigente en NCM/SIM Argentina."},
        {"titulo": "Resoluciones de clasificacion", "detalle": "3 precedentes: OMA 2017, AFIP 4068/2017, DGA 5813/2026."},
        {"titulo": "RGI aplicadas", "detalle": "RGI 1 (texto + notas legales). RGI 6 para subpartidas mutatis mutandis."},
        {"titulo": "Observaciones", "detalle": "28 observaciones consultadas. Aplica regulacion pilas/baterias de litio."}
    ],
    "exclusiones": [],
    "comparativo": [
        {"posicion": "8517.62.72.900 U", "descripcion": "Emisor c/receptor digital, frec. < 15 GHz", "die": "0%", "iva": "10.5%", "resultado": "SELECCIONADA"},
        {"posicion": "8517.13.00.000 C", "descripcion": "Telefonos inteligentes", "die": "0%", "iva": "21%", "resultado": "Solo con celular"},
        {"posicion": "8517.62.99.900 R", "descripcion": "Los demas (residual)", "die": "35%", "iva": "21%", "resultado": "Hay mas especifica"},
        {"posicion": "9102.xx (Cap. 91)", "descripcion": "Relojes de pulsera", "die": "20%", "iva": "21%", "resultado": "Excluido Nota 1"}
    ],
    "aranceles": {
        "die": "0%", "tasa_estadistica": "0%", "iva": "10.5%", "iva_adicional": "10%",
        "ganancias": "6%", "iibb": "2.5%", "antidumping": None, "intervenciones": [], "licencias": None
    },
    "calculo_cif": {
        "valor_cif": "500",
        "desglose": [
            {"concepto": "DIE", "alicuota": "0%", "monto": "0"},
            {"concepto": "Tasa Estadistica", "alicuota": "0%", "monto": "0"},
            {"concepto": "IVA", "alicuota": "10.5%", "monto": "52.50"},
            {"concepto": "IVA Adicional", "alicuota": "10%", "monto": "50.00"},
            {"concepto": "Antic. Ganancias", "alicuota": "6%", "monto": "30.00"},
            {"concepto": "IIBB", "alicuota": "2.5%", "monto": "12.50"}
        ],
        "total_tributos": "145.00",
        "costo_total": "645.00"
    },
    "observaciones": [
        {"titulo": "VI Enmienda del SA", "detalle": "Posicion incorporada por VI Enmienda, vigente desde 03/01/2018 (Dto. 1126/17)."},
        {"titulo": "Pilas y baterias de litio", "detalle": "Tramitar autorizacion ante Min. de Ambiente (Dir. Nac. Sustancias Quimicas) via TAD/GDE."},
        {"titulo": "ENACOM", "detalle": "Dispositivo WiFi/BT puede requerir homologacion (Res. ENACOM 2875/2016)."},
        {"titulo": "Acuerdos comerciales", "detalle": "Negociada en TLC Mercosur-Israel, Mercosur-SACU, Mercosur-Egipto. Verificar preferencias segun origen."}
    ],
    "confianza": 92
}


def main():
    if len(sys.argv) < 2:
        print(f"Uso: {sys.argv[0]} <dictamen.json | -> [output.pdf]")
        print(f"\nEjemplo JSON:\n{json.dumps(EJEMPLO, indent=2, ensure_ascii=False)}")
        sys.exit(1)

    src = sys.argv[1]
    data = json.load(sys.stdin) if src == "-" else json.load(open(src, encoding="utf-8"))
    out = sys.argv[2] if len(sys.argv) >= 3 else f"/tmp/informe-clasificacion-{data.get('id_tramite','out')}-{data.get('fecha', datetime.now().strftime('%Y-%m-%d'))}.pdf"
    print(generate(data, out))


if __name__ == "__main__":
    main()
