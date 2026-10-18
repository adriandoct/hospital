"""
Generador de diagrama gráfico UML idéntico a la especificación para incrustar en el documento Word.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(13, 9), facecolor='#0b1120')
ax.set_facecolor('#0b1120')
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Paleta
c_server_border = '#f59e0b'
c_server_bg = '#1e1e2d'
c_client_a_border = '#10b981'
c_client_b_border = '#38bdf8'
c_client_c_border = '#a855f7'
c_auth_border = '#f43f5e'
c_entity_border = '#0284c7'
c_model_border = '#d97706'
c_card_bg = '#131b2e'
text_color = '#f1f5f9'
text_muted = '#94a3b8'

def draw_uml_class(ax, x, y, w, h, stereotype, title, attrs, methods, border_color, bg_color=c_card_bg):
    # Caja principal
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5,rounding_size=1.2",
                                  edgecolor=border_color, facecolor=bg_color, linewidth=2, zorder=2)
    ax.add_patch(rect)
    
    # Encabezado
    ax.text(x + w/2, y + h - 2.8, f"«{stereotype}»", ha='center', va='center',
            color=border_color, fontsize=9.5, fontweight='bold', family='sans-serif', zorder=3)
    ax.text(x + w/2, y + h - 5.8, title, ha='center', va='center',
            color=text_color, fontsize=12, fontweight='bold', family='sans-serif', zorder=3)
    
    # Línea separadora encabezado
    ax.plot([x + 0.8, x + w - 0.8], [y + h - 7.5, y + h - 7.5], color=border_color, linewidth=0.8, alpha=0.6, zorder=3)
    
    # Atributos
    curr_y = y + h - 10.5
    for a in attrs:
        ax.text(x + 1.8, curr_y, a, ha='left', va='center',
                color='#e2e8f0', fontsize=9.2, family='monospace', zorder=3)
        curr_y -= 2.6
        
    # Línea separadora métodos
    if methods:
        ax.plot([x + 0.8, x + w - 0.8], [curr_y - 0.6, curr_y - 0.6], color=border_color, linewidth=0.8, alpha=0.6, zorder=3)
        curr_y -= 3.0
        for m in methods:
            ax.text(x + 1.8, curr_y, m, ha='left', va='center',
                    color='#38bdf8', fontsize=9.2, family='monospace', zorder=3)
            curr_y -= 2.6

# 1. Servidor Central (Superior)
draw_uml_class(ax, 32, 70, 36, 25,
               "server", "ServidorFederadoSalud",
               ["+ ronda_actual: RondaFederada", "+ modelo_global: ModeloDiagnostico"],
               ["+ agregar_ronda(): FedAvg", "+ entregar_modelo(): pesos"],
               c_server_border, bg_color='#1c1917')

# 2. Clientes Hospitalarios (Capa Media)
draw_uml_class(ax, 4, 38, 28, 23,
               "client", "HospitalA",
               ["+ api_key: String", "+ registros: RegistroClinico[]"],
               ["+ entrenar_local()", "+ enviar_pesos()"],
               c_client_a_border)

draw_uml_class(ax, 36, 38, 28, 23,
               "client", "HospitalB",
               ["+ api_key: String", "+ registros: RegistroClinico[]"],
               ["+ entrenar_local()", "+ enviar_pesos()"],
               c_client_b_border)

draw_uml_class(ax, 68, 38, 28, 23,
               "client", "HospitalC",
               ["+ api_key: String", "+ registros: RegistroClinico[]"],
               ["+ entrenar_local()", "+ enviar_pesos()"],
               c_client_c_border)

# 3. Clases de Soporte (Inferior)
draw_uml_class(ax, 4, 6, 28, 23,
               "auth", "Medico (AbstractUser)",
               ["+ hospital: Hospital", "+ cedula, especialidad"],
               ["+ login() / logout()"],
               c_auth_border)

draw_uml_class(ax, 36, 6, 28, 23,
               "entity", "RegistroClinico",
               ["+ edad, imc, glucosa", "+ presion", "+ diagnostico: 0|1"],
               [],
               c_entity_border)

draw_uml_class(ax, 68, 6, 28, 23,
               "model", "ModeloDiagnosticoNN",
               ["+ Linear(4,32) → ReLU", "+ Linear(32,32) → ReLU", "+ Linear(32,1) → Sigmoid"],
               [],
               c_model_border)

# Flechas y Conectores
# Servidor coordina con Hospitales
ax.annotate("", xy=(18, 61.5), xytext=(44, 70),
            arrowprops=dict(arrowstyle="-|>", color="#94a3b8", lw=1.5, ls="--"))
ax.annotate("", xy=(50, 61.5), xytext=(50, 70),
            arrowprops=dict(arrowstyle="-|>", color="#94a3b8", lw=1.5, ls="--"))
ax.annotate("", xy=(82, 61.5), xytext=(56, 70),
            arrowprops=dict(arrowstyle="-|>", color="#94a3b8", lw=1.5, ls="--"))

ax.text(50, 65.5, "1..* coordina", color="#fbbf24", fontsize=10, fontweight='bold', ha='center', va='center')

# Hospitales a entidades inferiores
ax.annotate("", xy=(18, 29.5), xytext=(18, 38),
            arrowprops=dict(arrowstyle="->", color="#94a3b8", lw=1.2))
ax.annotate("", xy=(50, 29.5), xytext=(50, 38),
            arrowprops=dict(arrowstyle="->", color="#94a3b8", lw=1.2))
ax.annotate("", xy=(82, 29.5), xytext=(82, 38),
            arrowprops=dict(arrowstyle="->", color="#94a3b8", lw=1.2))

plt.tight_layout()
output_path = r"c:\Users\Dell Latitude i7 8th\Documents\hospital\diagrama_uml.png"
plt.savefig(output_path, dpi=300, facecolor='#0b1120', edgecolor='none')
print(f"Diagrama UML guardado en: {output_path}")
