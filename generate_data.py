# generate_data.py
"""
Genera PDFs simulados de prueba para IntegraBot.

Crea en ./data tres documentos con texto normativo chileno:
- RIOHS_2026.pdf
- Contrato_Colectivo_2026.pdf
- Codigo_del_Trabajo.pdf
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
    return [
        (
            "Articulo 1. Ambito de aplicacion",
            "El presente Reglamento Interno de Orden, Higiene y Seguridad (RIOHS 2026) "
            "rige a todas las personas que prestan servicios a IntegraServicios S.A., "
            "en faenas presenciales, hibridas o de teletrabajo. Su incumplimiento puede "
            "dar lugar a medidas disciplinarias conforme al Articulo 154 del Codigo del Trabajo.",
        ),
        (
            "Articulo 12. Jornada de trabajo",
            "La jornada ordinaria de IntegraServicios S.A. es de 44 horas semanales, "
            "distribuidas de lunes a viernes, de 08:30 a 18:00 horas, con 45 minutos "
            "de colacion que no se consideran trabajados. Las horas extraordinarias "
            "requieren autorizacion previa del jefatura directa y se pagan con el recargo "
            "legal del 50 por ciento.",
        ),
        (
            "Articulo 14. Permisos administrativos",
            "Cada colaborador tiene derecho a 3 dias de permiso administrativo remunerado "
            "por ano calendario, no acumulables ni canjeables en dinero. La solicitud "
            "debe presentarse con al menos 48 horas de anticipacion en el portal de RRHH, "
            "salvo fuerza mayor. El permiso por fallecimiento de hijo, conyuge o conviviente "
            "civil es de 7 dias corridos, adicional a lo dispuesto en el Codigo del Trabajo.",
        ),
        (
            "Articulo 18. Elementos de proteccion personal",
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
            "Articulo 25. Procedimiento de denuncias internas",
            "Recibida la denuncia, Gestion de Personas designara un investigador imparcial "
            "en un plazo maximo de 3 dias habiles. Se notificara a las partes, se recabaran "
            "medios de prueba y se emitira un informe con medidas de resguardo. Esta "
            "prohibido tomar represalias contra quien denuncia de buena fe.",
        ),
        (
            "Articulo 31. Teletrabajo y desconexion digital",
            "Los colaboradores en modalidad teletrabajo tienen derecho a desconexion de "
            "al menos 12 horas continuas en un periodo de 24 horas. No se exigira respuesta "
            "a correos, chats o llamados fuera de la jornada, salvo emergencias operativas "
            "debidamente calificadas por la gerencia.",
        ),
        (
            "Articulo 40. Uso de sistemas y confidencialidad",
            "Esta prohibido compartir credenciales, extraer bases de datos de clientes o "
            "divulgar informacion comercial de IntegraServicios S.A. El incumplimiento "
            "sera considerado falta gravísima y podra originar termino de contrato por "
            "incumplimiento grave de las obligaciones que impone el contrato.",
        ),
    ]


def contrato_sections():
    return [
        (
            "Clausula 1. Partes y vigencia",
            "El presente Contrato Colectivo 2026 se celebra entre IntegraServicios S.A. "
            "y el Sindicato de Trabajadores N 1. Rige desde el 1 de enero de 2026 hasta "
            "el 31 de diciembre de 2027, y se aplica a todas las personas sindicalizadas "
            "y a quienes se adhieran conforme a la ley.",
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
            "Clausula 6. Movilizacion",
            "Se otorga un bono de movilizacion de $55.000 mensuales para faenas en la "
            "Region Metropolitana. Quienes utilicen vehiculo de la empresa o transporte "
            "corporativo no percibiran este bono. El valor se reajustara en enero de cada "
            "ano segun IPC del ano anterior.",
        ),
        (
            "Clausula 7. Vacaciones y feriado progresivo",
            "Ademas del feriado anual de 15 dias habiles, IntegraServicios S.A. otorga "
            "2 dias adicionales de vacaciones a quienes cumplan 5 anos de antiguedad "
            "continua en la empresa. Las vacaciones deben solicitarse con 30 dias de "
            "anticipacion y no podran fraccionarse en mas de dos periodos, salvo acuerdo "
            "escrito.",
        ),
        (
            "Clausula 8. Aguinaldos",
            "Se pagara un aguinaldo de Fiestas Patrias equivalente a $180.000 brutos "
            "en la remuneracion de septiembre, y un aguinaldo de Navidad de $220.000 "
            "brutos en la remuneracion de diciembre. Para percibirlos se requiere al "
            "menos 3 meses de antiguedad al momento del pago.",
        ),
        (
            "Clausula 12. Capacitacion y becas de estudio",
            "La empresa destinara anualmente un fondo de capacitacion equivalente al "
            "1 por ciento de la planilla bruta. Los colaboradores con 12 meses de "
            "antiguedad pueden postular a una beca de hasta $500.000 por ano para "
            "estudios tecnicos o universitarios relacionados con el cargo. La solicitud "
            "se presenta en marzo de cada ano ante el Comite Bipartito de Capacitacion.",
        ),
        (
            "Clausula 15. Sala cuna y fuero parental",
            "IntegraServicios S.A. cubre sala cuna para hijos menores de 2 anos, mediante "
            "convenio con instituciones certificadas o reembolso de hasta $280.000 "
            "mensuales contra boleta. Este beneficio es compatible con el fuero maternal "
            "y parental establecido en el Codigo del Trabajo.",
        ),
        (
            "Clausula 18. Seguro complementario de salud",
            "Todos los trabajadores con contrato indefinido y al menos 6 meses de "
            "antiguedad quedan cubiertos por un seguro complementario de salud con "
            "tope de reembolso anual de $2.500.000. La prima es financiada en un 80 por "
            "ciento por la empresa y 20 por ciento por el trabajador.",
        ),
    ]


def codigo_sections():
    return [
        (
            "Articulo 22. Jornada ordinaria",
            "La duracion de la jornada ordinaria de trabajo no excedera de 44 horas "
            "semanales (transicion a 40 horas segun Ley N 21.561). El empleador puede "
            "pactar jornadas excepcionales previa autorizacion de la Direccion del Trabajo. "
            "El descanso semanal es, por regla general, el dia domingo.",
        ),
        (
            "Articulo 67. Feriado anual",
            "Los trabajadores con mas de un ano de servicio tendran derecho a un feriado "
            "anual de 15 dias habiles, con remuneracion integra. El feriado se concede "
            "de preferencia en primavera o verano, considerandose las necesidades del "
            "servicio. El feriado no podra compensarse en dinero, salvo al termino de la "
            "relacion laboral.",
        ),
        (
            "Articulo 195. Fuero maternal",
            "La trabajadora tendra derecho a un descanso de maternidad de 6 semanas "
            "antes del parto y 12 semanas despues de el. Este derecho es irrenunciable. "
            "Durante el periodo de embarazo y hasta un ano despues de expirado el "
            "descanso de maternidad, la trabajadora estara cubierta por fuero laboral.",
        ),
        (
            "Articulo 199. Permiso por nacimiento y cuidado",
            "El padre tendra derecho a un permiso pagado de 5 dias en caso de nacimiento "
            "de un hijo, el que podra utilizar a su eleccion desde el momento del parto "
            "y en los 30 dias siguientes. Este permiso tambien se otorga al padre o "
            "madre adoptante, y es adicional al postnatal parental cuando corresponda.",
        ),
        (
            "Articulo 154. Reglamento interno",
            "Las empresas con 10 o mas trabajadores deben elaborar un reglamento interno "
            "de orden, higiene y seguridad. Dicho reglamento debe contener normas de "
            "higiene y seguridad, obligaciones y prohibiciones, y el procedimiento de "
            "reclamaciones. Debe ponerse en conocimiento de los trabajadores y "
            "remitirse a la Direccion del Trabajo.",
        ),
        (
            "Articulo 160. Termino de contrato por causal",
            "El contrato de trabajo termina sin derecho a indemnizacion cuando el "
            "empleador le ponga termino invocando alguna de las causales del Articulo 160, "
            "entre ellas: falta de probidad, acoso sexual, acoso laboral, vias de hecho, "
            "injurias o conducta inmoral, e incumplimiento grave de las obligaciones que "
            "impone el contrato.",
        ),
        (
            "Ley N 21.643 (Ley Karin). Prevencion del acoso y la violencia",
            "La Ley Karin modifica el Codigo del Trabajo para reforzar la prevencion, "
            "investigacion y sancion del acoso laboral, acoso sexual y la violencia en "
            "el trabajo. El empleador debe contar con un protocolo de prevencion, "
            "canales de denuncia confidenciales y medidas de resguardo inmediatas para "
            "las personas afectadas.",
        ),
        (
            "Articulo 184. Deber de proteccion",
            "El empleador estara obligado a tomar todas las medidas necesarias para "
            "proteger eficazmente la vida y salud de los trabajadores, informando de "
            "los posibles riesgos y manteniendo las condiciones adecuadas de higiene y "
            "seguridad. Debe cumplir los protocolos del Ministerio de Salud y de la "
            "Superintendencia de Seguridad Social.",
        ),
    ]


def main():
    build_pdf(
        "RIOHS_2026.pdf",
        "Reglamento Interno de Orden, Higiene y Seguridad 2026",
        "RIOHS 2026 - IntegraServicios S.A.",
        riohs_sections(),
    )
    build_pdf(
        "Contrato_Colectivo_2026.pdf",
        "Contrato Colectivo de Trabajo 2026-2027",
        "Contrato Colectivo 2026 - IntegraServicios S.A.",
        contrato_sections(),
    )
    build_pdf(
        "Codigo_del_Trabajo.pdf",
        "Extractos del Codigo del Trabajo de Chile",
        "Codigo del Trabajo - Documento de consulta",
        codigo_sections(),
    )
    print("Documentos de prueba generados en la carpeta data/")


if __name__ == "__main__":
    main()
