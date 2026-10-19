"""
Script para generar el documento Word de la Práctica de Laboratorio en Google Colab
y el cuaderno interactivo Jupyter (.ipynb) correspondiente.
"""

import os
import sys
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_code_block(doc, code_str, title=None):
    if title:
        p_t = doc.add_paragraph()
        p_t.paragraph_format.space_before = Pt(8)
        p_t.paragraph_format.space_after = Pt(2)
        r = p_t.add_run(f"💻 {title}")
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(2, 132, 199)

    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "0F172A")  # Slate 900
    set_cell_margins(cell, top=130, bottom=130, left=170, right=170)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    
    run = p.add_run(code_str.strip())
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(226, 232, 240)
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(6)

def add_callout(doc, title, text, callout_type="info"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    
    colors = {
        "info": ("E0F2FE", "💡"),      # Sky
        "warning": ("FEF3C7", "⚠️"),   # Amber
        "success": ("DCFCE7", "✅"),   # Green
        "target": ("EDE9FE", "🎯")     # Purple
    }
    bg_hex, icon = colors.get(callout_type, colors["info"])
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
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.bold = True
    
    if level == 1:
        p.paragraph_format.space_before = Pt(20)
        p.paragraph_format.space_after = Pt(6)
        run.font.size = Pt(16)
        run.font.color.rgb = RGBColor(15, 23, 42)
    elif level == 2:
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(2, 132, 199)
    elif level == 3:
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(2)
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(13, 148, 136)
    return p

def generate_word_document():
    doc = Document()
    
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
    # PORTADA
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(15)
    p_inst.paragraph_format.space_after = Pt(4)
    run_inst = p_inst.add_run("GUÍA DE LABORATORIO EN GOOGLE COLAB\nCURSO DE INTELIGENCIA ARTIFICIAL & DEEP LEARNING")
    run_inst.font.name = "Arial"
    run_inst.font.size = Pt(11)
    run_inst.font.bold = True
    run_inst.font.color.rgb = RGBColor(100, 116, 139)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(8)
    run_icon = p_title.add_run("🧠 🔬 ☁️\n")
    run_icon.font.size = Pt(32)
    run_t = p_title.add_run("IMPLEMENTACIÓN Y ENTRENAMIENTO DE LA RED NEURONAL EN PYTORCH CON APRENDIZAJE FEDERADO")
    run_t.font.name = "Arial"
    run_t.font.size = Pt(20)
    run_t.font.bold = True
    run_t.font.color.rgb = RGBColor(15, 23, 42)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(20)
    run_sub = p_sub.add_run("Práctica Celda por Celda para Google Colab: Dataset Clínico, MLP, Normalización Z-Score, Algoritmo FedAvg y Métricas de Convergencia")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(12)
    run_sub.font.bold = True
    run_sub.font.color.rgb = RGBColor(2, 132, 199)

    # Tabla Ficha
    tbl = doc.add_table(rows=6, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    rows = [
        ("Entorno de Ejecución:", "Google Colaboratory (CPU o GPU gratuita)"),
        ("Framework de Deep Learning:", "PyTorch (torch, torch.nn, torch.optim)"),
        ("Arquitectura del Modelo:", "Perceptrón Multicapa (MLP: 4 entradas -> 32 -> 32 -> 1 salida Sigmoide)"),
        ("Problema Biomédico:", "Clasificación binaria de riesgo de diabetes mellitus"),
        ("Paradigma de Entrenamiento:", "Aprendizaje Federado (Federated Averaging - FedAvg) sobre 3 silos hospitalarios"),
        ("Nivel Académico:", "Pregrado Universitario (Ingeniería de Software / Sistemas / IA)")
    ]
    for i, (k, v) in enumerate(rows):
        c0, c1 = tbl.cell(i, 0), tbl.cell(i, 1)
        set_cell_background(c0, "F1F5F9")
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, top=70, bottom=70, left=120, right=120)
        set_cell_margins(c1, top=70, bottom=70, left=120, right=120)
        c0.paragraphs[0].text = k
        c0.paragraphs[0].runs[0].font.name = "Arial"
        c0.paragraphs[0].runs[0].font.size = Pt(9)
        c0.paragraphs[0].runs[0].font.bold = True
        c1.paragraphs[0].text = v
        c1.paragraphs[0].runs[0].font.name = "Calibri"
        c1.paragraphs[0].runs[0].font.size = Pt(9.5)

    doc.add_page_break()

    # SECCIÓN 1: INTRODUCCIÓN Y OBJETIVOS
    style_heading(doc.add_paragraph(), "1. Introducción y Objetivos de la Práctica", 1)
    p = doc.add_paragraph()
    p.add_run(
        "Esta práctica de laboratorio está diseñada para que el estudiante experimente en Google Colab cómo funciona internamente "
        "la red neuronal de diagnóstico desarrollada para el proyecto de Aprendizaje Federado de Salud. Sin requerir instalaciones "
        "locales complejas, el alumno construirá el modelo con PyTorch, simulará la segregación privada de datos en 3 hospitales, "
        "ejecutará el algoritmo matemático FedAvg y evaluará las métricas de rendimiento en tiempo real."
    )

    add_callout(doc, "Objetivos de Aprendizaje",
                "1. Dominar el uso de PyTorch (torch.nn.Module, tensores y optimizadores) en Google Colab.\n"
                "2. Comprender la función de la normalización Z-Score en datos clínicos con escalas dispares.\n"
                "3. Aprender cómo se serializan y promedian los pesos sinápticos de múltiples modelos locales.\n"
                "4. Observar empíricamente cómo el modelo global mejora su precisión (Accuracy) y reduce la pérdida (BCELoss) ronda a ronda.\n"
                "5. Construir un módulo interactivo de inferencia para evaluar pacientes con riesgo de diabetes.", "target")

    # SECCIÓN 2: DIAGRAMA DE LA RED
    style_heading(doc.add_paragraph(), "2. Arquitectura de la Red Neuronal (PyTorch)", 1)
    
    img_path = r"c:\Users\Dell Latitude i7 8th\Documents\hospital\diagrama_red_neuronal.png"
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(img_path, width=Inches(6.0))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(10)
        r = p_cap.add_run("Figura 1: Estructura del Perceptrón Multicapa (MLP) implementado en PyTorch.")
        r.font.name = "Arial"
        r.font.size = Pt(8.5)
        r.font.italic = True

    p = doc.add_paragraph()
    p.add_run(
        "El modelo recibe un tensor de dimensión [batch_size, 4] con las siguientes variables clínicas:\n"
        "• x1 (Edad): Años cumplidos del paciente (ej: 25 a 75 años).\n"
        "• x2 (IMC): Índice de Masa Corporal = peso / estatura² (ej: 18.5 a 45.0 kg/m²).\n"
        "• x3 (Glucosa): Nivel de glucosa plasmática en ayunas (ej: 70 a 220 mg/dL).\n"
        "• x4 (Presión): Presión arterial sistólica (ej: 90 a 180 mmHg).\n\n"
        "La salida y_hat es un único valor continuo acotado entre 0.0 y 1.0 por la función Sigmoide, que representa "
        "la probabilidad estimada de padecer diabetes mellitus."
    )

    doc.add_page_break()

    # SECCIÓN 3: SECUENCIA CELDA POR CELDA EN GOOGLE COLAB
    style_heading(doc.add_paragraph(), "3. Secuencia de Código Celda por Celda para Google Colab", 1)
    
    p = doc.add_paragraph()
    p.add_run(
        "A continuación se presenta el código completo estructurado en celdas individuales para que los alumnos lo copien "
        "directamente en su cuaderno de Google Colab (o carguen el archivo .ipynb adjunto)."
    )

    # CELDA 1
    style_heading(doc.add_paragraph(), "Celda 1: Importación de Bibliotecas y Verificación del Entorno", 2)
    p = doc.add_paragraph()
    p.add_run("Importamos PyTorch, sus módulos de redes neuronales y optimización, además de NumPy y Matplotlib para graficación:")
    add_code_block(doc, """# [CELDA 1] Importación de librerías esenciales
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import matplotlib.pyplot as plt
import random

# Fijar semilla pseudoaleatoria para reproducibilidad experimental
torch.manual_seed(42)
np.random.seed(42)
random.seed(42)

# Verificar dispositivo (CPU o aceleración por GPU CUDA)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"🚀 Entorno de Google Colab listo. Dispositivo de cálculo: {device}")
print(f"📦 Versión de PyTorch: {torch.__version__}")""", "Celda 1 - Imports y Configuración de Semilla")

    # CELDA 2
    style_heading(doc.add_paragraph(), "Celda 2: Generación del Dataset Clínico Sintético con Fisiología Real", 2)
    p = doc.add_paragraph()
    p.add_run(
        "Para que los alumnos puedan entrenar sin depender de archivos externos, creamos una función que simula "
        "muestras clínicas con correlación biológica real (mayor edad, mayor IMC y mayor presión aumentan el riesgo de hiperglucemia):"
    )
    add_code_block(doc, """# [CELDA 2] Generación de registros clínicos sintéticos
def generar_datos_clinicos(n_muestras=300):
    datos = []
    for _ in range(n_muestras):
        edad = random.uniform(22, 75)
        imc = random.uniform(19, 42)
        presion = random.uniform(95, 170)
        
        # Riesgo fisiológico correlacionado
        riesgo = (edad * 0.03) + (imc * 0.08) + (presion * 0.02)
        glucosa = random.uniform(70, 130) + (riesgo * 15)
        
        # Probabilidad logística de diagnóstico
        score = (glucosa - 110) * 0.04 + (imc - 27) * 0.1 + (edad - 45) * 0.03
        prob = 1.0 / (1.0 + np.exp(-score))
        diagnostico = 1.0 if (random.random() < prob or glucosa > 140) else 0.0
        
        datos.append([edad, imc, glucosa, presion, diagnostico])
        
    return np.array(datos, dtype=np.float32)

dataset_completo = generar_datos_clinicos(360)
print(f"✅ Total de historias clínicas generadas: {len(dataset_completo)}")
print(f"📋 Ejemplo de primer paciente [Edad, IMC, Glucosa, Presión, Diagnóstico]:\n   {dataset_completo[0]}")""", "Celda 2 - Generación de Datos Clínicos")

    # CELDA 3
    style_heading(doc.add_paragraph(), "Celda 3: Particionamiento Federado (Silos Hospitalarios)", 2)
    p = doc.add_paragraph()
    p.add_run(
        "Simulamos el aislamiento de datos. Cada hospital custodiará sus propias historias médicas sin compartirlas, "
        "y reservamos un conjunto de prueba global independiente para evaluar el modelo agregado:"
    )
    add_code_block(doc, """# [CELDA 3] Particionamiento en 3 Hospitales y 1 Conjunto de Prueba Global
# 80 pacientes para cada hospital, 120 pacientes para test global
datos_hosp_a = dataset_completo[0:80]
datos_hosp_b = dataset_completo[80:160]
datos_hosp_c = dataset_completo[160:240]
datos_test_global = dataset_completo[240:360]

print(f"🏥 Hospital Universitario San Carlos (HospitalA): {len(datos_hosp_a)} pacientes privados")
print(f"🏥 Hospital General Santa María (HospitalB):       {len(datos_hosp_b)} pacientes privados")
print(f"🏥 Clínica Especializada Metropolitana (HospitalC): {len(datos_hosp_c)} pacientes privados")
print(f"🌐 Test Set Global de Validación:                  {len(datos_test_global)} pacientes")""", "Celda 3 - Segregación Hospitalaria")

    doc.add_page_break()

    # CELDA 4
    style_heading(doc.add_paragraph(), "Celda 4: Normalización Z-Score y PyTorch Dataset", 2)
    p = doc.add_paragraph()
    p.add_run(
        "Implementamos la estandarización médica Z-Score y creamos una clase compatible con torch.utils.data.Dataset:"
    )
    add_code_block(doc, """# [CELDA 4] Estandarización médica Z-Score y Dataset de PyTorch
MEDIAS = torch.tensor([48.0, 28.5, 125.0, 125.0], dtype=torch.float32)
DESVIACIONES = torch.tensor([15.0, 6.0, 35.0, 18.0], dtype=torch.float32)

def normalizar_features(tensor_x):
    # z = (x - mu) / sigma
    return (tensor_x - MEDIAS) / (DESVIACIONES + 1e-7)

class DiabetesDataset(Dataset):
    def __init__(self, datos_numpy):
        # Separar variables X (columnas 0 a 3) y etiqueta Y (columna 4)
        x_raw = torch.tensor(datos_numpy[:, :4], dtype=torch.float32)
        self.x = normalizar_features(x_raw)
        self.y = torch.tensor(datos_numpy[:, 4:], dtype=torch.float32)

    def __len__(self):
        return len(self.x)

    def __getitem__(self, idx):
        return self.x[idx], self.y[idx]

# Creación de DataLoaders
loader_a = DataLoader(DiabetesDataset(datos_hosp_a), batch_size=16, shuffle=True)
loader_b = DataLoader(DiabetesDataset(datos_hosp_b), batch_size=16, shuffle=True)
loader_c = DataLoader(DiabetesDataset(datos_hosp_c), batch_size=16, shuffle=True)
loader_test = DataLoader(DiabetesDataset(datos_test_global), batch_size=32, shuffle=False)

print("✅ DataLoaders creados correctamente con normalización Z-Score.")""", "Celda 4 - Dataset y DataLoader")

    # CELDA 5
    style_heading(doc.add_paragraph(), "Celda 5: Definición del Perceptrón Multicapa (ModeloDiagnosticoNN)", 2)
    p = doc.add_paragraph()
    p.add_run(
        "Definimos la arquitectura del Perceptrón Multicapa con PyTorch y funciones de ayuda para serializar los pesos en diccionarios Python:"
    )
    add_code_block(doc, """# [CELDA 5] Arquitectura de la Red Neuronal y Serializador de Pesos
class ModeloDiagnosticoNN(nn.Module):
    def __init__(self):
        super(ModeloDiagnosticoNN, self).__init__()
        self.fc1 = nn.Linear(4, 32)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(32, 32)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(32, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        out = self.relu1(self.fc1(x))
        out = self.relu2(self.fc2(out))
        out = self.sigmoid(self.fc3(out))
        return out

def serializar_pesos(modelo):
    \"\"\"Convierte el state_dict de PyTorch a listas numéricas serializables\"\"\"
    return {k: v.detach().cpu().numpy().tolist() for k, v in modelo.state_dict().items()}

def deserializar_pesos(modelo, dict_pesos):
    \"\"\"Carga un diccionario de listas en el state_dict de PyTorch\"\"\"
    state_dict = {k: torch.tensor(v, dtype=torch.float32) for k, v in dict_pesos.items()}
    modelo.load_state_dict(state_dict)

# Instanciar y ver resumen
modelo_demo = ModeloDiagnosticoNN()
total_params = sum(p.numel() for p in modelo_demo.parameters())
print(modelo_demo)
print(f"📊 Total de parámetros entrenables: {total_params}")""", "Celda 5 - Clase de la Red Neuronal")

    doc.add_page_break()

    # CELDA 6
    style_heading(doc.add_paragraph(), "Celda 6: Función de Entrenamiento Local en el Nodo Hospitalario", 2)
    p = doc.add_paragraph()
    p.add_run(
        "Esta función emula lo que cada hospital ejecuta en su servidor privado durante una ronda. Entrena durante E épocas "
        "usando Binary Cross-Entropy Loss (BCELoss) y el optimizador Adam:"
    )
    add_code_block(doc, """# [CELDA 6] Entrenamiento local de un nodo hospitalario
def entrenar_hospital_local(modelo_inicial, data_loader, epochs=4, lr=0.01):
    modelo_local = ModeloDiagnosticoNN()
    modelo_local.load_state_dict(modelo_inicial.state_dict())
    modelo_local.train()

    criterion = nn.BCELoss()
    optimizer = optim.Adam(modelo_local.parameters(), lr=lr)

    loss_final = 0.0
    for epoch in range(epochs):
        epoch_loss = 0.0
        for batch_x, batch_y in data_loader:
            optimizer.zero_grad()
            pred = modelo_local(batch_x)
            loss = criterion(pred, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        loss_final = epoch_loss / len(data_loader)

    # Evaluar precisión local
    modelo_local.eval()
    correctos = 0
    total = 0
    with torch.no_grad():
        for batch_x, batch_y in data_loader:
            pred = modelo_local(batch_x)
            clase = (pred >= 0.5).float()
            correctos += (clase == batch_y).sum().item()
            total += len(batch_y)

    acc_local = correctos / total
    pesos_actualizados = serializar_pesos(modelo_local)
    return pesos_actualizados, loss_final, acc_local, total""", "Celda 6 - Entrenamiento Local")

    # CELDA 7
    style_heading(doc.add_paragraph(), "Celda 7: Algoritmo de Agregación Federated Averaging (FedAvg)", 2)
    p = doc.add_paragraph()
    p.add_run(
        "El Servidor Central recibe los pesos de los 3 hospitales y computa el promedio ponderado exacto:"
    )
    add_code_block(doc, """# [CELDA 7] Algoritmo FedAvg matemático
def fed_avg(actualizaciones):
    total_muestras = sum(upd["num_muestras"] for upd in actualizaciones)
    pesos_agregados = {}
    claves = actualizaciones[0]["pesos"].keys()

    for key in claves:
        tensor_promedio = None
        for upd in actualizaciones:
            peso_ponderador = upd["num_muestras"] / total_muestras
            tensor_hosp = torch.tensor(upd["pesos"][key], dtype=torch.float32)
            if tensor_promedio is None:
                tensor_promedio = tensor_hosp * peso_ponderador
            else:
                tensor_promedio += tensor_hosp * peso_ponderador
        pesos_agregados[key] = tensor_promedio.detach().cpu().numpy().tolist()

    return pesos_agregados

def evaluar_modelo_global(modelo, test_loader):
    \"\"\"Calcula Accuracy y BCELoss en el conjunto de prueba global\"\"\"
    modelo.eval()
    criterion = nn.BCELoss()
    total_loss = 0.0
    correctos = 0
    total = 0

    with torch.no_grad():
        for batch_x, batch_y in test_loader:
            pred = modelo(batch_x)
            loss = criterion(pred, batch_y)
            total_loss += loss.item()
            clase = (pred >= 0.5).float()
            correctos += (clase == batch_y).sum().item()
            total += len(batch_y)

    return correctos / total, total_loss / len(test_loader)""", "Celda 7 - FedAvg y Evaluación Global")

    doc.add_page_break()

    # CELDA 8
    style_heading(doc.add_paragraph(), "Celda 8: Simulación Completa de Rondas Federadas", 2)
    p = doc.add_paragraph()
    p.add_run(
        "Ejecutamos un ciclo completo de 5 rondas de aprendizaje federado entre los 3 hospitales y registramos la convergencia:"
    )
    add_code_block(doc, """# [CELDA 8] Bucle de orquestación federada (5 rondas de aprendizaje)
modelo_global = ModeloDiagnosticoNN()

historial_rondas = []
historial_acc = []
historial_loss = []

# Evaluación ronda 0 (modelo base aleatorio)
acc_0, loss_0 = evaluar_modelo_global(modelo_global, loader_test)
historial_rondas.append(0)
historial_acc.append(acc_0 * 100)
historial_loss.append(loss_0)
print(f"⭐ Ronda #0 (Base Inicial) -> Precisión Global: {acc_0*100:.2f}% | Pérdida: {loss_0:.4f}")

NUM_RONDAS = 5
for r in range(1, NUM_RONDAS + 1):
    print(f"\\n{'='*60}")
    print(f"🔄 INICIANDO RONDA FEDERADA #{r}")
    print(f"{'='*60}")

    # 1. Cada hospital entrena localmente sobre sus propios pacientes
    w_a, loss_a, acc_a, n_a = entrenar_hospital_local(modelo_global, loader_a, epochs=3, lr=0.015)
    w_b, loss_b, acc_b, n_b = entrenar_hospital_local(modelo_global, loader_b, epochs=3, lr=0.015)
    w_c, loss_c, acc_c, n_c = entrenar_hospital_local(modelo_global, loader_c, epochs=3, lr=0.015)

    print(f"   🏥 HospitalA: Loss={loss_a:.4f}, Acc={acc_a*100:.1f}% ({n_a} pacientes)")
    print(f"   🏥 HospitalB: Loss={loss_b:.4f}, Acc={acc_b*100:.1f}% ({n_b} pacientes)")
    print(f"   🏥 HospitalC: Loss={loss_c:.4f}, Acc={acc_c*100:.1f}% ({n_c} pacientes)")

    # 2. Empaquetar deltas de pesos para el agregador
    actualizaciones = [
        {"pesos": w_a, "num_muestras": n_a},
        {"pesos": w_b, "num_muestras": n_b},
        {"pesos": w_c, "num_muestras": n_c}
    ]

    # 3. Servidor Central ejecuta FedAvg
    pesos_agregados = fed_avg(actualizaciones)

    # 4. Actualizar el modelo global
    deserializar_pesos(modelo_global, pesos_agregados)

    # 5. Evaluar nuevo modelo global sobre test set independiente
    acc_global, loss_global = evaluar_modelo_global(modelo_global, loader_test)
    historial_rondas.append(r)
    historial_acc.append(acc_global * 100)
    historial_loss.append(loss_global)

    print(f"   🎯 RESULTADO RONDA #{r} -> Precisión Global: {acc_global*100:.2f}% | Pérdida: {loss_global:.4f}")""", "Celda 8 - Bucle de Rondas Federadas")

    # CELDA 9
    style_heading(doc.add_paragraph(), "Celda 9: Gráficas de Convergencia con Matplotlib", 2)
    p = doc.add_paragraph()
    p.add_run("Generamos las curvas de evolución de precisión y pérdida, replicando el dashboard web:")
    add_code_block(doc, """# [CELDA 9] Gráficas de convergencia del modelo global federado
plt.figure(figsize=(12, 5))

# Gráfico 1: Precisión Global (Accuracy)
plt.subplot(1, 2, 1)
plt.plot(historial_rondas, historial_acc, marker='o', color='#10b981', linewidth=2.5, label='Precisión (%)')
plt.title('Evolución de la Precisión Global (Test Set)', fontsize=12, fontweight='bold')
plt.xlabel('Ronda Federada (FedAvg)')
plt.ylabel('Precisión (%)')
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend()

# Gráfico 2: Pérdida Global (BCELoss)
plt.subplot(1, 2, 2)
plt.plot(historial_rondas, historial_loss, marker='s', color='#f59e0b', linewidth=2.5, label='Pérdida (BCELoss)')
plt.title('Evolución de la Pérdida Global', fontsize=12, fontweight='bold')
plt.xlabel('Ronda Federada (FedAvg)')
plt.ylabel('Pérdida (BCE Loss)')
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend()

plt.tight_layout()
plt.show()""", "Celda 9 - Curvas de Convergencia")

    doc.add_page_break()

    # CELDA 10
    style_heading(doc.add_paragraph(), "Celda 10: Inferencia Clínica de Pacientes en Tiempo Real", 2)
    p = doc.add_paragraph()
    p.add_run(
        "Permite a los estudiantes introducir datos de pacientes arbitrarios y obtener la probabilidad diagnóstica calculada por el modelo global:"
    )
    add_code_block(doc, """# [CELDA 10] Diagnóstico clínico interactivo con el modelo global
def evaluar_paciente(edad, imc, glucosa, presion):
    modelo_global.eval()
    x_input = torch.tensor([[float(edad), float(imc), float(glucosa), float(presion)]], dtype=torch.float32)
    x_norm = normalizar_features(x_input)

    with torch.no_grad():
        prob = modelo_global(x_norm).item()

    porcentaje = prob * 100
    if prob >= 0.70:
        alerta = "ALTA PRIORIDAD (Riesgo Crítico)"
        diag = "Positivo para Diabetes Mellitus"
    elif prob >= 0.40:
        alerta = "MODERADA (Pre-diabetes / Seguimiento)"
        diag = "Riesgo Moderado"
    else:
        alerta = "BAJA (Valores fisiológicos normales)"
        diag = "Negativo / Bajo Riesgo"

    print(f"\\n{'='*55}")
    print(f"🩺 INFORME DIAGNÓSTICO DEL MODELO GLOBAL FEDERADO")
    print(f"{'='*55}")
    print(f"👤 Datos Paciente: Edad: {edad} años | IMC: {imc} | Glucosa: {glucosa} mg/dL | Presión: {presion} mmHg")
    print(f"📊 Probabilidad Estimada: {porcentaje:.2f}%")
    print(f"📋 Diagnóstico Sugerido:  {diag}")
    print(f"🚨 Nivel de Alerta:       {alerta}")
    print(f"{'='*55}")

# Prueba 1: Paciente con valores elevados
evaluar_paciente(edad=58, imc=33.4, glucosa=165, presion=145)

# Prueba 2: Paciente joven con valores normales
evaluar_paciente(edad=24, imc=21.2, glucosa=88, presion=110)""", "Celda 10 - Inferencia Clínica")

    # SECCIÓN 4: CUESTIONARIO Y RETOS DE LABORATORIO
    style_heading(doc.add_paragraph(), "4. Tareas Prácticas y Retos para el Alumno", 1)
    
    retos = [
        ("Reto 1: Variar la Tasa de Aprendizaje (Learning Rate)", 
         "Modifica el parámetro lr de 0.015 a 0.1 y a 0.001 en la Celda 8. Observa cómo cambia la estabilidad y velocidad de convergencia de FedAvg."),
        ("Reto 2: Simular Datos No-IID (Distribución Desbalanceada)",
         "En la Celda 2, crea el HospitalA con pacientes mayores de 60 años con alta glucosa, y el HospitalB con pacientes menores de 30 años sanos. Observa cómo el modelo FedAvg logra balancear ambas poblaciones."),
        ("Reto 3: Comparativa Centralizada vs. Federada",
         "Entrena un modelo con todos los datos juntos (centralizado) y compara su precisión final contra el modelo federado. ¿Qué tanta precisión se 'sacrifica' a cambio de garantizar privacidad médica total? (Típicamente menos del 1-2%)."),
        ("Reto 4: Añadir Regularización Dropout o BatchNorm",
         "Modifica la clase ModeloDiagnosticoNN en la Celda 5 agregando capas nn.Dropout(0.2) entre las capas ocultas para evitar el sobreajuste (overfitting).")
    ]
    for tit, desc in retos:
        style_heading(doc.add_paragraph(), tit, 2)
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        r = p.add_run(desc)
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)

    output_doc = "Practica_Google_Colab_Red_Neuronal_PyTorch.docx"
    doc.save(output_doc)
    print(f"✅ Documento Word generado: {os.path.abspath(output_doc)}")

def generate_ipynb_notebook():
    """Genera el cuaderno interactivo .ipynb con todas las celdas listas para Colab."""
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 0,
        "metadata": {
            "colab": {
                "name": "Practica_Aprendizaje_Federado_PyTorch.ipynb",
                "provenance": []
            },
            "kernelspec": {
                "name": "python3",
                "display_name": "Python 3"
            },
            "language_info": {
                "name": "python"
            }
        },
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# 🏥 Laboratorio en Google Colab: Red Neuronal con PyTorch y Aprendizaje Federado (FedAvg)\n",
                    "### Diagnóstico Distribuido de Diabetes sin Compartir Datos Clínicos Privados\n",
                    "---\n",
                    "Este cuaderno interactivo replica celda por celda el motor de Deep Learning utilizado en el proyecto de telemedicina federada.\n",
                    "Aprenderás a:\n",
                    "1. Definir un Perceptrón Multicapa (`ModeloDiagnosticoNN`) con PyTorch.\n",
                    "2. Aplicar normalización Z-Score a variables clínicas.\n",
                    "3. Simular 3 hospitales independientes (`HospitalA`, `HospitalB`, `HospitalC`).\n",
                    "4. Implementar el algoritmo de agregación ponderada **Federated Averaging (FedAvg)**.\n",
                    "5. Trazar gráficas de convergencia y evaluar pacientes en tiempo real."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# [CELDA 1] Importación de librerías esenciales y fijación de semillas\n",
                    "import torch\n",
                    "import torch.nn as nn\n",
                    "import torch.optim as optim\n",
                    "from torch.utils.data import Dataset, DataLoader\n",
                    "import numpy as np\n",
                    "import matplotlib.pyplot as plt\n",
                    "import random\n",
                    "\n",
                    "torch.manual_seed(42)\n",
                    "np.random.seed(42)\n",
                    "random.seed(42)\n",
                    "\n",
                    "device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')\n",
                    "print(f'🚀 Google Colab listo en dispositivo: {device}')\n",
                    "print(f'📦 PyTorch versión: {torch.__version__}')"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# [CELDA 2] Generación del dataset sintético con correlación médica\n",
                    "def generar_datos_clinicos(n_muestras=360):\n",
                    "    datos = []\n",
                    "    for _ in range(n_muestras):\n",
                    "        edad = random.uniform(22, 75)\n",
                    "        imc = random.uniform(19, 42)\n",
                    "        presion = random.uniform(95, 170)\n",
                    "        \n",
                    "        # Riesgo fisiológico correlacionado\n",
                    "        riesgo = (edad * 0.03) + (imc * 0.08) + (presion * 0.02)\n",
                    "        glucosa = random.uniform(70, 130) + (riesgo * 15)\n",
                    "        \n",
                    "        # Score logístico para diagnóstico de diabetes\n",
                    "        score = (glucosa - 110) * 0.04 + (imc - 27) * 0.1 + (edad - 45) * 0.03\n",
                    "        prob = 1.0 / (1.0 + np.exp(-score))\n",
                    "        diagnostico = 1.0 if (random.random() < prob or glucosa > 140) else 0.0\n",
                    "        \n",
                    "        datos.append([edad, imc, glucosa, presion, diagnostico])\n",
                    "    return np.array(datos, dtype=np.float32)\n",
                    "\n",
                    "dataset_completo = generar_datos_clinicos(360)\n",
                    "print(f'✅ Total de pacientes generados: {len(dataset_completo)}')\n",
                    "print(f'📋 Primer paciente [Edad, IMC, Glucosa, Presión, Diagnóstico]:\\n   {dataset_completo[0]}')"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# [CELDA 3] Segregación en 3 silos hospitalarios privados y test global\n",
                    "datos_hosp_a = dataset_completo[0:80]\n",
                    "datos_hosp_b = dataset_completo[80:160]\n",
                    "datos_hosp_c = dataset_completo[160:240]\n",
                    "datos_test_global = dataset_completo[240:360]\n",
                    "\n",
                    "print(f'🏥 HospitalA (San Carlos):       {len(datos_hosp_a)} historias privadas')\n",
                    "print(f'🏥 HospitalB (Santa María):      {len(datos_hosp_b)} historias privadas')\n",
                    "print(f'🏥 HospitalC (Metropolitana):    {len(datos_hosp_c)} historias privadas')\n",
                    "print(f'🌐 Test Set Global de Validación:{len(datos_test_global)} historias')"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# [CELDA 4] Estandarización Z-Score y clase Dataset en PyTorch\n",
                    "MEDIAS = torch.tensor([48.0, 28.5, 125.0, 125.0], dtype=torch.float32)\n",
                    "DESVIACIONES = torch.tensor([15.0, 6.0, 35.0, 18.0], dtype=torch.float32)\n",
                    "\n",
                    "def normalizar_features(tensor_x):\n",
                    "    return (tensor_x - MEDIAS) / (DESVIACIONES + 1e-7)\n",
                    "\n",
                    "class DiabetesDataset(Dataset):\n",
                    "    def __init__(self, datos_numpy):\n",
                    "        x_raw = torch.tensor(datos_numpy[:, :4], dtype=torch.float32)\n",
                    "        self.x = normalizar_features(x_raw)\n",
                    "        self.y = torch.tensor(datos_numpy[:, 4:], dtype=torch.float32)\n",
                    "\n",
                    "    def __len__(self):\n",
                    "        return len(self.x)\n",
                    "\n",
                    "    def __getitem__(self, idx):\n",
                    "        return self.x[idx], self.y[idx]\n",
                    "\n",
                    "loader_a = DataLoader(DiabetesDataset(datos_hosp_a), batch_size=16, shuffle=True)\n",
                    "loader_b = DataLoader(DiabetesDataset(datos_hosp_b), batch_size=16, shuffle=True)\n",
                    "loader_c = DataLoader(DiabetesDataset(datos_hosp_c), batch_size=16, shuffle=True)\n",
                    "loader_test = DataLoader(DiabetesDataset(datos_test_global), batch_size=32, shuffle=False)\n",
                    "\n",
                    "print('✅ DataLoaders inicializados correctamente.')"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# [CELDA 5] Definición de la Red Neuronal (Perceptrón Multicapa)\n",
                    "class ModeloDiagnosticoNN(nn.Module):\n",
                    "    def __init__(self):\n",
                    "        super(ModeloDiagnosticoNN, self).__init__()\n",
                    "        self.fc1 = nn.Linear(4, 32)\n",
                    "        self.relu1 = nn.ReLU()\n",
                    "        self.fc2 = nn.Linear(32, 32)\n",
                    "        self.relu2 = nn.ReLU()\n",
                    "        self.fc3 = nn.Linear(32, 1)\n",
                    "        self.sigmoid = nn.Sigmoid()\n",
                    "\n",
                    "    def forward(self, x):\n",
                    "        out = self.relu1(self.fc1(x))\n",
                    "        out = self.relu2(self.fc2(out))\n",
                    "        out = self.sigmoid(self.fc3(out))\n",
                    "        return out\n",
                    "\n",
                    "def serializar_pesos(modelo):\n",
                    "    return {k: v.detach().cpu().numpy().tolist() for k, v in modelo.state_dict().items()}\n",
                    "\n",
                    "def deserializar_pesos(modelo, dict_pesos):\n",
                    "    state_dict = {k: torch.tensor(v, dtype=torch.float32) for k, v in dict_pesos.items()}\n",
                    "    modelo.load_state_dict(state_dict)\n",
                    "\n",
                    "modelo_demo = ModeloDiagnosticoNN()\n",
                    "print(modelo_demo)\n",
                    "print(f'📊 Total de parámetros sinápticos: {sum(p.numel() for p in modelo_demo.parameters())}')"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# [CELDA 6] Función de entrenamiento privado local de un hospital\n",
                    "def entrenar_hospital_local(modelo_inicial, data_loader, epochs=3, lr=0.015):\n",
                    "    modelo_local = ModeloDiagnosticoNN()\n",
                    "    modelo_local.load_state_dict(modelo_inicial.state_dict())\n",
                    "    modelo_local.train()\n",
                    "\n",
                    "    criterion = nn.BCELoss()\n",
                    "    optimizer = optim.Adam(modelo_local.parameters(), lr=lr)\n",
                    "\n",
                    "    loss_final = 0.0\n",
                    "    for epoch in range(epochs):\n",
                    "        epoch_loss = 0.0\n",
                    "        for batch_x, batch_y in data_loader:\n",
                    "            optimizer.zero_grad()\n",
                    "            pred = modelo_local(batch_x)\n",
                    "            loss = criterion(pred, batch_y)\n",
                    "            loss.backward()\n",
                    "            optimizer.step()\n",
                    "            epoch_loss += loss.item()\n",
                    "        loss_final = epoch_loss / len(data_loader)\n",
                    "\n",
                    "    modelo_local.eval()\n",
                    "    correctos = 0\n",
                    "    total = 0\n",
                    "    with torch.no_grad():\n",
                    "        for batch_x, batch_y in data_loader:\n",
                    "            pred = modelo_local(batch_x)\n",
                    "            clase = (pred >= 0.5).float()\n",
                    "            correctos += (clase == batch_y).sum().item()\n",
                    "            total += len(batch_y)\n",
                    "\n",
                    "    return serializar_pesos(modelo_local), loss_final, (correctos / total), total"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# [CELDA 7] Algoritmo FedAvg y evaluación global sobre el Test Set\n",
                    "def fed_avg(actualizaciones):\n",
                    "    total_muestras = sum(upd['num_muestras'] for upd in actualizaciones)\n",
                    "    pesos_agregados = {}\n",
                    "    claves = actualizaciones[0]['pesos'].keys()\n",
                    "\n",
                    "    for key in claves:\n",
                    "        tensor_promedio = None\n",
                    "        for upd in actualizaciones:\n",
                    "            peso_ponderador = upd['num_muestras'] / total_muestras\n",
                    "            tensor_hosp = torch.tensor(upd['pesos'][key], dtype=torch.float32)\n",
                    "            if tensor_promedio is None:\n",
                    "                tensor_promedio = tensor_hosp * peso_ponderador\n",
                    "            else:\n",
                    "                tensor_promedio += tensor_hosp * peso_ponderador\n",
                    "        pesos_agregados[key] = tensor_promedio.detach().cpu().numpy().tolist()\n",
                    "\n",
                    "    return pesos_agregados\n",
                    "\n",
                    "def evaluar_modelo_global(modelo, test_loader):\n",
                    "    modelo.eval()\n",
                    "    criterion = nn.BCELoss()\n",
                    "    total_loss = 0.0\n",
                    "    correctos = 0\n",
                    "    total = 0\n",
                    "    with torch.no_grad():\n",
                    "        for batch_x, batch_y in test_loader:\n",
                    "            pred = modelo(batch_x)\n",
                    "            total_loss += criterion(pred, batch_y).item()\n",
                    "            clase = (pred >= 0.5).float()\n",
                    "            correctos += (clase == batch_y).sum().item()\n",
                    "            total += len(batch_y)\n",
                    "    return (correctos / total), (total_loss / len(test_loader))"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# [CELDA 8] Ejecución de 5 rondas federadas sincrónicas\n",
                    "modelo_global = ModeloDiagnosticoNN()\n",
                    "\n",
                    "historial_rondas = [0]\n",
                    "acc_0, loss_0 = evaluar_modelo_global(modelo_global, loader_test)\n",
                    "historial_acc = [acc_0 * 100]\n",
                    "historial_loss = [loss_0]\n",
                    "print(f'⭐ Ronda #0 (Inicial) -> Precisión Global: {acc_0*100:.2f}% | Pérdida: {loss_0:.4f}')\n",
                    "\n",
                    "for r in range(1, 6):\n",
                    "    print(f'\\n--- RONDA FEDERADA #{r} ---')\n",
                    "    w_a, loss_a, acc_a, n_a = entrenar_hospital_local(modelo_global, loader_a, epochs=3, lr=0.015)\n",
                    "    w_b, loss_b, acc_b, n_b = entrenar_hospital_local(modelo_global, loader_b, epochs=3, lr=0.015)\n",
                    "    w_c, loss_c, acc_c, n_c = entrenar_hospital_local(modelo_global, loader_c, epochs=3, lr=0.015)\n",
                    "    print(f'  🏥 HospA: Acc={acc_a*100:.1f}%, Loss={loss_a:.4f}')\n",
                    "    print(f'  🏥 HospB: Acc={acc_b*100:.1f}%, Loss={loss_b:.4f}')\n",
                    "    print(f'  🏥 HospC: Acc={acc_c*100:.1f}%, Loss={loss_c:.4f}')\n",
                    "    \n",
                    "    actualizaciones = [\n",
                    "        {'pesos': w_a, 'num_muestras': n_a},\n",
                    "        {'pesos': w_b, 'num_muestras': n_b},\n",
                    "        {'pesos': w_c, 'num_muestras': n_c}\n",
                    "    ]\n",
                    "    pesos_agregados = fed_avg(actualizaciones)\n",
                    "    deserializar_pesos(modelo_global, pesos_agregados)\n",
                    "    \n",
                    "    acc_glob, loss_glob = evaluar_modelo_global(modelo_global, loader_test)\n",
                    "    historial_rondas.append(r)\n",
                    "    historial_acc.append(acc_glob * 100)\n",
                    "    historial_loss.append(loss_glob)\n",
                    "    print(f'  🎯 MODELO GLOBAL RONDA #{r} -> Precisión: {acc_glob*100:.2f}% | Pérdida: {loss_glob:.4f}')"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# [CELDA 9] Visualización de las curvas de convergencia (Accuracy & Loss)\n",
                    "plt.figure(figsize=(12, 5))\n",
                    "plt.subplot(1, 2, 1)\n",
                    "plt.plot(historial_rondas, historial_acc, marker='o', color='#10b981', linewidth=2.5, label='Precisión Global (%)')\n",
                    "plt.title('Evolución de la Precisión Global (Test Set)', fontsize=12, fontweight='bold')\n",
                    "plt.xlabel('Ronda Federada')\n",
                    "plt.ylabel('Precisión (%)')\n",
                    "plt.grid(True, linestyle='--', alpha=0.5)\n",
                    "plt.legend()\n",
                    "\n",
                    "plt.subplot(1, 2, 2)\n",
                    "plt.plot(historial_rondas, historial_loss, marker='s', color='#f59e0b', linewidth=2.5, label='Pérdida Global (BCELoss)')\n",
                    "plt.title('Evolución de la Pérdida Global', fontsize=12, fontweight='bold')\n",
                    "plt.xlabel('Ronda Federada')\n",
                    "plt.ylabel('Pérdida (BCELoss)')\n",
                    "plt.grid(True, linestyle='--', alpha=0.5)\n",
                    "plt.legend()\n",
                    "plt.tight_layout()\n",
                    "plt.show()"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# [CELDA 10] Diagnóstico interactivo de pacientes con el modelo global\n",
                    "def evaluar_paciente(edad, imc, glucosa, presion):\n",
                    "    modelo_global.eval()\n",
                    "    x_input = torch.tensor([[float(edad), float(imc), float(glucosa), float(presion)]], dtype=torch.float32)\n",
                    "    x_norm = normalizar_features(x_input)\n",
                    "    with torch.no_grad():\n",
                    "        prob = modelo_global(x_norm).item()\n",
                    "    \n",
                    "    diag = 'Positivo para Diabetes Mellitus' if prob >= 0.50 else 'Negativo / Bajo Riesgo'\n",
                    "    alerta = 'ALTA PRIORIDAD' if prob >= 0.70 else ('MODERADA' if prob >= 0.40 else 'BAJA')\n",
                    "    print(f'\\n🩺 EVALUACIÓN CLÍNICA: Paciente (Edad={edad}, IMC={imc}, Glucosa={glucosa}, Presión={presion})')\n",
                    "    print(f'   Probabilidad Estimada: {prob*100:.2f}% | Diagnóstico: {diag} | Alerta: {alerta}')\n",
                    "\n",
                    "# Evaluación de dos casos clínicos de prueba\n",
                    "evaluar_paciente(edad=58, imc=33.5, glucosa=165, presion=145)\n",
                    "evaluar_paciente(edad=24, imc=21.0, glucosa=85, presion=110)"
                ]
            }
        ]
    }
    
    output_ipynb = "Practica_Google_Colab_Red_Neuronal.ipynb"
    with open(output_ipynb, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=2, ensure_ascii=False)
    print(f"✅ Cuaderno Jupyter generado: {os.path.abspath(output_ipynb)}")

if __name__ == "__main__":
    generate_word_document()
    generate_ipynb_notebook()
