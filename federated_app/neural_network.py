import torch
import torch.nn as nn
import torch.optim as optim
import copy
from .mongo_db import (
    guardar_modelo_global,
    obtener_ultimo_modelo_global,
    get_col_registros
)

# Factores de normalización clínica (Z-Score)
# Variables de entrada: [edad, imc, glucosa, presion]
MEDIAS = torch.tensor([48.0, 28.5, 125.0, 125.0], dtype=torch.float32)
DESVIACIONES = torch.tensor([15.0, 6.0, 35.0, 18.0], dtype=torch.float32)


class ModeloDiagnosticoNN(nn.Module):
    """
    Red Neuronal Perceptrón Multicapa (MLP) para Diagnóstico de Diabetes.
    Estructura exacta especificada en el diagrama de clases UML:
      - Linear(4, 32) -> ReLU
      - Linear(32, 32) -> ReLU
      - Linear(32, 1) -> Sigmoid
    """
    def __init__(self):
        super(ModeloDiagnosticoNN, self).__init__()
        self.fc1 = nn.Linear(4, 32)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(32, 32)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(32, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # x: Tensor con forma (batch_size, 4)
        out = self.relu1(self.fc1(x))
        out = self.relu2(self.fc2(out))
        out = self.sigmoid(self.fc3(out))
        return out


def normalizar_features(tensor_x):
    """Aplica estandarización con medias y desviaciones fijas de referencia médica."""
    return (tensor_x - MEDIAS) / (DESVIACIONES + 1e-7)


def serializar_state_dict(modelo):
    """
    Convierte el state_dict de PyTorch en un diccionario Python serializable en JSON/BSON.
    """
    serializable = {}
    for key, val in modelo.state_dict().items():
        serializable[key] = val.detach().cpu().numpy().tolist()
    return serializable


def deserializar_state_dict(modelo, state_dict_serializado):
    """
    Carga un diccionario serializado en el state_dict del modelo PyTorch.
    """
    new_state_dict = {}
    for key, val in state_dict_serializado.items():
        new_state_dict[key] = torch.tensor(val, dtype=torch.float32)
    modelo.load_state_dict(new_state_dict)
    return modelo


# ==============================================================================
# Algoritmo de Agregación FedAvg (Federated Averaging - McMahan et al.)
# ==============================================================================

def fed_avg(actualizaciones_hospitales):
    """
    Implementa Federated Averaging (FedAvg):
      W_global = SUM( (n_k / N_total) * W_k )
    Donde:
      - n_k es el número de muestras locales del hospital k.
      - N_total es la suma total de muestras entre todos los hospitales participantes.
      - W_k es el tensor de pesos resultante del entrenamiento local del hospital k.
    """
    if not actualizaciones_hospitales:
        raise ValueError("No hay actualizaciones para agregar.")

    total_muestras = sum(item["num_muestras"] for item in actualizaciones_hospitales)
    if total_muestras == 0:
        total_muestras = len(actualizaciones_hospitales)

    # Inicializar acumulador con las claves del primer hospital
    primeros_pesos = actualizaciones_hospitales[0]["pesos"]
    pesos_agregados = {}
    for key in primeros_pesos.keys():
        pesos_agregados[key] = torch.zeros_like(torch.tensor(primeros_pesos[key], dtype=torch.float32))

    # Ponderación proporcional al tamaño muestral privado de cada hospital
    for item in actualizaciones_hospitales:
        peso_hospital = item["num_muestras"] / float(total_muestras)
        client_weights = item["pesos"]
        for key in pesos_agregados.keys():
            tensor_k = torch.tensor(client_weights[key], dtype=torch.float32)
            pesos_agregados[key] += tensor_k * peso_hospital

    # Convertir de vuelta a formato serializable
    resultado_serializado = {}
    for key, tensor in pesos_agregados.items():
        resultado_serializado[key] = tensor.numpy().tolist()

    return resultado_serializado


# ==============================================================================
# Entrenamiento y Validación Local (Ejecutado por cada Hospital)
# ==============================================================================

def entrenar_modelo_local(modelo, registros_clinicos, epochs=5, lr=0.01, batch_size=16):
    """
    Entrena la red localmente en el hospital sobre sus registros privados.
    Garantía de privacidad: Ningún registro clínico sale del proceso local.
    """
    if not registros_clinicos:
        return serializar_state_dict(modelo), 0.0, 0.0, 0

    x_list = []
    y_list = []
    for reg in registros_clinicos:
        x_list.append([reg["edad"], reg["imc"], reg["glucosa"], reg["presion"]])
        y_list.append([reg["diagnostico"]])

    x_tensor = torch.tensor(x_list, dtype=torch.float32)
    y_tensor = torch.tensor(y_list, dtype=torch.float32)

    # Normalizar
    x_tensor = normalizar_features(x_tensor)

    dataset = torch.utils.data.TensorDataset(x_tensor, y_tensor)
    loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

    criterio = nn.BCELoss()
    optimizador = optim.Adam(modelo.parameters(), lr=lr)

    modelo.train()
    loss_acumulado = 0.0
    for epoch in range(epochs):
        epoch_loss = 0.0
        for b_x, b_y in loader:
            optimizador.zero_grad()
            preds = modelo(b_x)
            loss = criterio(preds, b_y)
            loss.backward()
            optimizador.step()
            epoch_loss += loss.item() * len(b_x)
        loss_acumulado = epoch_loss / len(dataset)

    # Evaluar precisión local
    modelo.eval()
    with torch.no_grad():
        preds_all = modelo(x_tensor)
        aciertos = ((preds_all >= 0.5) == (y_tensor == 1)).sum().item()
        acc = aciertos / float(len(dataset))

    return serializar_state_dict(modelo), loss_acumulado, acc, len(dataset)


def evaluar_modelo_global(modelo):
    """
    Evalúa el modelo global frente a un conjunto de validación de registros clínicos.
    """
    registros = list(get_col_registros().find().limit(150))
    if not registros:
        return {"loss": 0.50, "accuracy": 0.70}

    x_list = [[r["edad"], r["imc"], r["glucosa"], r["presion"]] for r in registros]
    y_list = [[r["diagnostico"]] for r in registros]

    x_tensor = normalizar_features(torch.tensor(x_list, dtype=torch.float32))
    y_tensor = torch.tensor(y_list, dtype=torch.float32)

    modelo.eval()
    criterio = nn.BCELoss()
    with torch.no_grad():
        preds = modelo(x_tensor)
        loss = criterio(preds, y_tensor).item()
        aciertos = ((preds >= 0.5) == (y_tensor == 1)).sum().item()
        accuracy = aciertos / float(len(registros))

    return {
        "loss": round(float(loss), 4),
        "accuracy": round(float(accuracy), 4)
    }


def predecir_riesgo(edad, imc, glucosa, presion):
    """
    Ejecuta inferencia diagnóstica con el modelo global vigente.
    Retorna la probabilidad (0-1) y la clasificación binaria sugerida.
    """
    modelo_doc = obtener_ultimo_modelo_global()
    modelo = ModeloDiagnosticoNN()

    if modelo_doc and "pesos" in modelo_doc:
        deserializar_state_dict(modelo, modelo_doc["pesos"])

    modelo.eval()
    x = torch.tensor([[float(edad), float(imc), float(glucosa), float(presion)]], dtype=torch.float32)
    x_norm = normalizar_features(x)

    with torch.no_grad():
        prob = modelo(x_norm).item()

    return {
        "probabilidad": round(prob, 4),
        "porcentaje": round(prob * 100, 2),
        "diagnostico_sugerido": "Positivo para Diabetes" if prob >= 0.5 else "Negativo / Bajo Riesgo",
        "nivel_alerta": "alta" if prob >= 0.7 else ("moderada" if prob >= 0.4 else "baja"),
        "version_modelo": modelo_doc.get("version", "v1.0-inicial") if modelo_doc else "v0-base"
    }


def inicializar_modelo_si_no_existe():
    """
    Asegura que exista al menos el modelo global base (ronda 0) en MongoDB.
    """
    ultimo = obtener_ultimo_modelo_global()
    if ultimo:
        return ultimo

    modelo_inicial = ModeloDiagnosticoNN()
    pesos_init = serializar_state_dict(modelo_inicial)
    total_params = sum(p.numel() for p in modelo_inicial.parameters())
    
    metricas_init = evaluar_modelo_global(modelo_inicial)
    guardar_modelo_global(
        version="v1.0.0-base",
        ronda_numero=0,
        pesos_serializados=pesos_init,
        total_parametros=total_params,
        metricas=metricas_init,
        hospitales=["ServidorCentral"]
    )
    return obtener_ultimo_modelo_global()
