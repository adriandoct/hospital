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
    obtener_registros_por_hospital
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

# Inicialización segura en arranque
sembrar_registros_clinicos_si_vacio()
inicializar_modelo_si_no_existe()


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
    modelo_actual = obtener_ultimo_modelo_global()
    ronda_actual = obtener_o_crear_ronda_activa()
    historial = obtener_historial_modelos()
    hospitales = Hospital.objects.all().order_by('codigo')
    resumen_registros = obtener_total_registros_resumen()

    # Formatear datos de historial para Chart.js
    labels_grafica = [f"Ronda {h.get('ronda_numero', 0)}" for h in historial]
    acc_grafica = [h.get('metricas', {}).get('accuracy', 0) * 100 for h in historial]
    loss_grafica = [h.get('metricas', {}).get('loss', 0) for h in historial]

    context = {
        "medico": request.user,
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
    modelo = obtener_ultimo_modelo_global()
    if not modelo:
        modelo = inicializar_modelo_si_no_existe()

    ronda = obtener_o_crear_ronda_activa()

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

    modelo_global_doc = obtener_ultimo_modelo_global()
    modelo_base = ModeloDiagnosticoNN()
    if modelo_global_doc and "pesos" in modelo_global_doc:
        deserializar_state_dict(modelo_base, modelo_global_doc["pesos"])

    hospitales_objs = Hospital.objects.filter(codigo__in=["HospitalA", "HospitalB", "HospitalC"])
    reporte_hospitales = []

    ronda = obtener_o_crear_ronda_activa()
    ronda_num = ronda["ronda_numero"]

    for hosp in hospitales_objs:
        registros = obtener_registros_por_hospital(hosp.codigo)
        # Clonar modelo para entrenamiento local privado
        import copy
        modelo_local = copy.deepcopy(modelo_base)
        pesos_actualizados, loss_loc, acc_loc, n_muestras = entrenar_modelo_local(
            modelo=modelo_local,
            registros_clinicos=registros,
            epochs=3,
            lr=0.015
        )
        
        # Registrar en MongoDB
        registrar_actualizacion_hospital(
            ronda_numero=ronda_num,
            hospital_codigo=hosp.codigo,
            pesos=pesos_actualizados,
            num_muestras=n_muestras,
            loss_local=loss_loc,
            acc_local=acc_loc
        )

        reporte_hospitales.append({
            "hospital": hosp.codigo,
            "muestras_privadas": n_muestras,
            "loss_local": round(loss_loc, 4),
            "acc_local": round(acc_loc, 4)
        })

    # Cerrar ronda y agregar con FedAvg
    ronda_cerrada = obtener_o_crear_ronda_activa()
    actualizaciones = ronda_cerrada.get("actualizaciones", {})
    esperados = ["HospitalA", "HospitalB", "HospitalC"]

    lista_updates = [actualizaciones[h] for h in esperados if h in actualizaciones]
    pesos_agregados = fed_avg(lista_updates)

    # Evaluar modelo global nuevo
    nuevo_global = ModeloDiagnosticoNN()
    deserializar_state_dict(nuevo_global, pesos_agregados)
    metricas = evaluar_modelo_global(nuevo_global)

    nueva_version = f"v{ronda_num + 1}.0-fedavg"
    guardar_modelo_global(
        version=nueva_version,
        ronda_numero=ronda_num,
        pesos_serializados=pesos_agregados,
        total_parametros=sum(p.numel() for p in nuevo_global.parameters()),
        metricas=metricas,
        hospitales=esperados
    )
    cerrar_ronda(ronda_num, nueva_version)

    return JsonResponse({
        "status": "ok",
        "mensaje": f"Ronda {ronda_num} completada exitosamente mediante FedAvg",
        "reporte_hospitales": reporte_hospitales,
        "nuevo_modelo": {
            "version": nueva_version,
            "metricas": metricas
        }
    })
