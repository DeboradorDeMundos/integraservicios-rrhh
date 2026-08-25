# generate_data.py
"""
Genera PDFs simulados de prueba para IntegraBot.

Crea en ./data tres documentos con texto normativo chileno:
- RIOHS_IntegraServicios_2026.pdf
- Contrato_Colectivo_2026.pdf
- Codigo_del_Trabajo_Chile.pdf
"""
import os

from fpdf import FPDF

DATA_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def latin(text: str) -> str:
    """Normaliza texto para las fuentes core de FPDF (Latin-1)."""
    replacements = {
        "\u2014": "-",
        "\u2013": "-",
        "\u201c": '"',
        "\u201d": '"',
        "\u2018": "'",
        "\u2019": "'",
        "\u2026": "...",
        "\u00a0": " ",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text.encode("latin-1", "replace").decode("latin-1")


class ManualPDF(FPDF):
    """PDF corporativo con encabezado y pie de pagina."""

    def __init__(self, title: str, subtitle: str):
        super().__init__()
        self.doc_title = title
        self.subtitle = subtitle
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        self.set_xy(self.l_margin, 10)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(0, 51, 102)
        usable_width = self.w - self.l_margin - self.r_margin
        self.cell(usable_width, 8, latin(self.doc_title), align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(0, 51, 102)
        self.line(self.l_margin, 18, self.w - self.r_margin, 18)
        self.set_y(22)
        self.set_x(self.l_margin)

    def footer(self):
        self.set_y(-15)
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        usable_width = self.w - self.l_margin - self.r_margin
        self.cell(
            usable_width,
            10,
            latin(f"{self.subtitle} | Pagina {self.page_no()}"),
            align="C",
        )

    def add_section(self, heading: str, body: str):
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(0, 51, 102)
        self.multi_cell(0, 8, latin(heading))
        self.ln(1)
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 6, latin(body))
        self.ln(5)


def build_pdf(filename: str, title: str, subtitle: str, sections: list[tuple[str, str]]):
    os.makedirs(DATA_DIRECTORY, exist_ok=True)
    pdf = ManualPDF(title=title, subtitle=subtitle)
    pdf.add_page()
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(0, 51, 102)
    pdf.multi_cell(0, 10, latin(title), align="C")
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "I", 11)
    pdf.multi_cell(
        0,
        8,
        latin("IntegraServicios S.A. | Documento de prueba para IntegraBot"),
        align="C",
    )
    pdf.ln(6)

    for heading, body in sections:
        pdf.add_section(heading, body)

    output_path = os.path.join(DATA_DIRECTORY, filename)
    pdf.output(output_path)
    print(f"Creado: {output_path}")


def riohs_sections():
    """Documentos internos: jornada, licencias medicas, EPP y denuncias Ley Karin."""
    return [
        (
            "Articulo 1. Ambito de aplicacion",
            "El presente Reglamento Interno de Orden, Higiene y Seguridad "
            "(RIOHS_IntegraServicios_2026) rige a todas las personas que prestan "
            "servicios a IntegraServicios S.A., en faenas presenciales, hibridas o de "
            "teletrabajo. Su incumplimiento puede dar lugar a medidas disciplinarias "
            "conforme al Articulo 154 del Codigo del Trabajo.",
        ),
        (
            "Articulo 12. Jornadas de trabajo",
            "La jornada ordinaria de IntegraServicios S.A. es de 44 horas semanales, "
            "distribuidas de lunes a viernes, de 08:30 a 18:00 horas, con 45 minutos "
            "de colacion que no se consideran trabajados. Las horas extraordinarias "
            "requieren autorizacion previa de la jefatura directa y se pagan con el "
            "recargo legal del 50 por ciento.",
        ),
        (
            "Articulo 16. Licencias medicas",
            "El colaborador que presente licencia medica debe ingresarla en el portal "
            "de RRHH dentro de 48 horas desde su emision. Durante la vigencia de la "
            "licencia no se pagan bono de colacion ni bono de movilizacion si el "
            "ausentismo supera 15 dias corridos. Esta prohibido concurrir a faena "
            "estando con licencia vigente. El incumplimiento se considera falta grave.",
        ),
        (
            "Articulo 18. Elementos de proteccion personal (EPP)",
            "En faenas de terreno es obligatorio el uso de casco, calzado de seguridad, "
            "chaleco reflectante y lentes de proteccion. El no uso de EPP constituye falta "
            "grave. La empresa entrega los EPP sin costo y el trabajador debe conservarlos "
            "e informar deterioros al prevencionista de riesgos.",
        ),
        (
            "Articulo 22. Acoso laboral, sexual y violencia en el trabajo (Ley Karin)",
            "IntegraServicios S.A. rechaza toda forma de acoso laboral, acoso sexual y "
            "violencia en el trabajo, conforme a la Ley N 21.643 (Ley Karin). Cualquier "
            "denuncia puede presentarse de forma verbal o escrita ante Gestion de Personas "
            "o al correo denuncias@integraservicios.cl. La investigacion no podra exceder "
            "30 dias y se resguardara la confidencialidad de las partes.",
        ),
        (
            "Articulo 25. Procedimiento de denuncia de acoso laboral",
            "Recibida la denuncia, Gestion de Personas designara un investigador imparcial "
            "en un plazo maximo de 3 dias habiles. Se notificara a las partes, se recabaran "
            "medios de prueba y se emitira un informe con medidas de resguardo inmediatas. "
            "Esta prohibido tomar represalias contra quien denuncia de buena fe. El canal "
            "es confidencial y aplica a trabajo presencial, hibrido y remoto.",
        ),
    ]


def contrato_sections():
    """Documento interno: aguinaldo, bono de escolaridad y dias administrativos."""
    return [
        (
            "Clausula 1. Partes y vigencia",
            "El presente Contrato Colectivo 2026 se celebra entre IntegraServicios S.A. "
            "y el Sindicato de Trabajadores N 1. Rige desde el 1 de enero de 2026 hasta "
            "el 31 de diciembre de 2027, y se aplica a todas las personas sindicalizadas "
            "y a quienes se adhieran conforme a la ley.",
        ),
        (
            "Clausula 4. Dias administrativos pagados",
            "Cada colaborador tiene derecho a 3 dias administrativos pagados por ano "
            "calendario, no acumulables ni canjeables en dinero. La solicitud debe "
            "presentarse con al menos 48 horas de anticipacion en el portal de RRHH, "
            "salvo fuerza mayor. No se otorgan durante licencia medica ni aviso de "
            "termino de contrato.",
        ),
        (
            "Clausula 5. Bono de colacion",
            "La empresa pagara un bono de colacion de $85.000 liquidos mensuales a quienes "
            "trabajen jornada completa presencial o hibrida. El bono no es imponible ni "
            "tributable en los terminos de la normativa vigente, se paga junto a la "
            "remuneracion del mes y no se otorga durante feriados legales ni licencias "
            "medicas superiores a 15 dias corridos.",
        ),
        (
            "Clausula 8. Aguinaldo de Fiestas Patrias",
            "Se pagara un aguinaldo de Fiestas Patrias equivalente a $180.000 brutos "
            "en la remuneracion de septiembre. Adicionalmente, se pagara un aguinaldo "
            "de Navidad de $220.000 brutos en la remuneracion de diciembre. Para "
            "percibirlos se requiere al menos 3 meses de antiguedad al momento del pago.",
        ),
        (
            "Clausula 10. Bono de escolaridad",
            "Se otorga un bono de escolaridad de $75.000 por hijo o hija en edad escolar "
            "(pre-kinder a ensenanza media) y de $95.000 por hijo o hija en educacion "
            "superior reconocida por el MINEDUC. El beneficio se paga en marzo contra "
            "certificado de alumno regular. Tope: 3 cargas por colaborador por ano.",
        ),
        (
            "Clausula 12. Capacitacion y becas de estudio",
            "La empresa destinara anualmente un fondo de capacitacion equivalente al "
            "1 por ciento de la planilla bruta. Los colaboradores con 12 meses de "
            "antiguedad pueden postular a una beca de hasta $500.000 por ano para "
            "estudios tecnicos o universitarios relacionados con el cargo.",
        ),
    ]


def codigo_sections():
    """Documentos externos: descanso dominical, finiquitos, horas extra y Ley Karin."""
    return [
        (
            "Articulo 32. Calculo de horas extraordinarias",
            "Las horas extraordinarias se pagan con un recargo del 50 por ciento sobre "
            "el sueldo convenido para la jornada ordinaria. Solo pueden pactarse para "
            "atender necesidades o situaciones temporales de la empresa, con un maximo "
            "de 2 horas extra por dia. El pacto debe constar por escrito. Ejemplo de "
            "calculo: si el valor hora ordinaria es $5.000, la hora extra vale $7.500.",
        ),
        (
            "Articulo 35. Descanso dominical",
            "Los trabajadores gozaran de un dia de descanso a la semana, que se "
            "otorgara preferentemente en domingo. En actividades exceptuadas, el "
            "empleador debe otorgar un dia de descanso compensatorio en la semana "
            "siguiente. El descanso semanal es irrenunciable y no puede compensarse "
            "en dinero mientras subsista el contrato.",
        ),
        (
            "Articulo 163 y 177. Finiquitos",
            "Al termino del contrato el empleador debe pagar las remuneraciones "
            "pendientes, feriado proporcional y, cuando corresponda, indemnizacion "
            "por anos de servicio y sustitutiva de aviso previo. El finiquito debe "
            "otorgarse por escrito y puede ratificarse ante la Inspeccion del Trabajo "
            "o un notario. El trabajador puede reservar derechos en el mismo documento. "
            "Sin finiquito no se entiende cumplida la obligacion de liquidar el contrato.",
        ),
        (
            "Articulo 67. Feriado anual",
            "Los trabajadores con mas de un ano de servicio tendran derecho a un feriado "
            "anual de 15 dias habiles, con remuneracion integra. El feriado no podra "
            "compensarse en dinero, salvo al termino de la relacion laboral, caso en el "
            "cual se incluye en el finiquito.",
        ),
        (
            "Ley N 21.643 (Ley Karin). Prevencion del acoso y la violencia",
            "La Ley Karin modifica el Codigo del Trabajo para reforzar la prevencion, "
            "investigacion y sancion del acoso laboral, acoso sexual y la violencia en "
            "el trabajo. El empleador debe contar con un protocolo de prevencion, "
            "canales de denuncia confidenciales y medidas de resguardo inmediatas para "
            "las personas afectadas.",
        ),
    ]


def main():
    build_pdf(
        "RIOHS_IntegraServicios_2026.pdf",
        "Reglamento Interno de Orden, Higiene y Seguridad 2026",
        "RIOHS IntegraServicios 2026",
        riohs_sections(),
    )
    build_pdf(
        "Contrato_Colectivo_2026.pdf",
        "Contrato Colectivo de Trabajo 2026-2027",
        "Contrato Colectivo 2026 - IntegraServicios S.A.",
        contrato_sections(),
    )
    build_pdf(
        "Codigo_del_Trabajo_Chile.pdf",
        "Extractos del Codigo del Trabajo de Chile y Ley Karin",
        "Codigo del Trabajo Chile - Documento de consulta",
        codigo_sections(),
    )
    print("Documentos de prueba generados en la carpeta data/")


if __name__ == "__main__":
    main()
