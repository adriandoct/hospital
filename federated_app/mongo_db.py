import datetime
from django.conf import settings
from pymongo import MongoClient, DESCENDING

_client = None

def get_mongo_client():
    global _client
    if _client is None:
        mongo_uri = getattr(settings, 'MONGO_URI', 'mongodb://localhost:27017/')
        _client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
    return _client

def get_mongo_db():
    client = get_mongo_client()
    db_name = getattr(settings, 'MONGO_DB_NAME', 'salud_federada')
    return client[db_name]

# Colecciones principales
def get_col_registros():
    return get_mongo_db()['registros_clinicos']

def get_col_modelos():
    return get_mongo_db()['modelos_globales']

def get_col_rondas():
    return get_mongo_db()['rondas_federadas']


def encode_mongo_keys(d):
    """Reemplaza caracteres reservados de MongoDB como '.' por '__dot__'"""
    if isinstance(d, dict):
        return {k.replace('.', '__dot__'): encode_mongo_keys(v) for k, v in d.items()}
    return d

def decode_mongo_keys(d):
    """Restaura los '.' originales de los nombres de capas de PyTorch"""
    if isinstance(d, dict):
        return {k.replace('__dot__', '.'): decode_mongo_keys(v) for k, v in d.items()}
    return d

# ==============================================================================
# Operaciones de Modelos Globales
# ==============================================================================

def guardar_modelo_global(version, ronda_numero, pesos_serializados, total_parametros, metricas, hospitales):
    """
    Persiste en MongoDB el nuevo modelo global agregado resultante de FedAvg.
    """
    col = get_col_modelos()
    doc = {
        "version": version,
        "ronda_numero": int(ronda_numero),
        "pesos": encode_mongo_keys(pesos_serializados),
        "total_parametros": int(total_parametros),
        "metricas": metricas,  # e.g. {"loss": 0.32, "accuracy": 0.88}
        "hospitales_contribuyentes": list(hospitales),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    result = col.insert_one(doc)
    return result.inserted_id

def obtener_ultimo_modelo_global():
    """
    Recupera el modelo global vigente más reciente para ser descargado por los hospitales.
    """
    col = get_col_modelos()
    modelo = col.find_one(sort=[("ronda_numero", DESCENDING), ("_id", DESCENDING)])
    if modelo:
        if "_id" in modelo:
            modelo["_id"] = str(modelo["_id"])
        if "pesos" in modelo:
            modelo["pesos"] = decode_mongo_keys(modelo["pesos"])
    return modelo


def obtener_historial_modelos(limite=15):
    """
    Obtiene el historial cronológico de modelos globales para trazar gráficos en el dashboard médico.
    """
    col = get_col_modelos()
    docs = list(col.find({}, {"pesos": 0}).sort("ronda_numero", 1).limit(limite))
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs


# ==============================================================================
# Operaciones de Rondas Federadas
# ==============================================================================

def obtener_o_crear_ronda_activa():
    """
    Retorna la ronda federada actual en estado 'en_espera' o 'recibiendo'.
    Si no existe o la última ya fue cerrada con FedAvg, crea la siguiente ronda.
    """
    col = get_col_rondas()
    ronda = col.find_one({"estado": "recibiendo"})
    if not ronda:
        # Calcular siguiente número de ronda
        ultima = col.find_one(sort=[("ronda_numero", DESCENDING)])
        siguiente_num = (ultima["ronda_numero"] + 1) if ultima else 1
        
        doc = {
            "ronda_numero": siguiente_num,
            "estado": "recibiendo",
            "hospitales_esperados": ["HospitalA", "HospitalB", "HospitalC"],
            "actualizaciones": {},  # hospital_codigo -> {pesos, num_muestras, loss}
            "fecha_inicio": datetime.datetime.utcnow().isoformat(),
            "fecha_cierre": None
        }
        col.insert_one(doc)
        ronda = col.find_one({"ronda_numero": siguiente_num})

    if ronda and "_id" in ronda:
        ronda["_id"] = str(ronda["_id"])
        if "actualizaciones" in ronda:
            for h, upd in ronda["actualizaciones"].items():
                if "pesos" in upd:
                    upd["pesos"] = decode_mongo_keys(upd["pesos"])
    return ronda

def registrar_actualizacion_hospital(ronda_numero, hospital_codigo, pesos, num_muestras, loss_local, acc_local=None):
    """
    Registra en MongoDB la actualización de pesos enviada por un hospital para la ronda especificada.
    """
    col = get_col_rondas()
    key_path = f"actualizaciones.{hospital_codigo}"
    update_data = {
        "pesos": encode_mongo_keys(pesos),
        "num_muestras": int(num_muestras),
        "loss_local": float(loss_local),
        "acc_local": float(acc_local) if acc_local is not None else None,
        "recibido_en": datetime.datetime.utcnow().isoformat()
    }
    col.update_one(
        {"ronda_numero": int(ronda_numero), "estado": "recibiendo"},
        {"$set": {key_path: update_data}}
    )
    ronda_actualizada = col.find_one({"ronda_numero": int(ronda_numero)})
    if ronda_actualizada and "actualizaciones" in ronda_actualizada:
        for h, upd in ronda_actualizada["actualizaciones"].items():
            if "pesos" in upd:
                upd["pesos"] = decode_mongo_keys(upd["pesos"])
    return ronda_actualizada

def cerrar_ronda(ronda_numero, nuevo_modelo_version):
    """
    Marca la ronda federada como 'completada'.
    """
    col = get_col_rondas()
    col.update_one(
        {"ronda_numero": int(ronda_numero)},
        {
            "$set": {
                "estado": "completada",
                "modelo_resultante_version": nuevo_modelo_version,
                "fecha_cierre": datetime.datetime.utcnow().isoformat()
            }
        }
    )


# ==============================================================================
# Almacenamiento Documental de Registros Clínicos Locales
# ==============================================================================

def sembrar_registros_clinicos_si_vacio():
    """
    Puebla la colección de registros clínicos privados para cada hospital
    si la colección está vacía (datos clínicos sintéticos pero realistas para diabetes).
    """
    col = get_col_registros()
    if col.count_documents({}) > 0:
        return

    import random
    random.seed(42)
    registros = []

    hospitales = ["HospitalA", "HospitalB", "HospitalC"]
    # Generar muestras con correlación clínica para diabetes:
    # edad (20-80), imc (18-45), glucosa (70-220), presion (90-180)
    for hosp in hospitales:
        for _ in range(80):
            edad = round(random.uniform(25, 75), 1)
            imc = round(random.uniform(19, 42), 1)
            presion = round(random.uniform(95, 170), 1)
            
            # Riesgo fisiológico correlacionado
            riesgo = (edad * 0.03) + (imc * 0.08) + (presion * 0.02)
            glucosa = round(random.uniform(70, 130) + (riesgo * 15), 1)
            
            # Diagnóstico probabilístico (1: diabético, 0: no diabético)
            score = (glucosa - 110) * 0.04 + (imc - 27) * 0.1 + (edad - 45) * 0.03
            prob = 1.0 / (1.0 + 2.71828 ** (-score))
            diagnostico = 1 if (random.random() < prob or glucosa > 140) else 0

            registros.append({
                "hospital_codigo": hosp,
                "edad": edad,
                "imc": imc,
                "glucosa": glucosa,
                "presion": presion,
                "diagnostico": diagnostico,
                "fecha_registro": datetime.datetime.utcnow().isoformat()
            })

    col.insert_many(registros)

def obtener_registros_por_hospital(hospital_codigo):
    """
    Recupera los registros clínicos pertenecientes a un hospital específico.
    Demuestra que los datos están segregados por entidad clínica.
    """
    col = get_col_registros()
    return list(col.find({"hospital_codigo": hospital_codigo}))

def obtener_total_registros_resumen():
    """
    Resumen de datos clínicos custodiados por hospital para el dashboard.
    """
    col = get_col_registros()
    pipeline = [
        {"$group": {"_id": "$hospital_codigo", "total": {"$sum": 1}, "positivos": {"$sum": "$diagnostico"}}}
    ]
    return list(col.aggregate(pipeline))
