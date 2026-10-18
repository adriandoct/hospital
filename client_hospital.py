"""
================================================================================
CLIENTE DE HOSPITAL FEDERADO («client» HospitalA, HospitalB, HospitalC)
================================================================================
Este script emula la ejecución distribuida del agente hospitalario:
  1. Conexión autenticada mediante API Key secreta propia de cada hospital.
  2. Descarga del modelo global vigente (pesos W_global) desde GET /api/modelo/.
  3. Reconstrucción local de la red neuronal ModeloDiagnosticoNN con PyTorch.
  4. Carga de los registros clínicos privados almacenados localmente en el hospital.
  5. Entrenamiento local privado (Forward + Backward + Optimizador) durante E épocas.
  6. Extracción y envío exclusivo de los pesos resultantes W_k a POST /api/actualizaciones/.
  7. Confirmación de recepción y cálculo de FedAvg en el Servidor Central.

GARANTÍA DE PRIVACIDAD:
  Los datos clínicos NUNCA salen del hospital. Únicamente se transmiten matrices numéricas de pesos.
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import argparse
import requests
import torch
import torch.nn as nn
import torch.optim as optim
import random

# Ajustar PYTHONPATH para permitir importar la red neuronal del proyecto
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Inicializar Django para consultar las API Keys de los hospitales
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'federated_project.settings')
import django
django.setup()

from federated_app.models import Hospital
from federated_app.neural_network import (
    ModeloDiagnosticoNN,
    deserializar_state_dict,
    serializar_state_dict,
    normalizar_features
)
from federated_app.mongo_db import obtener_registros_por_hospital

SERVER_URL = "http://127.0.0.1:8000"


def generar_registros_locales_sinteticos(n=60):
    """
    Simula registros clínicos privados custodiados en la base de datos interna del hospital.
    Variables: [edad, imc, glucosa, presion] -> diagnostico (0|1)
    """
    registros = []
    for _ in range(n):
        edad = random.uniform(22, 78)
        imc = random.uniform(19, 44)
        presion = random.uniform(95, 175)
        riesgo = (edad * 0.03) + (imc * 0.08) + (presion * 0.02)
        glucosa = random.uniform(70, 130) + (riesgo * 15)
        score = (glucosa - 110) * 0.04 + (imc - 27) * 0.1 + (edad - 45) * 0.03
        prob = 1.0 / (1.0 + 2.71828 ** (-score))
        diag = 1 if (random.random() < prob or glucosa > 140) else 0

        registros.append({
            "edad": round(edad, 1),
            "imc": round(imc, 1),
            "glucosa": round(glucosa, 1),
            "presion": round(presion, 1),
            "diagnostico": diag
        })
    return registros


def entrenar_nodo_hospital(hospital_codigo, server_url=SERVER_URL, epochs=3, lr=0.01):
    print("\n" + "="*70)
    print(f"🏥 INICIANDO CLIENTE FEDERADO: {hospital_codigo}")
    print("="*70)

    # 1. Recuperar credencial API Key
    try:
        hosp_obj = Hospital.objects.get(codigo=hospital_codigo, activo=True)
        api_key = hosp_obj.api_key
        print(f"🔑 API Key verificada para {hosp_obj.nombre}: {api_key[:12]}...")
    except Hospital.DoesNotExist:
        print(f"❌ Error: El hospital '{hospital_codigo}' no está registrado o no está activo en la base de datos.")
        return False

    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    # 2. Descargar modelo global vigente desde el Servidor Central
    print(f"\n📡 Paso 1: Descargando modelo global desde GET {server_url}/api/modelo/ ...")
    try:
        res = requests.get(f"{server_url}/api/modelo/", headers=headers, timeout=10)
    except requests.exceptions.ConnectionError:
        print(f"❌ Error de conexión: No se pudo contactar con el servidor en {server_url}.")
        print("   Asegúrese de que el servidor Django esté corriendo con 'python manage.py runserver'.")
        return False

    if res.status_code != 200:
        print(f"❌ Error en descarga de modelo: {res.status_code} - {res.text}")
        return False

    modelo_info = res.json()
    version_global = modelo_info.get("version")
    ronda_activa = modelo_info.get("ronda_activa")
    print(f"✅ Modelo recibido con éxito | Versión: {version_global} | Ronda Activa: #{ronda_activa}")

    # 3. Cargar pesos en red neuronal PyTorch local
    print("🧠 Paso 2: Reconstruyendo 'ModeloDiagnosticoNN' local con PyTorch...")
    modelo_local = ModeloDiagnosticoNN()
    if modelo_info.get("pesos"):
        deserializar_state_dict(modelo_local, modelo_info["pesos"])

    # 4. Obtener registros privados (de MongoDB o locales)
    print("📋 Paso 3: Cargando historias clínicas privadas del hospital...")
    registros = obtener_registros_por_hospital(hospital_codigo)
    if not registros:
        print("   ⚠️ No se encontraron registros en MongoDB para este hospital, generando sintéticos locales...")
        registros = generar_registros_locales_sinteticos(n=75)

    print(f"   🔒 {len(registros)} registros clínicos cargados en memoria local (¡Los datos nunca saldrán de aquí!)")

    # Preparar tensores
    x_list = [[r["edad"], r["imc"], r["glucosa"], r["presion"]] for r in registros]
    y_list = [[r["diagnostico"]] for r in registros]

    x_tensor = normalizar_features(torch.tensor(x_list, dtype=torch.float32))
    y_tensor = torch.tensor(y_list, dtype=torch.float32)

    dataset = torch.utils.data.TensorDataset(x_tensor, y_tensor)
    loader = torch.utils.data.DataLoader(dataset, batch_size=16, shuffle=True)

    # 5. Entrenamiento local privado
    print(f"⚡ Paso 4: Entrenando red neuronal localmente ({epochs} épocas, Adam lr={lr})...")
    criterio = nn.BCELoss()
    optimizador = optim.Adam(modelo_local.parameters(), lr=lr)

    modelo_local.train()
    loss_final = 0.0
    for ep in range(epochs):
        epoch_loss = 0.0
        for b_x, b_y in loader:
            optimizador.zero_grad()
            pred = modelo_local(b_x)
            loss = criterio(pred, b_y)
            loss.backward()
            optimizador.step()
            epoch_loss += loss.item() * len(b_x)
        loss_final = epoch_loss / len(dataset)
        print(f"   [Época {ep + 1}/{epochs}] Loss local: {loss_final:.4f}")

    # Precisión local alcanzada
    modelo_local.eval()
    with torch.no_grad():
        preds = modelo_local(x_tensor)
        correctos = ((preds >= 0.5) == (y_tensor == 1)).sum().item()
        acc_local = correctos / len(dataset)
    print(f"   🎯 Precisión local alcanzada por {hospital_codigo}: {acc_local * 100:.2f}%")

    # 6. Serializar pesos calculados para enviar
    pesos_locales = serializar_state_dict(modelo_local)

    # 7. Enviar actualización al servidor central
    print(f"\n📤 Paso 5: Enviando pesos calculados a POST {server_url}/api/actualizaciones/ ...")
    payload = {
        "pesos": pesos_locales,
        "num_muestras": len(dataset),
        "loss_local": round(float(loss_final), 4),
        "acc_local": round(float(acc_local), 4)
    }

    resp_up = requests.post(f"{server_url}/api/actualizaciones/", headers=headers, json=payload, timeout=15)
    if resp_up.status_code != 200:
        print(f"❌ Error al enviar pesos: {resp_up.status_code} - {resp_up.text}")
        return False

    res_data = resp_up.json()
    print("✅ Respuesta del Servidor Federado:")
    print(f"   Mensaje: {res_data.get('mensaje')}")
    print(f"   Progreso de Ronda #{res_data.get('ronda_numero')}: "
          f"{res_data.get('actualizaciones_recibidas')}/{res_data.get('actualizaciones_esperadas')} hospitales")

    if res_data.get("ronda_completada"):
        nuevo = res_data.get("nuevo_modelo")
        print("\n🎉 ¡TODOS LOS HOSPITALES REPORTARON! El servidor ejecutó FedAvg exitosamente.")
        print(f"   🌟 Nueva Versión Global: {nuevo.get('version')}")
        print(f"   🎯 Nueva Precisión Global: {nuevo.get('metricas', {}).get('accuracy') * 100:.2f}%")
        print(f"   📉 Nuevo Loss Global: {nuevo.get('metricas', {}).get('loss')}")

    return True


def ejecutar_todos_los_hospitales(server_url=SERVER_URL):
    """
    Ejecuta el ciclo de los 3 hospitales en secuencia para completar una ronda de FedAvg.
    """
    hospitales = ["HospitalA", "HospitalB", "HospitalC"]
    print("\n🚀 INICIANDO SIMULACIÓN DE RONDA FEDERADA COMPLETA (HospitalA + HospitalB + HospitalC)")
    for h in hospitales:
        exito = entrenar_nodo_hospital(h, server_url)
        if not exito:
            print(f"Fallo en {h}. Deteniendo ejecución.")
            break
    print("\n✅ Simulación completada. Ingrese a http://127.0.0.1:8000/dashboard/ para ver el nuevo modelo.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cliente Federado de Hospital para Diabetes")
    parser.add_argument("--hospital", type=str, choices=["HospitalA", "HospitalB", "HospitalC", "all"], default="all",
                        help="Hospital específico o 'all' para simular los 3")
    parser.add_argument("--url", type=str, default=SERVER_URL, help="URL base del servidor Django")
    args = parser.parse_args()

    if args.hospital == "all":
        ejecutar_todos_los_hospitales(args.url)
    else:
        entrenar_nodo_hospital(args.hospital, args.url)
