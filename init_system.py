import os
import sys
import django

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'federated_project.settings')
django.setup()

from django.core.management import call_command
from federated_app.models import Hospital, Medico
from federated_app.mongo_db import sembrar_registros_clinicos_si_vacio
from federated_app.neural_network import inicializar_modelo_si_no_existe

def setup_all():
    print("📌 1. Ejecutando migraciones de Django...")
    call_command('makemigrations', 'federated_app', interactive=False)
    call_command('migrate', interactive=False)

    print("\n📌 2. Registrando Hospitales en la Federación...")
    hospitals_data = [
        {"codigo": "HospitalA", "nombre": "Hospital Universitario San Carlos", "api_key": "sec_key_hospital_a_99a8b7c6d5e4f3a2"},
        {"codigo": "HospitalB", "nombre": "Hospital General Santa María", "api_key": "sec_key_hospital_b_11b2c3d4e5f6a7b8"},
        {"codigo": "HospitalC", "nombre": "Clínica Especializada Metropolitana", "api_key": "sec_key_hospital_c_77c8d9e0f1a2b3c4"},
    ]

    hospitales_map = {}
    for h in hospitals_data:
        obj, created = Hospital.objects.get_or_create(
            codigo=h["codigo"],
            defaults={
                "nombre": h["nombre"],
                "api_key": h["api_key"],
                "activo": True
            }
        )
        if not created and obj.api_key != h["api_key"]:
            obj.api_key = h["api_key"]
            obj.save()
        hospitales_map[h["codigo"]] = obj
        print(f"   🏥 {obj.codigo}: {obj.nombre} [API Key: {obj.api_key}]")

    print("\n📌 3. Creando Cuentas de Médicos para Autenticación...")
    medicos_data = [
        {
            "username": "dr_garcia",
            "password": "medico123",
            "first_name": "Alejandro",
            "last_name": "García",
            "email": "dr.garcia@san-carlos.org",
            "hospital": hospitales_map["HospitalA"],
            "cedula": "MED-84920",
            "especialidad": "Endocrinología y Diabetes"
        },
        {
            "username": "dra_rodriguez",
            "password": "medico123",
            "first_name": "Valeria",
            "last_name": "Rodríguez",
            "email": "v.rodriguez@santamaria.org",
            "hospital": hospitales_map["HospitalB"],
            "cedula": "MED-91024",
            "especialidad": "Medicina Interna"
        },
        {
            "username": "dr_santos",
            "password": "medico123",
            "first_name": "Mateo",
            "last_name": "Santos",
            "email": "m.santos@metropolitana.org",
            "hospital": hospitales_map["HospitalC"],
            "cedula": "MED-33819",
            "especialidad": "Diabetología y Nutrición"
        }
    ]

    for m in medicos_data:
        if not Medico.objects.filter(username=m["username"]).exists():
            user = Medico.objects.create_user(
                username=m["username"],
                password=m["password"],
                first_name=m["first_name"],
                last_name=m["last_name"],
                email=m["email"],
                hospital=m["hospital"],
                cedula=m["cedula"],
                especialidad=m["especialidad"]
            )
            print(f"   👨‍⚕️ Médico creado: {user.username} ({user.get_full_name()}) -> {m['hospital'].codigo}")
        else:
            print(f"   ℹ️ Médico ya existe: {m['username']}")

    print("\n📌 4. Inicializando Colecciones en MongoDB (salud_federada)...")
    from federated_app.mongo_db import verificar_conexion_mongo
    ok, msg = verificar_conexion_mongo()
    if ok:
        try:
            sembrar_registros_clinicos_si_vacio()
            modelo = inicializar_modelo_si_no_existe()
            if modelo:
                print(f"   🍃 MongoDB listo con modelo global vigente: {modelo.get('version')} (Ronda #{modelo.get('ronda_numero')})")
            else:
                print("   🍃 MongoDB conectado.")
        except Exception as e:
            print(f"   ⚠️ Error al inicializar colecciones: {e}")
    else:
        print(f"   ⚠️ MongoDB no conectado: {msg}")
        print("   💡 Pasos de solución en Railway / MongoDB Atlas:")
        print("      1. Ve a MongoDB Atlas -> Database Access -> Crea un usuario con rol 'Read and write to any database'.")
        print("      2. En Network Access -> Agrega IP '0.0.0.0/0' (Allow Access from Anywhere).")
        print("      3. En Railway -> Variables -> Corrige MONGO_URI asegurando no dejar los corchetes < > ni comillas:")
        print("         MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority")

    print("\n✅ INICIALIZACIÓN COMPLETADA CON ÉXITO.")

if __name__ == "__main__":
    setup_all()
