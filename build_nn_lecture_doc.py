"""
Script para generar el documento oficial en formato Microsoft Word (.docx)
con la guía pedagógica universitaria paso a paso del funcionamiento de la red neuronal.
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_lecture_document():
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    c_primary = RGBColor(15, 23, 42)
    c_blue = RGBColor(2, 132, 199)
    c_teal = RGBColor(13, 148, 136)
    c_purple = RGBColor(126, 34, 206)
    c_amber = RGBColor(217, 119, 6)
    c_gray = RGBColor(100, 116, 139)

    # PORTADA
    p_top = doc.add_paragraph()
    p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_top.paragraph_format.space_before = Pt(25)
    p_top.paragraph_format.space_after = Pt(10)
    
    r_icon = p_top.add_run("🧠 🩺\n")
    r_icon.font.size = Pt(34)

    r_title = p_top.add_run("GUÍA DIDÁCTICA UNIVERSITARIA:\nFUNCIONAMIENTO PASO A PASO DE LA RED NEURONAL\n")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = c_primary

    r_sub = p_top.add_run("Diagnóstico Clínico de Diabetes Mediante Perceptrón Multicapa (MLP) y Aprendizaje Federado\n")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(13)
    r_sub.font.bold = True
    r_sub.font.color.rgb = c_blue

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_after = Pt(25)
    r_meta = p_meta.add_run(
        "Material de Cátedra para Estudiantes de Ingeniería, Ciencias de la Computación, Datos y Medicina\n"
        "Explicación Intuitiva, Fundamentación Matemática, Arquitectura PyTorch y Algoritmo FedAvg"
    )
    r_meta.font.size = Pt(10.5)
    r_meta.font.italic = True
    r_meta.font.color.rgb = c_gray

    # Ficha técnica
    meta_table = doc.add_table(rows=5, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    ficha = [
        ("Tipo de Modelo:", "Red Neuronal Perceptrón Multicapa (MLP / Feedforward Neural Network)"),
        ("Variables de Entrada:", "4 Biomarcadores (Edad, IMC, Glucosa en plasma, Presión sistólica)"),
        ("Topología de Capas:", "Linear(4, 32) → ReLU → Linear(32, 32) → ReLU → Linear(32, 1) → Sigmoid"),
        ("Función de Pérdida & Optimizador:", "Binary Cross-Entropy (BCELoss) + Optimizador Adam (lr=0.01)"),
        ("Paradigma de Entrenamiento:", "Aprendizaje Federado (FedAvg - Federated Averaging de McMahan et al.)")
    ]
    for i, (k, v) in enumerate(ficha):
        c0 = meta_table.cell(i, 0)
        c1 = meta_table.cell(i, 1)
        c0.paragraphs[0].text = k
        c0.paragraphs[0].runs[0].font.bold = True
        c0.paragraphs[0].runs[0].font.size = Pt(9.5)
        c1.paragraphs[0].text = v
        c1.paragraphs[0].runs[0].font.size = Pt(9.5)
        set_cell_background(c0, "F1F5F9")
        set_cell_background(c1, "F8FAFC")
        set_cell_margins(c0, 70, 70, 100, 100)
        set_cell_margins(c1, 70, 70, 100, 100)

    doc.add_page_break()

    # 1. INTRODUCCIÓN Y ANALOGÍA CLÍNICA
    h1 = doc.add_heading("1. Introducción y la Analogía Clínica: ¿Por qué una Red Neuronal?", level=1)
    
    p = doc.add_paragraph()
    p.add_run(
        "Al enseñar este tema en el aula universitaria, la primera pregunta que suele surgir entre los estudiantes es: "
        "¿Por qué necesitamos una red neuronal profunda si un médico podría simplemente escribir reglas como:\n"
    )
    
    # Bloque de código simple
    tbl_code = doc.add_table(rows=1, cols=1)
    tbl_code.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_code = tbl_code.cell(0, 0)
    set_cell_background(c_code, "0F172A")
    set_cell_margins(c_code, 80, 80, 120, 120)
    p_code = c_code.paragraphs[0]
    p_code.text = "if glucosa > 140 or imc > 35:\n    diagnostico = 'Positivo para Diabetes'\nelse:\n    diagnostico = 'Bajo Riesgo'"
    p_code.runs[0].font.name = "Consolas"
    p_code.runs[0].font.size = Pt(9.5)
    p_code.runs[0].font.color.rgb = RGBColor(56, 189, 248)

    p2 = doc.add_paragraph()
    p2.paragraph_format.space_before = Pt(8)
    p2.add_run(
        "La respuesta radica en la "
    )
    r_nl = p2.add_run("no linealidad biológica")
    r_nl.font.bold = True
    p2.add_run(
        ": El cuerpo humano no es un interruptor binario. Un paciente joven de 22 años con glucosa de 135 mg/dL "
        "debido a la ingesta reciente de carbohidratos no comparte el mismo riesgo que un adulto de 68 años con hipertensión "
        "y sobrepeso leve que presenta esa misma cifra. Existen sinergias, umbrales cruzados y correlaciones sutiles "
        "que ningún árbol condicional simple puede capturar con precisión. La red neuronal aprende estas relaciones "
        "ocultas directamente a partir de la experiencia clínica."
    )

    # 2. EL VECTOR DE ENTRADA Y NORMALIZACIÓN Z-SCORE
    doc.add_heading("2. Paso 0: El Vector de Biomarcadores y la Estandarización Z-Score", level=1)
    p3 = doc.add_paragraph()
    p3.add_run(
        "La red neuronal recibe como entrada un vector cuatridimensional con 4 biomarcadores de cada paciente:\n"
        "• x₁ = Edad (en años)\n"
        "• x₂ = IMC (Índice de Masa Corporal en kg/m²)\n"
        "• x₃ = Glucosa (nivel en plasma en ayunas, mg/dL)\n"
        "• x₄ = Presión Arterial Sistólica (mm Hg)\n\n"
        "Ejemplo clínico de un paciente real (Don Juan): "
    )
    r_ex = p3.add_run("X = [55.0, 31.4, 142.0, 138.0]")
    r_ex.font.bold = True
    r_ex.font.color.rgb = c_blue

    doc.add_heading("El peligro de las escalas dispares:", level=2)
    p4 = doc.add_paragraph()
    p4.add_run(
        "Pregunta para la clase: ¿Qué ocurre si alimentamos a la red directamente con esos valores crudos?\n"
        "Respuesta: Ocurre una catástrofe de gradientes. La glucosa (142.0) y la presión (138.0) son órdenes de magnitud "
        "mayores que el IMC (31.4). Durante las multiplicaciones de matrices, las variables grandes dominarán artificialmente "
        "a las variables pequeñas, no porque sean médicamente más relevantes, sino por un mero artefacto de unidades de medida."
    )

    doc.add_heading("La solución matemática (Normalización Z-Score):", level=2)
    p5 = doc.add_paragraph()
    p5.add_run(
        "En el archivo 'neural_network.py' se aplica la fórmula estándar de estandarización:\n"
    )
    
    # Caja fórmula
    tbl_f = doc.add_table(rows=1, cols=1)
    tbl_f.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_f = tbl_f.cell(0, 0)
    set_cell_background(c_f, "F1F5F9")
    set_cell_margins(c_f, 90, 90, 120, 120)
    pf = c_f.paragraphs[0]
    pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rf = pf.add_run("X_norm = (X - μ) / σ")
    rf.font.name = "Arial"
    rf.font.size = Pt(13)
    rf.font.bold = True
    rf.font.color.rgb = c_primary

    p6 = doc.add_paragraph()
    p6.paragraph_format.space_before = Pt(6)
    p6.add_run(
        "Donde μ representa las medias de referencia clínica [48.0, 28.5, 125.0, 125.0] y σ las desviaciones estándar "
        "[15.0, 6.0, 35.0, 18.0]. De este modo, todas las entradas se centran en torno a 0.0 con dispersión 1.0. "
        "Un valor de +1.5 significa que el paciente está 1.5 desviaciones por encima del promedio de la población."
    )

    # 3. ANATOMÍA Y DIAGRAMA DE LA RED
    doc.add_page_break()
    h3_title = doc.add_heading("3. Anatomía de la Red: Perceptrón Multicapa (MLP)", level=1)
    
    img_path = r"c:\Users\Dell Latitude i7 8th\Documents\hospital\diagrama_red_neuronal.png"
    if os.path.exists(img_path):
        doc.add_paragraph().alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(img_path, width=Inches(6.4))
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rc = cap.add_run("Figura 1: Arquitectura Multicapa Feedforward y Ciclo de Aprendizaje en PyTorch.")
        rc.font.size = Pt(9)
        rc.font.italic = True
        rc.font.color.rgb = c_gray

    p7 = doc.add_paragraph()
    p7.add_run(
        "Nuestra red 'ModeloDiagnosticoNN' está compuesta por 3 transformaciones lineales sucesivas entrelazadas "
        "con funciones de activación no lineales. Cada neurona ejecuta la ecuación fundamental del aprendizaje profundo:\n"
    )
    
    tbl_eq = doc.add_table(rows=1, cols=1)
    tbl_eq.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_eq = tbl_eq.cell(0, 0)
    set_cell_background(c_eq, "EFF6FF")
    set_cell_margins(c_eq, 80, 80, 120, 120)
    peq = c_eq.paragraphs[0]
    peq.alignment = WD_ALIGN_PARAGRAPH.CENTER
    req = peq.add_run("z = W · x + b   ===>   a = f(z)")
    req.font.name = "Arial"
    req.font.size = Pt(12)
    req.font.bold = True
    req.font.color.rgb = c_blue

    doc.add_heading("Desglose del Conteo de Parámetros (1,217 Pesos Entrenables):", level=2)
    p_params = doc.add_paragraph()
    p_params.add_run(
        "Es un ejercicio excelente para los estudiantes calcular manualmente el número total de parámetros del modelo:\n"
        "1. Capa 1: Linear(4, 32)  ==> (4 entradas × 32 neuronas) + 32 sesgos (bias) = 128 + 32 = 160 parámetros.\n"
        "2. Capa 2: Linear(32, 32) ==> (32 entradas × 32 neuronas) + 32 sesgos = 1,024 + 32 = 1,056 parámetros.\n"
        "3. Capa 3: Linear(32, 1)  ==> (32 entradas × 1 neurona) + 1 sesgo = 32 + 1 = 33 parámetros.\n\n"
        "Total de Parámetros Aprendibles = 160 + 1,056 + 33 = "
    )
    r_tp = p_params.add_run("1,217 parámetros flotantes.")
    r_tp.font.bold = True
    r_tp.font.color.rgb = c_teal

    # 4. PROPAGACIÓN HACIA ADELANTE PASO A PASO
    doc.add_heading("4. Propagación Hacia Adelante (Forward Pass) Paso a Paso", level=1)
    
    steps = [
        ("Capa Oculta 1: Linear(4, 32) + Activación ReLU",
         "Toma las 4 variables clínicas y las expande a 32 representaciones latentes. "
         "Inmediatamente aplica la función ReLU (Rectified Linear Unit):\n"
         "  f(z) = max(0, z)\n"
         "• ¿Por qué ReLU? Si el estímulo combinado es negativo, la neurona se apaga completamente (0). "
         "Si es positivo, transmite la señal con gradiente constante 1. Esto rompe la linealidad y evita el "
         "problema del desvanecimiento de gradientes (Vanishing Gradient)."),

        ("Capa Oculta 2: Linear(32, 32) + Activación ReLU",
         "Combina las 32 características preliminares entre sí para formar patrones fisiológicos de orden superior. "
         "Por ejemplo: una neurona de esta capa puede especializarse en detectar simultáneamente 'hipertensión arterial "
         "combinada con edad avanzada y glucosa limítrofe', un biomarcador de alto riesgo endotelial."),

        ("Capa de Salida: Linear(32, 1) + Activación Sigmoide",
         "Colapsa los 32 patrones diagnósticos en un único número escalar z_final. "
         "Para convertir ese número arbitrario en una probabilidad comprensible para médicos, aplica la función Sigmoide:\n"
         "  σ(z) = 1 / (1 + e^(-z))\n"
         "• Comportamiento:\n"
         "  - Si z es muy negativo (-∞) -> σ(z) tiende a 0.0 (0% riesgo).\n"
         "  - Si z es neutro (0.0) -> σ(z) = 0.5 (50% incertidumbre).\n"
         "  - Si z es muy positivo (+∞) -> σ(z) tiende a 1.0 (100% riesgo confirmado).\n"
         "• Regla de decisión clínica: Si ŷ >= 0.50 -> Diagnóstico Positivo; Si ŷ < 0.50 -> Negativo.")
    ]

    for st_title, st_desc in steps:
        h_st = doc.add_heading(st_title, level=2)
        h_st.paragraph_format.space_before = Pt(8)
        doc.add_paragraph(st_desc)

    # 5. CÓMO APRENDE LA RED: LOSS Y BACKPROPAGATION
    doc.add_page_break()
    doc.add_heading("5. ¿Cómo Aprende la Red? (Entrenamiento Local en el Hospital)", level=1)

    p_loss = doc.add_paragraph()
    p_loss.add_run(
        "El aprendizaje de la red neuronal en cada hospital sigue un ciclo riguroso de 3 etapas matemáticas:\n"
    )

    doc.add_heading("Etapa 1: Medición del Error (Binary Cross-Entropy Loss):", level=2)
    p_bce = doc.add_paragraph()
    p_bce.add_run(
        "Para comparar la probabilidad predicha por la red (ŷ) frente al diagnóstico médico real verificado (y ∈ {0, 1}), "
        "se utiliza la función de pérdida de Entropía Cruzada Binaria:\n"
    )
    
    tbl_bce = doc.add_table(rows=1, cols=1)
    tbl_bce.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_bce = tbl_bce.cell(0, 0)
    set_cell_background(c_bce, "FEF3C7")
    set_cell_margins(c_bce, 90, 90, 120, 120)
    pbce = c_bce.paragraphs[0]
    pbce.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rbce = pbce.add_run("Loss = - [ y · log(ŷ) + (1 - y) · log(1 - ŷ) ]")
    rbce.font.name = "Arial"
    rbce.font.size = Pt(12)
    rbce.font.bold = True
    rbce.font.color.rgb = c_amber

    p_bce_desc = doc.add_paragraph()
    p_bce_desc.paragraph_format.space_before = Pt(6)
    p_bce_desc.add_run(
        "Intuición pedagógica para los alumnos:\n"
        "• Caso 1: El paciente tiene diabetes (y = 1). La fórmula se simplifica a Loss = -log(ŷ). "
        "Si la red predijo 0.99 (99%), el logaritmo es casi 0, por lo que el error es despreciable. "
        "Pero si predijo 0.05 (5%), -log(0.05) = 2.99, aplicando una penalización severa.\n"
        "• Caso 2: El paciente está sano (y = 0). La fórmula se simplifica a Loss = -log(1 - ŷ). "
        "Si la red predijo erróneamente 0.95, la penalización se dispara hacia el infinito."
    )

    doc.add_heading("Etapa 2: Retropropagación del Gradiente (Backpropagation):", level=2)
    p_back = doc.add_paragraph()
    p_back.add_run(
        "Una vez calculado el Loss escalar, PyTorch recorre la red en reversa utilizando la regla de la cadena "
        "del cálculo multivariable para hallar las derivadas parciales de la pérdida con respecto a cada peso:\n"
        "  ∂Loss / ∂W\n"
        "Cada gradiente nos indica la sensibilidad de la red: 'Si aumento este peso específico en un 1%, ¿el error sube o baja?'"
    )

    doc.add_heading("Etapa 3: Optimizador Adam (Adaptive Moment Estimation):", level=2)
    p_adam = doc.add_paragraph()
    p_adam.add_run(
        "A diferencia del Descenso de Gradiente básico (SGD), el optimizador Adam mantiene promedios exponenciales móviles "
        "del gradiente (primer momento: velocidad) y del cuadrado del gradiente (segundo momento: escala). "
        "Actualiza los pesos con tasas de aprendizaje individuales para cada parámetro:\n"
        "  W_nuevo = W_actual - η · m̂ / (sqrt(v̂) + ε)\n"
        "Esto permite una convergencia mucho más rápida y estable, evitando atascarse en mesetas o mínimos locales."
    )

    # 6. CASO PRÁCTICO: EL PACIENTE DON JUAN
    doc.add_page_break()
    doc.add_heading("6. Caso Práctico Numérico: Evaluando a un Paciente Real", level=1)
    
    p_caso = doc.add_paragraph()
    p_caso.add_run(
        "Presenta este ejercicio a los alumnos para que sigan el flujo numérico completo:\n\n"
        "Paciente: Don Juan (55 años, IMC de 31.4 kg/m², glucosa en ayunas de 142.0 mg/dL, presión de 138.0 mm Hg).\n\n"
        "1. Estandarización de Entradas:\n"
        "   • z(edad) = (55 - 48) / 15 = +0.467\n"
        "   • z(imc) = (31.4 - 28.5) / 6 = +0.483\n"
        "   • z(glucosa) = (142 - 125) / 35 = +0.486\n"
        "   • z(presión) = (138 - 125) / 18 = +0.722\n\n"
        "2. Transformación en Capa Oculta 1:\n"
        "   Las 32 neuronas multiplican estas entradas por sus pesos W1 y suman sus sesgos b1. "
        "   Aquellas con sumas positivas activan sus valores mediante ReLU.\n\n"
        "3. Transformación en Capa Oculta 2:\n"
        "   Las 32 neuronas intermedias integran las señales anteriores y producen el vector latente H2.\n\n"
        "4. Inferencia en Capa de Salida:\n"
        "   La neurona final computa el producto escalar W3 · H2 + b3 = +1.658.\n"
        "   Aplica la función sigmoide: σ(1.658) = 1 / (1 + e^(-1.658)) = 0.840.\n\n"
        "5. Conclusión Diagnóstica:\n"
        "   Probabilidad de Diabetes = 84.0%. Clasificación: Riesgo Clínico Alto (Positivo). "
        "   El sistema alerta al facultativo médico en el dashboard para solicitar pruebas de hemoglobina glicosilada (HbA1c)."
    )

    # 7. EL GIRO FEDERADO (FEDAVG)
    doc.add_heading("7. El Salto al Aprendizaje Federado (FedAvg)", level=1)
    p_fed = doc.add_paragraph()
    p_fed.add_run(
        "El aspecto más fascinante de este proyecto para los alumnos es cómo esta red se entrena colectivamente "
        "sin que los historiales de los pacientes salgan de cada hospital:\n\n"
        "1. HospitalA entrena su red sobre sus 80 pacientes ancianos privados -> Obtiene matriz WA.\n"
        "2. HospitalB entrena su red sobre sus 80 pacientes jóvenes privados -> Obtiene matriz WB.\n"
        "3. HospitalC entrena su red sobre sus 80 pacientes con sobrepeso privados -> Obtiene matriz WC.\n"
        "4. Cada hospital envía por HTTP POST únicamente sus tensores de pesos numéricos al servidor Django.\n"
        "5. El Servidor Central aplica la agregación de Federated Averaging:\n"
    )

    tbl_fed = doc.add_table(rows=1, cols=1)
    tbl_fed.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_fed = tbl_fed.cell(0, 0)
    set_cell_background(c_fed, "F3E8FF")
    set_cell_margins(c_fed, 90, 90, 120, 120)
    pfed = c_fed.paragraphs[0]
    pfed.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rfed = pfed.add_run("W_global = (nA / N) · WA + (nB / N) · WB + (nC / N) · WC")
    rfed.font.name = "Arial"
    rfed.font.size = Pt(12)
    rfed.font.bold = True
    rfed.font.color.rgb = c_purple

    p_fed_fin = doc.add_paragraph()
    p_fed_fin.paragraph_format.space_before = Pt(6)
    p_fed_fin.add_run(
        "El nuevo modelo global posee la sabiduría clínica acumulada de los tres hospitales combinados, "
        "sin que ningún médico o servidor haya visto jamás los registros privados de los demás centros."
    )

    # 8. PREGUNTAS CLAVE PARA EVALUACIÓN EN CLASE
    doc.add_page_break()
    doc.add_heading("8. Preguntas de Discusión y Evaluación para la Clase", level=1)
    
    preguntas = [
        ("Pregunta 1: ¿Por qué usamos Sigmoide en la salida en vez de ReLU?",
         "Respuesta: Porque el diagnóstico médico requiere una probabilidad acotada estrictamente entre 0.0 (0%) y 1.0 (100%). "
         "ReLU produce valores desde 0 hasta infinito (+∞), lo cual carece de interpretación probabilística directa."),

        ("Pregunta 2: ¿Qué pasaría si promediáramos los pesos con promedio simple en vez de ponderado?",
         "Respuesta: Si un hospital tiene 1,000 pacientes y otro tiene solo 10, un promedio simple le daría el mismo peso "
         "al hospital pequeño que al grande, introduciendo un sesgo desproporcionado. FedAvg pondera por (n_k / N_total) "
         "para respetar la representatividad estadística de cada conjunto de datos."),

        ("Pregunta 3: ¿Por qué guardamos los pesos en MongoDB y no en SQLite?",
         "Respuesta: Los pesos de las redes neuronales son diccionarios estructurados en matrices de punto flotante de tamaño dinámico. "
         "El formato BSON de MongoDB es nativo para documentos semiestructurados y no requiere alterar esquemas relacionales "
         "cuando la arquitectura de la red evoluciona."),

        ("Pregunta 4: ¿Un atacante que intercepte los pesos enviados podría reconstruir al paciente?",
         "Respuesta: No de forma directa. Los pesos son combinaciones agregadas de cientos de muestras. Sin embargo, para entornos "
         "de ultra-alta seguridad, este sistema puede reforzarse adicionalmente con Privacidad Diferencial (DP) agregando ruido gaussiano "
         "a los gradientes, o Cifrado Homomórfico.")
    ]

    for pr, resp in preguntas:
        doc.add_heading(pr, level=2)
        doc.add_paragraph(resp)

    # Guardar
    out_path = r"c:\Users\Dell Latitude i7 8th\Documents\hospital\Guia_Didactica_Red_Neuronal_Universitaria.docx"
    doc.save(out_path)
    print(f"Guía didáctica universitaria guardada en: {out_path}")

if __name__ == "__main__":
    create_lecture_document()
