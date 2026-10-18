"""
Genera una infografía gráfica de alta calidad de la red neuronal y el ciclo de vida
para incrustar en el documento Word pedagógico para estudiantes.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(12, 7.5), facecolor='#0f172a')
ax.set_facecolor('#0f172a')
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Título de la infografía
ax.text(50, 95, "ARQUITECTURA DE LA RED NEURONAL MULTICAPA (MLP)", 
        color="#38bdf8", fontsize=15, fontweight='bold', ha='center', va='center')
ax.text(50, 91, "Diagnóstico Clínico de Diabetes · [Linear(4,32)→ReLU→Linear(32,32)→ReLU→Linear(32,1)→Sigmoid]", 
        color="#94a3b8", fontsize=9.5, ha='center', va='center')

# Función para dibujar cajas de capas
def draw_layer_box(x, y, w, h, title, subtitle, color, border_color):
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5,rounding_size=1.2",
                                  edgecolor=border_color, facecolor=color, linewidth=2, zorder=2)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h - 4, title, ha='center', va='center',
            color='#ffffff', fontsize=11, fontweight='bold', zorder=3)
    ax.text(x + w/2, y + h - 8, subtitle, ha='center', va='center',
            color=border_color, fontsize=8.5, fontweight='bold', zorder=3)

# 1. Capa de Entrada (4 neuronas)
draw_layer_box(4, 25, 20, 58, "Capa de Entrada", "4 Biomarcadores (X)", "#1e293b", "#38bdf8")
entradas = [
    ("x₁: Edad", "años", 68),
    ("x₂: IMC", "kg/m²", 55),
    ("x₃: Glucosa", "mg/dL", 42),
    ("x₄: Presión", "mm Hg", 29)
]
for nombre, unidad, y_pos in entradas:
    circ = patches.Circle((9, y_pos), 2.2, edgecolor="#38bdf8", facecolor="#0284c7", zorder=4)
    ax.add_patch(circ)
    ax.text(12.5, y_pos + 0.5, nombre, color="#f8fafc", fontsize=9.5, fontweight='bold', zorder=4)
    ax.text(12.5, y_pos - 2.2, f"({unidad})", color="#94a3b8", fontsize=8, zorder=4)

# 2. Capa Oculta 1 (32 neuronas)
draw_layer_box(29, 25, 20, 58, "Capa Oculta 1", "Linear(4, 32) + ReLU", "#1e293b", "#10b981")
ax.text(39, 68, "32 Neuronas", color="#10b981", fontsize=10, fontweight='bold', ha='center', zorder=4)
for i, y_c in enumerate([60, 54, 48, 38, 32]):
    circ = patches.Circle((39, y_c), 2.0, edgecolor="#10b981", facecolor="#065f46", zorder=4)
    ax.add_patch(circ)
ax.text(39, 43, "• • •", color="#10b981", fontsize=14, ha='center', va='center', zorder=4)
ax.text(39, 27, "f(z) = max(0, z)", color="#a7f3d0", fontsize=8, ha='center', zorder=4)

# 3. Capa Oculta 2 (32 neuronas)
draw_layer_box(54, 25, 20, 58, "Capa Oculta 2", "Linear(32, 32) + ReLU", "#1e293b", "#a855f7")
ax.text(64, 68, "32 Neuronas", color="#c084fc", fontsize=10, fontweight='bold', ha='center', zorder=4)
for i, y_c in enumerate([60, 54, 48, 38, 32]):
    circ = patches.Circle((64, y_c), 2.0, edgecolor="#a855f7", facecolor="#581c87", zorder=4)
    ax.add_patch(circ)
ax.text(64, 43, "• • •", color="#c084fc", fontsize=14, ha='center', va='center', zorder=4)
ax.text(64, 27, "Extracción Abstracta", color="#e9d5ff", fontsize=8, ha='center', zorder=4)

# 4. Capa de Salida (1 neurona Sigmoide)
draw_layer_box(79, 25, 18, 58, "Capa de Salida", "Linear(32, 1) + Sigmoid", "#1e293b", "#f59e0b")
circ_out = patches.Circle((88, 55), 3.5, edgecolor="#f59e0b", facecolor="#b45309", zorder=4)
ax.add_patch(circ_out)
ax.text(88, 55, "σ(z)", color="#ffffff", fontsize=11, fontweight='bold', ha='center', va='center', zorder=5)

ax.text(88, 44, "Probabilidad", color="#fbbf24", fontsize=10, fontweight='bold', ha='center', zorder=4)
ax.text(88, 39, "ŷ ∈ [0.0 , 1.0]", color="#ffffff", fontsize=9, ha='center', zorder=4)
ax.text(88, 32, "ŷ ≥ 0.5 → Diabético\nŷ < 0.5 → Normal", color="#94a3b8", fontsize=7.8, ha='center', zorder=4)

# Flechas de conexión entre capas (Forward Pass)
ax.annotate("", xy=(29, 55), xytext=(24, 55),
            arrowprops=dict(arrowstyle="->", color="#38bdf8", lw=2))
ax.annotate("", xy=(54, 55), xytext=(49, 55),
            arrowprops=dict(arrowstyle="->", color="#10b981", lw=2))
ax.annotate("", xy=(79, 55), xytext=(74, 55),
            arrowprops=dict(arrowstyle="->", color="#a855f7", lw=2))

# Bloque inferior: Ciclo de Entrenamiento
rect_train = patches.FancyBboxPatch((4, 4), 93, 16, boxstyle="round,pad=0.5,rounding_size=1",
                                    edgecolor="#475569", facecolor="#131b2e", linewidth=1.5, zorder=2)
ax.add_patch(rect_train)

ax.text(6, 15.5, "CICLO DE APRENDIZAJE EN EL HOSPITAL (PYTORCH):", color="#f8fafc", fontsize=9.5, fontweight='bold', zorder=3)
ax.text(6, 11.5, "1. Forward Pass: Inferencia del paciente ŷ", color="#38bdf8", fontsize=8.5, zorder=3)
ax.text(6, 7.5, "2. BCE Loss: L = -[y·log(ŷ) + (1-y)·log(1-ŷ)]", color="#f59e0b", fontsize=8.5, zorder=3)

ax.text(52, 11.5, "3. Backpropagation: Regla de la cadena ∂L/∂W", color="#ec4899", fontsize=8.5, zorder=3)
ax.text(52, 7.5, "4. Optimizador Adam: W = W - η·grad (Actualiza pesos locales)", color="#10b981", fontsize=8.5, zorder=3)

output_path = r"c:\Users\Dell Latitude i7 8th\Documents\hospital\diagrama_red_neuronal.png"
plt.tight_layout()
plt.savefig(output_path, dpi=300, facecolor='#0f172a', edgecolor='none')
print(f"Diagrama de red neuronal guardado en: {output_path}")
