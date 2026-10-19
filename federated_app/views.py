import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from functools import wraps

from .models import Hospital, Medico
from .mongo_db import (
    obtener_ultimo_modelo_global,
    obtener_historial_modelos,
    obtener_o_crear_ronda_activa,
    registrar_actualizacion_hospital,
    cerrar_ronda,
    guardar_modelo_global,
    sembrar_registros_clinicos_si_vacio,
    obtener_total_registros_resumen,
    obtener_registros_por_hospital,
    verificar_conexion_mongo
)
from .neural_network import (
    ModeloDiagnosticoNN,
    deserializar_state_dict,
    serializar_state_dict,
    fed_avg,
    evaluar_modelo_global,
    predecir_riesgo,
    inicializar_modelo_si_no_existe,
    entrenar_modelo_local
)

# Inicialización segura en arranque tolerante a demoras de red en despliegue
def _inicializar_sistema_en_arranque():
    try:
        ok, msg = verificar_conexion_mongo()
        if ok:
            sembrar_registros_clinicos_si_vacio()
            inicializar_modelo_si_no_existe()
    except Exception:
        pass

_inicializar_sistema_en_arranque()


# ==============================================================================
# Decorador de Autenticación de Hospitales por API Key
# ==============================================================================

def validar_hospital_api_key(view_func):
    """
    Verifica que la petición incluya un header 'X-API-KEY' válido
    correspondiente a un hospital activo registrado en la federación.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        api_key = request.headers.get('X-API-KEY') or request.GET.get('api_key')
        if not api_key:
            return JsonResponse({
                "error": "Autenticación requerida",
                "detalle": "Falta cabecera 'X-API-KEY' o parámetro 'api_key'"
            }, status=401)

        try:
            hospital = Hospital.objects.get(api_key=api_key, activo=True)
            request.hospital = hospital
        except Hospital.DoesNotExist:
            return JsonResponse({
                "error": "Acceso denegado",
                "detalle": "API Key de hospital inválida o revocada"
            }, status=403)

        return view_func(request, *args, **kwargs)
    return _wrapped


# ==============================================================================
# Vistas de Autenticación de Médicos (Django Auth)
# ==============================================================================

def login_view(request):
    """
    Autenticación de médicos con username y password mediante Django Auth.
    GET: Renderiza formulario de inicio de sesión clínico.
    POST: Valida credenciales e inicia sesión.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    error_mensaje = None
    if request.method == 'POST':
        # Soporta tanto envío por Form tradicional como por JSON
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                username = data.get('username')
                password = data.get('password')
            except json.JSONDecodeError:
                return JsonResponse({"error": "JSON malformado"}, status=400)
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if request.content_type == 'application/json':
                return JsonResponse({"status": "ok", "redirect": "/dashboard/"})
            return redirect('dashboard')
        else:
            error_mensaje = "Credenciales médicas inválidas. Verifique usuario y contraseña."
            if request.content_type == 'application/json':
                return JsonResponse({"error": error_mensaje}, status=401)

    return render(request, 'login.html', {"error": error_mensaje})


def logout_view(request):
    """
    Cierra la sesión del facultativo médico y redirige a login.
    """
    logout(request)
    return redirect('login')


# ==============================================================================
# Vista de Dashboard Médico
# ==============================================================================

@login_required
def dashboard_view(request):
    """
    Panel de control clínico protegido para el médico autenticado.
    Muestra:
      - Datos del médico y hospital afiliado.
      - Estado y versión del modelo global vigente.
      - Métricas de aprendizaje federado (Accuracy, BCE Loss).
      - Progreso de la ronda actual y hospitales participantes.
      - Historial de rondas agregadas con FedAvg en MongoDB.
      - Resumen de registros privados protegidos.
    """
    mongo_ok, mongo_msg = verificar_conexion_mongo()

    try:
        modelo_actual = obtener_ultimo_modelo_global() if mongo_ok else None
        if not modelo_actual:
            modelo_actual = {"version": "v1.0.0-base", "ronda_numero": 0, "metricas": {"accuracy": 0.72, "loss": 0.54}}
    except Exception:
        modelo_actual = {"version": "v1.0.0-base", "ronda_numero": 0, "metricas": {"accuracy": 0.72, "loss": 0.54}}

    try:
        ronda_actual = obtener_o_crear_ronda_activa() if mongo_ok else {"ronda_numero": 1, "estado": "recibiendo", "hospitales_esperados": ["HospitalA", "HospitalB", "HospitalC"]}
    except Exception:
        ronda_actual = {"ronda_numero": 1, "estado": "recibiendo", "hospitales_esperados": ["HospitalA", "HospitalB", "HospitalC"]}

    try:
        historial = obtener_historial_modelos() if mongo_ok else []
    except Exception:
        historial = []

    hospitales = Hospital.objects.all().order_by('codigo')

    try:
        resumen_registros = obtener_total_registros_resumen() if mongo_ok else []
    except Exception:
        resumen_registros = []

    # Formatear datos de historial para Chart.js
    labels_grafica = [f"Ronda {h.get('ronda_numero', 0)}" for h in historial]
    acc_grafica = [h.get('metricas', {}).get('accuracy', 0) * 100 for h in historial]
    loss_grafica = [h.get('metricas', {}).get('loss', 0) for h in historial]

    context = {
        "medico": request.user,
        "mongo_conectado": mongo_ok,
        "mongo_error": mongo_msg if not mongo_ok else None,
        "modelo_actual": modelo_actual,
        "ronda_actual": ronda_actual,
        "historial": historial,
        "hospitales": hospitales,
        "resumen_registros": resumen_registros,
        "labels_grafica": json.dumps(labels_grafica),
        "acc_grafica": json.dumps(acc_grafica),
        "loss_grafica": json.dumps(loss_grafica),
    }
    return render(request, 'dashboard.html', context)


# ==============================================================================
# Endpoints de la API Federada (Protegidos con API Key de Hospital)
# ==============================================================================

@validar_hospital_api_key
def api_obtener_modelo(request):
    """
    GET /api/modelo/
    El hospital descarga los pesos del modelo global vigente para entrenar localmente.
    """
    try:
        modelo = obtener_ultimo_modelo_global()
        if not modelo:
            modelo = inicializar_modelo_si_no_existe()
        ronda = obtener_o_crear_ronda_activa()
    except Exception as e:
        return JsonResponse({
            "error": "Error de base de datos en MongoDB",
            "detalle": str(e),
            "sugerencia": "Verifica las credenciales de MONGO_URI en Railway o MongoDB Atlas"
        }, status=503)

    return JsonResponse({
        "status": "ok",
        "hospital_autenticado": request.hospital.codigo,
        "version": modelo.get("version"),
        "ronda_numero": modelo.get("ronda_numero", 0),
        "ronda_activa": ronda.get("ronda_numero", 1),
        "total_parametros": modelo.get("total_parametros"),
        "metricas": modelo.get("metricas", {}),
        "pesos": modelo.get("pesos")
    })


@csrf_exempt
@validar_hospital_api_key
def api_enviar_actualizacion(request):
    """
    POST /api/actualizaciones/
    El hospital envía los pesos actualizados calculados con PyTorch en su nodo privado.
    Si se reciben los pesos de todos los hospitales esperados, se ejecuta FedAvg automáticamente.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest("Método no permitido. Use POST.")

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "JSON no válido"}, status=400)

    pesos = data.get('pesos')
    num_muestras = data.get('num_muestras', 50)
    loss_local = data.get('loss_local', 0.0)
    acc_local = data.get('acc_local', 0.0)

    if not pesos:
        return JsonResponse({"error": "Campo 'pesos' es obligatorio"}, status=400)

    try:
        ronda = obtener_o_crear_ronda_activa()
        ronda_num = ronda["ronda_numero"]
        hosp_cod = request.hospital.codigo

        # Registrar la actualización del hospital en MongoDB
        ronda_actualizada = registrar_actualizacion_hospital(
            ronda_numero=ronda_num,
            hospital_codigo=hosp_cod,
            pesos=pesos,
            num_muestras=num_muestras,
            loss_local=loss_local,
            acc_local=acc_local
        )

        actualizaciones = ronda_actualizada.get("actualizaciones", {})
        esperados = ronda_actualizada.get("hospitales_esperados", ["HospitalA", "HospitalB", "HospitalC"])

        # Verificar si todos los hospitales han reportado en esta ronda
        ronda_completada = False
        nuevo_modelo_info = None

        if all(h in actualizaciones for h in esperados):
            # 1. Preparar lista de actualizaciones para FedAvg
            lista_updates = [actualizaciones[h] for h in esperados]

            # 2. Ejecutar agregación matemática FedAvg
            pesos_agregados = fed_avg(lista_updates)

            # 3. Evaluar el nuevo modelo agregado con PyTorch
            nuevo_modelo = ModeloDiagnosticoNN()
            deserializar_state_dict(nuevo_modelo, pesos_agregados)
            metricas_nuevas = evaluar_modelo_global(nuevo_modelo)

            # 4. Guardar nuevo modelo global en MongoDB
            nueva_version = f"v{ronda_num + 1}.0-fedavg"
            guardar_modelo_global(
                version=nueva_version,
                ronda_numero=ronda_num,
                pesos_serializados=pesos_agregados,
                total_parametros=sum(p.numel() for p in nuevo_modelo.parameters()),
                metricas=metricas_nuevas,
                hospitales=esperados
            )

            # 5. Cerrar la ronda actual
            cerrar_ronda(ronda_num, nueva_version)
            ronda_completada = True

            nuevo_modelo_info = {
                "version": nueva_version,
                "metricas": metricas_nuevas,
                "hospitales_contribuyentes": esperados
            }

        return JsonResponse({
            "status": "ok",
            "mensaje": f"Pesos de {hosp_cod} recibidos exitosamente",
            "ronda_numero": ronda_num,
            "actualizaciones_recibidas": len(actualizaciones),
            "actualizaciones_esperadas": len(esperados),
            "ronda_completada": ronda_completada,
            "nuevo_modelo": nuevo_modelo_info
        })
    except Exception as e:
        return JsonResponse({
            "error": "Error al persistir actualización en MongoDB",
            "detalle": str(e),
            "sugerencia": "Verifica las credenciales de MONGO_URI en Railway"
        }, status=503)


# ==============================================================================
# Endpoint de Inferencia Médica y Diagnóstico
# ==============================================================================

@csrf_exempt
@login_required
def api_diagnosticar(request):
    """
    POST /api/diagnosticar/
    Permite al médico autenticado evaluar un paciente con las 4 variables clínicas:
    edad, imc, glucosa, presion. Infiere con el modelo neuronal global vigente.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest("Método no permitido. Use POST.")

    try:
        data = json.loads(request.body)
        edad = float(data.get('edad'))
        imc = float(data.get('imc'))
        glucosa = float(data.get('glucosa'))
        presion = float(data.get('presion'))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"error": "Parámetros inválidos. Requiere edad, imc, glucosa y presion como números"}, status=400)

    resultado = predecir_riesgo(edad, imc, glucosa, presion)
    return JsonResponse({"status": "ok", "resultado": resultado})


# ==============================================================================
# Endpoint de Simulación Rápida de Ronda Federada (Para Demostración)
# ==============================================================================

def _generar_muestras_sinteticas_reserva(n=50):
    import random
    muestras = []
    for _ in range(n):
        edad = random.uniform(25, 75)
        imc = random.uniform(19, 42)
        presion = random.uniform(95, 170)
        riesgo = (edad * 0.03) + (imc * 0.08) + (presion * 0.02)
        glucosa = random.uniform(70, 130) + (riesgo * 15)
        score = (glucosa - 110) * 0.04 + (imc - 27) * 0.1 + (edad - 45) * 0.03
        prob = 1.0 / (1.0 + 2.71828 ** (-score))
        diag = 1 if (random.random() < prob or glucosa > 140) else 0
        muestras.append({
            "edad": round(edad, 1),
            "imc": round(imc, 1),
            "glucosa": round(glucosa, 1),
            "presion": round(presion, 1),
            "diagnostico": diag
        })
    return muestras


@csrf_exempt
@login_required
def api_simular_ronda(request):
    """
    POST /api/simular-ronda/
    Ejecuta un ciclo federado completo local en el servidor:
      1. Descarga modelo global vigente.
      2. Cada hospital (HospitalA, HospitalB, HospitalC) entrena su MLP localmente con PyTorch sobre sus registros privados.
      3. Se envían los pesos calculados al agregador FedAvg.
      4. Se persiste el nuevo modelo en MongoDB.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest("Método no permitido.")

    try:
        modelo_global_doc = obtener_ultimo_modelo_global()
    except Exception:
        modelo_global_doc = None

    modelo_base = ModeloDiagnosticoNN()
    if modelo_global_doc and "pesos" in modelo_global_doc:
        deserializar_state_dict(modelo_base, modelo_global_doc["pesos"])

    hospitales_objs = Hospital.objects.filter(codigo__in=["HospitalA", "HospitalB", "HospitalC"])
    hospitales_codigos = [h.codigo for h in hospitales_objs] if hospitales_objs.exists() else ["HospitalA", "HospitalB", "HospitalC"]

    try:
        ronda = obtener_o_crear_ronda_activa()
        ronda_num = ronda.get("ronda_numero", 1)
    except Exception:
        ronda_num = 1
        ronda = {"ronda_numero": 1}

    reporte_hospitales = []
    actualizaciones = {}

    for hosp_code in hospitales_codigos:
        try:
            registros = obtener_registros_por_hospital(hosp_code)
        except Exception:
            registros = []
        if not registros:
            registros = _generar_muestras_sinteticas_reserva(50)

        # Clonar modelo para entrenamiento local privado
        import copy
        modelo_local = copy.deepcopy(modelo_base)
        pesos_actualizados, loss_loc, acc_loc, n_muestras = entrenar_modelo_local(
            modelo=modelo_local,
            registros_clinicos=registros,
            epochs=3,
            lr=0.015
        )

        actualizaciones[hosp_code] = {
            "pesos": pesos_actualizados,
            "num_muestras": n_muestras,
            "loss_local": loss_loc,
            "acc_local": acc_loc
        }

        # Intentar registrar en MongoDB
        try:
            registrar_actualizacion_hospital(
                ronda_numero=ronda_num,
                hospital_codigo=hosp_code,
                pesos=pesos_actualizados,
                num_muestras=n_muestras,
                loss_local=loss_loc,
                acc_local=acc_loc
            )
        except Exception:
            pass

        reporte_hospitales.append({
            "hospital": hosp_code,
            "muestras_privadas": n_muestras,
            "loss_local": round(loss_loc, 4),
            "acc_local": round(acc_loc, 4)
        })

    # Cerrar ronda y agregar con FedAvg
    esperados = hospitales_codigos
    lista_updates = [actualizaciones[h] for h in esperados if h in actualizaciones]
    pesos_agregados = fed_avg(lista_updates)

    # Evaluar modelo global nuevo
    nuevo_global = ModeloDiagnosticoNN()
    deserializar_state_dict(nuevo_global, pesos_agregados)
    metricas = evaluar_modelo_global(nuevo_global)

    nueva_version = f"v{ronda_num + 1}.0-fedavg"
    try:
        guardar_modelo_global(
            version=nueva_version,
            ronda_numero=ronda_num,
            pesos_serializados=pesos_agregados,
            total_parametros=sum(p.numel() for p in nuevo_global.parameters()),
            metricas=metricas,
            hospitales=esperados
        )
        cerrar_ronda(ronda_num, nueva_version)
    except Exception:
        pass

    return JsonResponse({
        "status": "ok",
        "mensaje": f"Ronda {ronda_num} completada exitosamente mediante FedAvg",
        "reporte_hospitales": reporte_hospitales,
        "nuevo_modelo": {
            "version": nueva_version,
            "metricas": metricas
        }
    })
