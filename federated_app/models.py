from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
import secrets

class Hospital(models.Model):
    """
    Representa una entidad hospitalaria participante en la federación («client»).
    Cada hospital posee su propia clave API secreta para descargar modelos
    y reportar las actualizaciones de pesos calculadas localmente.
    """
    codigo = models.CharField(max_length=50, unique=True, help_text="Ej: HospitalA, HospitalB, HospitalC")
    nombre = models.CharField(max_length=200)
    api_key = models.CharField(max_length=64, unique=True, default=secrets.token_hex)
    ubicacion = models.CharField(max_length=200, blank=True, default="Centro Médico Metropolitano")
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Hospital"
        verbose_name_plural = "Hospitales"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def regenerar_api_key(self):
        self.api_key = secrets.token_hex(32)
        self.save()
        return self.api_key


class Medico(AbstractUser):
    """
    Entidad de autenticación médica («auth» Medico (AbstractUser)).
    Extiende el modelo nativo de usuarios de Django para asociar al médico
    con su hospital de procedencia, cédula profesional y especialidad clínica.
    """
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medicos",
        help_text="Hospital al que pertenece el facultativo médico"
    )
    cedula = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text="Cédula profesional médica"
    )
    especialidad = models.CharField(
        max_length=100,
        default="Endocrinología y Diabetes",
        help_text="Especialidad clínica"
    )

    class Meta:
        verbose_name = "Médico"
        verbose_name_plural = "Médicos"

    def __str__(self):
        return f"Dr(a). {self.get_full_name() or self.username} ({self.especialidad})"


# ==============================================================================
# Modelos documentales lógicos (Entidades persistidas en MongoDB)
# ==============================================================================

class RegistroClinicoDTO:
    """
    Esquema lógico para la entidad «entity» RegistroClinico persistida en MongoDB.
    Los datos privados de pacientes residen de forma distribuida en cada nodo/hospital:
      - edad: años
      - imc: Índice de Masa Corporal (kg/m^2)
      - glucosa: nivel de glucosa en plasma (mg/dL)
      - presion: presión arterial sistólica (mm Hg)
      - diagnostico: 0 (No diabético) | 1 (Diabético)
    """
    def __init__(self, edad, imc, glucosa, presion, diagnostico, hospital_codigo=None):
        self.edad = float(edad)
        self.imc = float(imc)
        self.glucosa = float(glucosa)
        self.presion = float(presion)
        self.diagnostico = int(diagnostico)
        self.hospital_codigo = hospital_codigo

    def to_dict(self):
        return {
            "edad": self.edad,
            "imc": self.imc,
            "glucosa": self.glucosa,
            "presion": self.presion,
            "diagnostico": self.diagnostico,
            "hospital_codigo": self.hospital_codigo
        }

    def to_feature_vector(self):
        return [self.edad, self.imc, self.glucosa, self.presion]
