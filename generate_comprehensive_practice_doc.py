"""
Script generador del documento Word (.docx):
Manual Técnico y Guía Práctica Universitaria de Aprendizaje Federado en Salud.
Incluye arquitectura completa, Django, MongoDB Atlas, PyTorch, FedAvg, Railway,
solución de errores reales y guía de laboratorio para estudiantes universitarios.
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def set_cell_background(cell, fill_hex):
    """Aplica color de fondo a una celda de tabla."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    """Ajusta padding interno de una celda en dxa."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_code_block(doc, code_str, language="python"):
    """Inserta un bloque de código estilizado con fondo oscuro/gris y tipografía Consolas."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "0F172A")  # Slate 900
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    
    run = p.add_run(code_str.strip())
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(226, 232, 240)  # Slate 200
    
    # Espaciado posterior a la tabla
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(6)

def add_callout(doc, title, text, callout_type="info"):
    """Crea una caja de aviso destacada (tip, advertencia o nota técnica)."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    
    colors = {
        "info": ("E0F2FE", "0369A1", "💡"),      # Sky
        "warning": ("FEF3C7", "B45309", "⚠️"),   # Amber
        "success": ("DCFCE7", "15803D", "✅"),   # Green
        "error": ("FEE2E2", "B91C1C", "🚨")      # Red
    }
    bg_hex, border_hex, icon = colors.get(callout_type, colors["info"])
    set_cell_background(cell, bg_hex)
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    
    run_icon = p.add_run(f"{icon} {title}\n")
    run_icon.font.name = "Arial"
    run_icon.font.size = Pt(10)
    run_icon.font.bold = True
    
    run_text = p.add_run(text)
    run_text.font.name = "Calibri"
    run_text.font.size = Pt(9.5)
    run_text.font.color.rgb = RGBColor(30, 41, 59)
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(6)

def style_heading(p, text, level=1):
    """Estiliza encabezados con colores y fuentes profesionales."""
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.bold = True
    
    if level == 1:
        p.paragraph_format.space_before = Pt(20)
        p.paragraph_format.space_after = Pt(6)
        run.font.size = Pt(16)
        run.font.color.rgb = RGBColor(15, 23, 42)  # Navy 900
    elif level == 2:
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(2, 132, 199)  # Blue 600
    elif level == 3:
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(2)
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(13, 148, 136) # Teal 600
    return p

def main():
    doc = Document()
    
    # Configuración de márgenes estándar (1 pulgada)
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
    
    # =========================================================================
    # PORTADA UNIVERSITARIA Y FICHA TÉCNICA
    # =========================================================================
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(20)
    p_inst.paragraph_format.space_after = Pt(4)
    run_inst = p_inst.add_run("GUÍA PRÁCTICA UNIVERSITARIA & MANUAL TÉCNICO DE LABORATORIO\nINGENIERÍA DE SOFTWARE & CIENCIAS DE LA COMPUTACIÓN")
    run_inst.font.name = "Arial"
    run_inst.font.size = Pt(11)
    run_inst.font.bold = True
    run_inst.font.color.rgb = RGBColor(100, 116, 139)
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(10)
    run_icon = p_title.add_run("🏥 🧠 🌐\n")
    run_icon.font.size = Pt(30)
    run_t = p_title.add_run("APRENDIZAJE FEDERADO EN SALUD:\nDIAGNÓSTICO DISTRIBUIDO DE DIABETES")
    run_t.font.name = "Arial"
    run_t.font.size = Pt(22)
    run_t.font.bold = True
    run_t.font.color.rgb = RGBColor(15, 23, 42)
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(25)
    run_sub = p_sub.add_run("Implementación Integral con Django, PyTorch (MLP + FedAvg), MongoDB Atlas y Despliegue en Cloud Railway")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(12.5)
    run_sub.font.bold = True
    run_sub.font.color.rgb = RGBColor(2, 132, 199)
    
    # Ficha Técnica
    tbl_meta = doc.add_table(rows=7, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_rows = [
        ("Área de Conocimiento:", "Inteligencia Artificial Distribuida, Privacidad Diferencial y Desarrollo Cloud"),
        ("Arquitectura de IA:", "Perceptrón Multicapa (PyTorch nn.Module) + Federated Averaging (FedAvg)"),
        ("Backend y Orquestación:", "Django 6.1 (Auth personalizada, API REST, Django Templates y Bootstrap/CSS)"),
        ("Base de Datos Documental:", "MongoDB Atlas Cloud (Colecciones: registros_clinicos, modelos_globales, rondas_federadas)"),
        ("Plataforma de Despliegue:", "Railway Cloud Container (Nixpacks, Gunicorn WSGI, Whitenoise, SSL Proxy)"),
        ("Garantía de Privacidad:", "Datos clínicos privados y aislados (Zero Data Sharing); intercambio exclusivo de pesos"),
        ("Audiencia Objetivo:", "Estudiantes Universitarios de Ingeniería de Sistemas, Software y Ciencia de Datos")
    ]
    for idx, (label, val) in enumerate(meta_rows):
        c0 = tbl_meta.cell(idx, 0)
        c1 = tbl_meta.cell(idx, 1)
        set_cell_background(c0, "F1F5F9")
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, top=80, bottom=80, left=120, right=120)
        set_cell_margins(c1, top=80, bottom=80, left=120, right=120)
        c0.paragraphs[0].text = label
        c0.paragraphs[0].runs[0].font.name = "Arial"
        c0.paragraphs[0].runs[0].font.size = Pt(9)
        c0.paragraphs[0].runs[0].font.bold = True
        c1.paragraphs[0].text = val
        c1.paragraphs[0].runs[0].font.name = "Calibri"
        c1.paragraphs[0].runs[0].font.size = Pt(9.5)
    
    doc.add_page_break()
    
    # =========================================================================
    # SECCIÓN 1: FUNDAMENTOS TEÓRICOS DEL APRENDIZAJE FEDERADO
    # =========================================================================
    style_heading(doc.add_paragraph(), "1. Fundamentos Teóricos del Aprendizaje Federado (Federated Learning)", 1)
    
    p = doc.add_paragraph()
    p.add_run(
        "El Aprendizaje Federado (FL, por sus siglas en inglés) es un paradigma contemporáneo de Machine Learning propuesto "
        "originalmente por investigadores de Google en 2016 (McMahan et al.). A diferencia del enfoque convencional centralizado, "
        "donde todos los datos de entrenamiento deben transferirse físicamente a un servidor o clúster común, el Aprendizaje "
        "Federado entrena modelos de manera descentralizada directamente en los dispositivos de borde o nodos participantes (en este "
        "caso, entidades hospitalarias)."
    )
    
    style_heading(doc.add_paragraph(), "1.1 El Desafío de la Privacidad en el Sector Sanitario", 2)
    p = doc.add_paragraph()
    p.add_run(
        "En la medicina contemporánea, los historiales clínicos electrónicos (EHR) son los activos más confidenciales de una institución. "
        "Marcos normativos internacionales rigurosos como HIPAA (Health Insurance Portability and Accountability Act en EE.UU.) y "
        "GDPR (Reglamento General de Protección de Datos en Europa), así como las leyes nacionales de protección de datos personales, "
        "prohíben terminantemente la transferencia masiva o no autorizada de datos de pacientes entre hospitales.\n\n"
        "Esta restricción crea los denominados 'Silos de Datos' (Data Silos): cada hospital cuenta con un número limitado de pacientes "
        "con diabetes u otras patologías, lo que resulta en modelos de Machine Learning locales con bajo poder predictivo, "
        "sesgados por la demografía particular de ese centro. El Aprendizaje Federado resuelve este dilema al permitir que múltiples "
        "hospitales colaboren para entrenar un modelo global de alta precisión diagnóstica sin que un solo byte de datos de pacientes "
        "abandone el perímetro de seguridad de cada centro."
    )
    
    style_heading(doc.add_paragraph(), "1.2 Formulación Matemática del Algoritmo Federated Averaging (FedAvg)", 2)
    p = doc.add_paragraph()
    p.add_run(
        "El núcleo algorítmico del aprendizaje federado sincrónico es FedAvg. Consideremos un conjunto de K hospitales "
        "(en nuestra práctica, HospitalA, HospitalB y HospitalC), donde cada hospital k custodia un conjunto de datos privado D_k con n_k muestras. "
        "El número total de muestras en la federación es N = Σ n_k.\n\n"
        "El protocolo opera en rondas iterativas t = 1, 2, ...:\n"
        "1. Difusión Global: El Servidor Central transmite los pesos globales actuales W_t a los hospitales participantes.\n"
        "2. Entrenamiento Local Privado: Cada hospital inicializa su modelo local con W_t y optimiza su función de pérdida "
        "mediante Descenso de Gradiente Estocástico (SGD / Adam) a lo largo de E épocas sobre sus datos privados D_k, "
        "obteniendo un nuevo vector de pesos locales W_{t+1}^k.\n"
        "3. Transmisión Segura de Parámetros: Cada hospital transmite únicamente el delta o tensor de pesos W_{t+1}^k al servidor central.\n"
        "4. Agregación Ponderada: El servidor central computa el nuevo modelo global W_{t+1} mediante el promedio ponderado "
        "según el volumen de registros de cada hospital:"
    )
    
    add_code_block(doc, "W_{t+1} = \\sum_{k=1}^{K} \\frac{n_k}{N} W_{t+1}^k\n\nDonde:\n  - K = 3 (HospitalA, HospitalB, HospitalC)\n  - n_k = número de historias clínicas privadas del hospital k\n  - N = número total de historias clínicas en la federación\n  - W_{t+1}^k = tensor de pesos sinápticos entrenados por el hospital k", "text")
    
    add_callout(doc, "Principio de Cero Fuga de Datos (Zero Data Leakage)", 
                "El servidor central JAMÁS tiene acceso a los registros médicos de los pacientes (edad, glucosa, IMC, presión arterial). "
                "Únicamente manipula matrices numéricas de punto flotante que representan parámetros sinápticos. "
                "Esto asegura cumplimiento estricto con estándares éticos y legales hospitalarios.", "success")
    
    # =========================================================================
    # SECCIÓN 2: ARQUITECTURA DEL SISTEMA Y DIAGRAMA DE CLASES UML
    # =========================================================================
    style_heading(doc.add_paragraph(), "2. Arquitectura General del Sistema y Diagrama de Clases UML", 1)
    
    p = doc.add_paragraph()
    p.add_run(
        "El sistema implementa una arquitectura híbrida desacoplada que combina una base relacional para la gestión de acceso médico "
        "(Django ORM) con una base de datos documental de alto rendimiento para modelos neuronales (MongoDB), "
        "y un motor de Deep Learning con aceleración vectorial (PyTorch)."
    )
    
    # Incrustar Diagrama UML
    uml_path = r"c:\Users\Dell Latitude i7 8th\Documents\hospital\diagrama_uml.png"
    if os.path.exists(uml_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(uml_path, width=Inches(6.2))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(14)
        run_cap = p_cap.add_run("Figura 1: Diagrama de Clases UML de la Arquitectura de Aprendizaje Federado.")
        run_cap.font.name = "Arial"
        run_cap.font.size = Pt(8.5)
        run_cap.font.italic = True
        run_cap.font.color.rgb = RGBColor(100, 116, 139)
    
    style_heading(doc.add_paragraph(), "2.1 Componentes Principales de la Topología", 2)
    tbl_top = doc.add_table(rows=5, cols=3)
    tbl_top.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Componente", "Tecnología / Capa", "Responsabilidad en la Federación"]
    for j, h in enumerate(headers):
        cell = tbl_top.cell(0, j)
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        p = cell.paragraphs[0]
        p.text = h
        p.runs[0].font.name = "Arial"
        p.runs[0].font.size = Pt(9)
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
    
    rows_top = [
        ("Servidor Central (ServerFederado)", "Django 6.1 + Gunicorn + MongoDB", "Coordina rondas, valida API Keys, recibe pesos de hospitales, computa FedAvg y publica el modelo global vigente."),
        ("Nodos Clientes (HospitalA, B, C)", "PyTorch + Requests + SQLite", "Custodian registros clínicos privados. Descargan modelo global, entrenan localmente y envían pesos resultantes."),
        ("Portal Web Médico", "Django Views + Templates + Chart.js", "Permite a los facultativos autenticarse, monitorear convergencia de precisión y evaluar pacientes en tiempo real."),
        ("Repositorio Documental", "MongoDB Atlas (Cloud)", "Persiste colecciones BSON de pesos serializados, metadatos de rondas federadas y registros clínicos sintéticos.")
    ]
    for i, row in enumerate(rows_top):
        for j, val in enumerate(row):
            cell = tbl_top.cell(i+1, j)
            bg = "F8FAFC" if i % 2 == 0 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            p = cell.paragraphs[0]
            p.text = val
            p.runs[0].font.name = "Calibri"
            p.runs[0].font.size = Pt(9)
    
    doc.add_page_break()

    # =========================================================================
    # SECCIÓN 3: BASE DE DATOS NOSQL CON MONGODB ATLAS
    # =========================================================================
    style_heading(doc.add_paragraph(), "3. Base de Datos NoSQL con MongoDB Atlas: Modelado y Resiliencia", 1)
    
    p = doc.add_paragraph()
    p.add_run(
        "A diferencia de las bases de datos relacionales tradicionales como PostgreSQL o MySQL (diseñadas para filas rígidas de "
        "tamaño fijo), los modelos de Deep Learning consisten en matrices numéricas multidimensionales (tensores de pesos y sesgos). "
        "MongoDB almacena información en documentos BSON (Binary JSON), lo que permite persistir diccionarios complejos de capas "
        "neuronales ('fc1.weight', 'fc1.bias') como documentos anidados sin necesidad de costosas conversiones de esquema."
    )
    
    style_heading(doc.add_paragraph(), "3.1 Colecciones Principales en la Base de Datos 'salud_federada'", 2)
    p = doc.add_paragraph()
    p.add_run(
        "En el archivo federated_app/mongo_db.py se gestionan tres colecciones documentales esenciales:\n"
        "1. registros_clinicos: Almacena las historias médicas segregadas por hospital_codigo (HospitalA, HospitalB, HospitalC). "
        "Cada registro contiene: edad, imc, glucosa, presion, diagnostico (1: positivo, 0: negativo) y fecha_registro.\n"
        "2. modelos_globales: Registra cada versión del modelo resultante de FedAvg. Contiene version (ej: v1.0.0-base, v2.0-fedavg), "
        "ronda_numero, total_parametros, metricas (accuracy, loss), hospitales_contribuyentes y el diccionario de pesos serializados.\n"
        "3. rondas_federadas: Coordina el ciclo de vida de cada ronda. Guarda ronda_numero, estado ('recibiendo' o 'completada'), "
        "hospitales_esperados, actualizaciones recibidas y fecha de cierre."
    )
    
    style_heading(doc.add_paragraph(), "3.2 Conexión Robusta y Sanitizador de URI en mongo_db.py", 2)
    p = doc.add_paragraph()
    p.add_run(
        "Durante el despliegue en la nube, es muy frecuente que los estudiantes cometan errores al configurar la variable MONGO_URI en Railway, "
        "tales como copiar las comillas de la cadena, dejar los corchetes angulares <password> del asistente de Atlas, o usar contraseñas con "
        "caracteres especiales no codificados. Para resolver esto de forma profesional y transparente, implementamos un algoritmo sanitizador:"
    )
    
    add_code_block(doc, """def sanitize_mongo_uri(uri: str) -> str:
    \"\"\"
    Limpia y corrige errores comunes de formato en cadenas de conexión de MongoDB / Atlas:
      1. Elimina comillas externas accidentales (' o \") y espacios en blanco.
      2. Remueve corchetes angulares accidentales < > dejados de la plantilla de Atlas.
      3. Sustituye automáticamente placeholders como <usuario> o <password> por credenciales válidas.
      4. Inserta las credenciales 'admin_hospital:12345678Rosario' si la URI no las contiene.
      5. Codifica caracteres especiales en usuario y contraseña usando quote_plus.
    \"\"\"
    default_user = getattr(settings, 'MONGO_USER', 'admin_hospital') or 'admin_hospital'
    default_pwd = getattr(settings, 'MONGO_PASSWORD', '12345678Rosario') or '12345678Rosario'

    if not uri or not isinstance(uri, str) or not uri.strip():
        return f"mongodb://localhost:27017/"

    uri = uri.strip().strip('"\\'')
    prefix, rest = uri.split('://', 1)

    if '@' not in rest:
        # Inyecta credenciales configuradas si faltaban en la URI
        user_clean = urllib.parse.quote_plus(default_user)
        pwd_clean = urllib.parse.quote_plus(default_pwd)
        return f"{prefix}://{user_clean}:{pwd_clean}@{rest}"

    auth_part, host_part = rest.rsplit('@', 1)
    if ':' in auth_part:
        user, pwd = auth_part.split(':', 1)
        if user.startswith('<') and user.endswith('>'):
            user = user[1:-1]
        if pwd.startswith('<') and pwd.endswith('>'):
            pwd = pwd[1:-1]
        if user.lower() in ('<usuario>', '<username>', 'usuario'):
            user = default_user
        if pwd.lower() in ('<password>', 'password', '<contraseña>'):
            pwd = default_pwd
        user_clean = urllib.parse.quote_plus(urllib.parse.unquote_plus(user))
        pwd_clean = urllib.parse.quote_plus(urllib.parse.unquote_plus(pwd))
        return f"{prefix}://{user_clean}:{pwd_clean}@{host_part}"
    return uri""")
    
    style_heading(doc.add_paragraph(), "3.3 Solución al Error 8000: 'bad auth : authentication failed'", 2)
    add_callout(doc, "Diagnóstico del Error AtlasError 8000",
                "Cuando en los logs de Railway aparece: 'bad auth : authentication failed, code: 8000, codeName: AtlasError', "
                "significa que el clúster de MongoDB Atlas rechazó las credenciales. Las soluciones definitivas son:\n"
                "1. En MongoDB Atlas -> Security -> Database Access: crear el usuario 'admin_hospital' con contraseña '12345678Rosario' "
                "y asignarle el rol 'Read and write to any database'.\n"
                "2. En Security -> Network Access: añadir la regla IP '0.0.0.0/0' (Allow access from anywhere) para que Railway se conecte.\n"
                "3. En Railway Variables: declarar MONGO_URI, MONGO_USER y MONGO_PASSWORD sin comillas ni corchetes angulares.", "warning")

    # =========================================================================
    # SECCIÓN 4: DESARROLLO BACKEND CON DJANGO
    # =========================================================================
    style_heading(doc.add_paragraph(), "4. Desarrollo Backend con Django: Modelos, Vistas y Seguridad", 1)
    
    p = doc.add_paragraph()
    p.add_run(
        "Django actúa como el orquestador central del sistema. Provee la capa de autenticación médica para facultativos, "
        "valida las peticiones de los hospitales mediante claves de API únicas y expone el Dashboard interactivo con Chart.js."
    )
    
    style_heading(doc.add_paragraph(), "4.1 Modelo Personalizado de Médico y Hospitales en models.py", 2)
    p = doc.add_paragraph()
    p.add_run(
        "Para representar a los médicos facultativos en el sistema, extendemos AbstractUser de Django. Esto permite "
        "aprovechar todo el sistema de sesiones seguras y hashing de contraseñas de Django, añadiendo atributos clínicos "
        "especializados como cédula profesional, especialidad médica y hospital de afiliación:"
    )
    
    add_code_block(doc, """# federated_app/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class Hospital(models.Model):
    codigo = models.CharField(max_length=50, unique=True)  # Ej: HospitalA, HospitalB
    nombre = models.CharField(max_length=200)
    api_key = models.CharField(max_length=128, unique=True) # Clave secreta para REST API
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class Medico(AbstractUser):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, null=True, blank=True)
    cedula = models.CharField(max_length=50, blank=True)
    especialidad = models.CharField(max_length=100, default="Medicina General")

    def __str__(self):
        return f"Dr(a). {self.get_full_name()} ({self.hospital.codigo if self.hospital else 'Central'})\"""")

    style_heading(doc.add_paragraph(), "4.2 Decorador de Seguridad para Hospitales por API Key", 2)
    p = doc.add_paragraph()
    p.add_run(
        "Los hospitales clientes se comunican con el servidor mediante peticiones HTTP automatizadas. Para asegurar que "
        "solamente los hospitales autorizados puedan descargar o enviar pesos sinápticos, se diseñó el decorador validar_hospital_api_key:"
    )
    
    add_code_block(doc, """def validar_hospital_api_key(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        api_key = request.headers.get('X-API-KEY') or request.GET.get('api_key')
        if not api_key:
            return JsonResponse({"error": "Autenticación requerida. Falta cabecera 'X-API-KEY'"}, status=401)
        try:
            hospital = Hospital.objects.get(api_key=api_key, activo=True)
            request.hospital = hospital
        except Hospital.DoesNotExist:
            return JsonResponse({"error": "Acceso denegado. API Key inválida o revocada"}, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped""")

    doc.add_page_break()

    # =========================================================================
    # SECCIÓN 5: LA RED NEURONAL CON PYTORCH
    # =========================================================================
    style_heading(doc.add_paragraph(), "5. La Red Neuronal con PyTorch: Arquitectura, Normalización y FedAvg", 1)
    
    p = doc.add_paragraph()
    p.add_run(
        "El motor de Inteligencia Artificial se construyó con PyTorch (torch.nn), la biblioteca líder en investigación "
        "de Deep Learning debido a su grafo computacional dinámico y su flexibilidad para manipular tensores a nivel de capa."
    )
    
    # Incrustar Diagrama de la Red Neuronal
    nn_img_path = r"c:\Users\Dell Latitude i7 8th\Documents\hospital\diagrama_red_neuronal.png"
    if os.path.exists(nn_img_path):
        p_img2 = doc.add_paragraph()
        p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img2.paragraph_format.space_before = Pt(8)
        p_img2.paragraph_format.space_after = Pt(4)
        run_img2 = p_img2.add_run()
        run_img2.add_picture(nn_img_path, width=Inches(6.2))
        
        p_cap2 = doc.add_paragraph()
        p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap2.paragraph_format.space_after = Pt(14)
        run_cap2 = p_cap2.add_run("Figura 2: Arquitectura del Perceptrón Multicapa (MLP) para Diagnóstico Clínico de Diabetes.")
        run_cap2.font.name = "Arial"
        run_cap2.font.size = Pt(8.5)
        run_cap2.font.italic = True
        run_cap2.font.color.rgb = RGBColor(100, 116, 139)
    
    style_heading(doc.add_paragraph(), "5.1 Definición de la Red Neuronal ModeloDiagnosticoNN", 2)
    p = doc.add_paragraph()
    p.add_run(
        "La red neuronal clasifica a un paciente como diabético (1) o no diabético (0) basándose en 4 variables fisiológicas:\n"
        "• x1: Edad del paciente (años)\n"
        "• x2: Índice de Masa Corporal - IMC (kg/m²)\n"
        "• x3: Glucosa plasmática en ayunas (mg/dL)\n"
        "• x4: Presión arterial sistólica (mmHg)\n\n"
        "Su topología consta de 3 capas densas (Fully Connected / Linear) con activaciones no lineales ReLU y salida Sigmoide:"
    )
    
    add_code_block(doc, """import torch
import torch.nn as nn

class ModeloDiagnosticoNN(nn.Module):
    def __init__(self):
        super(ModeloDiagnosticoNN, self).__init__()
        # Capa 1: Entrada 4 características -> 32 neuronas ocultas
        self.fc1 = nn.Linear(4, 32)
        self.relu1 = nn.ReLU()
        # Capa 2: 32 neuronas -> 32 neuronas
        self.fc2 = nn.Linear(32, 32)
        self.relu2 = nn.ReLU()
        # Capa 3: 32 neuronas -> 1 salida (probabilidad 0 a 1)
        self.fc3 = nn.Linear(32, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # x tiene dimensión [batch_size, 4]
        out = self.relu1(self.fc1(x))
        out = self.relu2(self.fc2(out))
        out = self.sigmoid(self.fc3(out))
        return out""")
    
    style_heading(doc.add_paragraph(), "5.2 Estandarización Clínica Z-Score", 2)
    p = doc.add_paragraph()
    p.add_run(
        "Las variables de entrada poseen magnitudes y escalas drásticamente dispares (por ejemplo, glucosa entre 70 y 200 mg/dL, "
        "mientras que el IMC oscila entre 18 y 40). Sin normalización, los gradientes de la glucosa dominarían completamente la "
        "actualización de pesos, causando inestabilidad numérica. Aplicamos estandarización fija Z-Score:"
    )
    add_code_block(doc, """MEDIAS = torch.tensor([48.0, 28.5, 125.0, 125.0], dtype=torch.float32)
DESVIACIONES = torch.tensor([15.0, 6.0, 35.0, 18.0], dtype=torch.float32)

def normalizar_features(tensor_x):
    # z = (x - mu) / sigma
    return (tensor_x - MEDIAS) / (DESVIACIONES + 1e-7)""")

    style_heading(doc.add_paragraph(), "5.3 Implementación del Algoritmo FedAvg en Python", 2)
    p = doc.add_paragraph()
    p.add_run(
        "La función fed_avg recibe la lista de actualizaciones recibidas de los hospitales en la ronda vigente. "
        "Cada actualización contiene el diccionario de pesos serializados y el número de muestras locales num_muestras. "
        "El código realiza el promedio ponderado exacto para cada parámetro de la red:"
    )
    
    add_code_block(doc, """def fed_avg(actualizaciones):
    total_muestras = sum(upd["num_muestras"] for upd in actualizaciones)
    pesos_agregados = {}
    primeros_pesos = actualizaciones[0]["pesos"]

    for key in primeros_pesos.keys():
        tensor_promedio = None
        for upd in actualizaciones:
            ponderador = upd["num_muestras"] / total_muestras
            tensor_hosp = torch.tensor(upd["pesos"][key], dtype=torch.float32)
            if tensor_promedio is None:
                tensor_promedio = tensor_hosp * ponderador
            else:
                tensor_promedio += tensor_hosp * ponderador
        pesos_agregados[key] = tensor_promedio.detach().cpu().numpy().tolist()

    return pesos_agregados""")

    doc.add_page_break()

    # =========================================================================
    # SECCIÓN 6: DESPLIEGUE EN LA NUBE CON RAILWAY
    # =========================================================================
    style_heading(doc.add_paragraph(), "6. Despliegue en la Nube con Railway: Configuración y Solución de Errores", 1)
    
    p = doc.add_paragraph()
    p.add_run(
        "Railway es una plataforma moderna de infraestructura en la nube (PaaS). Utiliza Nixpacks para detectar "
        "automáticamente proyectos Python, instalar dependencias, compilar archivos estáticos y ejecutar el servidor WSGI."
    )
    
    style_heading(doc.add_paragraph(), "6.1 Archivo de Orquestación railway.json y Procfile", 2)
    p = doc.add_paragraph()
    p.add_run(
        "Para automatizar el arranque, migraciones y recolección de estáticos en cada commit, se configuró railway.json:"
    )
    add_code_block(doc, """{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python manage.py migrate --noinput && python manage.py collectstatic --noinput && python init_system.py && gunicorn federated_project.wsgi:application --bind 0.0.0.0:$PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}""", "json")

    style_heading(doc.add_paragraph(), "6.2 Solución al Error 403: 'La verificación CSRF ha fallado' en Railway", 2)
    p = doc.add_paragraph()
    p.add_run(
        "Un problema clásico al desplegar Django en Railway ocurre cuando el usuario intenta iniciar sesión y recibe:\n"
        "'Prohibido (403): La verificación CSRF ha fallado. Solicitud abortada.'\n\n"
        "Causa Raíz: Railway termina la conexión segura SSL/HTTPS en sus balanceadores de carga Cloudflare/Envoy y luego "
        "reenvía la petición a Gunicorn en HTTP plano por el puerto $PORT. Como Django no sabe que la petición original "
        "era HTTPS, rechaza el formulario por seguridad. La solución obligatoria en settings.py es:"
    )
    add_code_block(doc, """# Soporte para Proxy Inverso SSL en Railway
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Orígenes confiables autorizados para CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
    'https://*.up.railway.app',
    'https://web-production-28da9.up.railway.app',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]""")

    # =========================================================================
    # SECCIÓN 7: GUÍA DE PRÁCTICA UNIVERSITARIA PASO A PASO
    # =========================================================================
    style_heading(doc.add_paragraph(), "7. Guía de Práctica Universitaria Paso a Paso (Laboratorio)", 1)
    
    p = doc.add_paragraph()
    p.add_run(
        "A continuación se detallan las instrucciones para que los estudiantes ejecuten la práctica en sus estaciones de trabajo:"
    )
    
    pasos = [
        ("Paso 1: Clonar el Repositorio", "git clone https://github.com/adriandoct/hospital.git\ncd hospital"),
        ("Paso 2: Crear y Activar Entorno Virtual", "python -m venv venv\n# En Windows:\n.\\venv\\Scripts\\activate\n# En Linux/Mac:\nsource venv/bin/activate"),
        ("Paso 3: Instalar Dependencias", "pip install -r requirements.txt"),
        ("Paso 4: Configurar Variables de Entorno", "Crear un archivo .env en la raíz con:\nMONGO_USER=admin_hospital\nMONGO_PASSWORD=12345678Rosario\nMONGO_DB_NAME=salud_federada"),
        ("Paso 5: Inicializar Base de Datos y Semilla", "python init_system.py\n(Aplica migraciones, registra los 3 hospitales y crea los 3 médicos facultativos)"),
        ("Paso 6: Iniciar el Servidor Central", "python manage.py runserver 8000"),
        ("Paso 7: Ejecutar Clientes Hospitalarios en Paralelo", "Abrir terminales independientes y ejecutar:\n# Terminal 1:\npython client_hospital.py --hospital HospitalA\n# Terminal 2:\npython client_hospital.py --hospital HospitalB\n# Terminal 3:\npython client_hospital.py --hospital HospitalC"),
        ("Paso 8: Monitorear en el Dashboard Web", "Navegar a http://127.0.0.1:8000/login/ e ingresar con:\nUsuario: dr_garcia | Contraseña: medico123\nVerificar la evolución de Accuracy y Loss en la gráfica Chart.js."),
        ("Paso 9: Evaluar Diagnóstico de Pacientes", "En la sección de Inferencia Clínica, ingresar:\nEdad: 54, IMC: 31.5, Glucosa: 155, Presión: 140\nVerificar el cálculo instantáneo de probabilidad de diabetes emitido por el modelo global agregado.")
    ]
    
    for titulo, cmd in pasos:
        style_heading(doc.add_paragraph(), titulo, 2)
        add_code_block(doc, cmd, "bash")
        
    style_heading(doc.add_paragraph(), "7.1 Cuestionario de Evaluación para el Alumno", 2)
    preguntas = [
        "1. ¿Por qué el algoritmo FedAvg pondera las actualizaciones según el número de muestras (n_k / N)? ¿Qué sucedería si se usara un promedio simple?",
        "2. Explica qué sucedería con el gradiente de la red neuronal si no se aplicara la normalización Z-Score a la glucosa y al IMC.",
        "3. ¿Qué mecanismo criptográfico o de arquitectura garantiza que el servidor central no pueda reconstruir los datos originales de los pacientes a partir de los pesos?",
        "4. En el archivo mongo_db.py, ¿por qué es necesario reemplazar los puntos '.' de las claves de capas PyTorch por '__dot__' antes de guardarlos en MongoDB?",
        "5. Explica el rol de SECURE_PROXY_SSL_HEADER en el despliegue con balanceadores de carga en la nube como Railway."
    ]
    for preg in preguntas:
        p_q = doc.add_paragraph()
        p_q.paragraph_format.left_indent = Inches(0.25)
        p_q.paragraph_format.space_before = Pt(3)
        p_q.paragraph_format.space_after = Pt(3)
        run_q = p_q.add_run(preg)
        run_q.font.name = "Calibri"
        run_q.font.size = Pt(10)
        run_q.font.italic = True
        run_q.font.color.rgb = RGBColor(15, 23, 42)

    # Guardar documento
    output_filename = "Manual_Practica_Aprendizaje_Federado_Salud.docx"
    doc.save(output_filename)
    print(f"✅ Documento generado exitosamente: {os.path.abspath(output_filename)}")

if __name__ == "__main__":
    main()
