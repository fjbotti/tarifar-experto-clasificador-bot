# TOOLS.md - Herramientas del Clasificador

## PDF - Generacion de Informes

**HERRAMIENTA UNICA para generar PDF: `bin/generar-dictamen.py`**

Este script genera PDFs profesionales con el logo de Tarifar, diseño minimalista y 7 secciones.

### Como usar:

```bash
mkdir -p output

# 1. Crear el JSON con los datos de la clasificacion
cat > output/informe-input.json << 'JSONEOF'
{
  "id_tramite": "TAR-2026-XX-XXXX",
  "fecha": "2026-03-08",
  "producto": {
    "descripcion": "...",
    "origen": "...",
    "uso": "...",
    "caracteristicas": {"clave": "valor"}
  },
  "clasificacion": {
    "ncm": "XXXX.XX.XX",
    "sim": "XXXX.XX.XX.XXX Z",
    "descripcion_oficial": "..."
  },
  "jerarquia": [
    {"nivel": "Seccion XVI", "detalle": "..."},
    {"nivel": "Capitulo 85", "detalle": "..."}
  ],
  "fundamento": {
    "rgi": [{"regla": "RGI 1", "aplicacion": "..."}],
    "notas_consultadas": [{"tipo": "Cap XX", "contenido": "..."}],
    "precedentes": [{"dictamen": "...", "descripcion": "..."}]
  },
  "marcha_clasificatoria": [
    {"titulo": "Analisis del producto", "detalle": "..."},
    {"titulo": "Seccion y Capitulo", "detalle": "..."}
  ],
  "comparativo": [
    {"posicion": "XXXX.XX", "descripcion": "...", "die": "0%", "iva": "10.5%", "resultado": "SELECCIONADA"}
  ],
  "exclusiones": [{"codigo": "XXXX.XX", "motivo": "..."}],
  "aranceles": {
    "die": "0%", "tasa_estadistica": "0%", "iva": "10.5%",
    "iva_adicional": "10%", "ganancias": "6%", "iibb": "2.5%",
    "antidumping": null, "intervenciones": [], "licencias": null
  },
  "calculo_cif": {
    "valor_cif": "500",
    "desglose": [{"concepto": "DIE", "alicuota": "0%", "monto": "0"}],
    "total_tributos": "145.00",
    "costo_total": "645.00"
  },
  "observaciones": [
    {"titulo": "Regulacion X", "detalle": "..."}
  ],
  "confianza": 92
}
JSONEOF

# 2. Generar el PDF
python3 bin/generar-dictamen.py output/informe-input.json output/informe-clasificacion.pdf

# 3. Enviar al usuario (usar ruta output/informe-clasificacion.pdf)
```

### REGLAS ABSOLUTAS:
- SOLO usar `python3 bin/generar-dictamen.py` para PDFs
- Guardar SIEMPRE en `output/` (nunca en /tmp/)
- NO usar HTML + weasyprint
- NO usar HTML + chromium/puppeteer
- NO usar fpdf/reportlab directamente
- NO generar HTML de ninguna forma
- Caracteres ASCII solamente en el JSON (sin acentos, sin ñ, sin emojis)
