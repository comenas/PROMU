from core.matemáticas import *
import matplotlib.pyplot as plt
import threading


def Graficas_salto(path, peso_kg):
    """
    Genera una figura con 6 subgráficas (2×3):
    Aceleración, Velocidad, Desplazamiento, Fuerza, Potencia, Masa aparente.
    Cada magnitud se calcula a partir del Excel y del peso del sujeto.
    """
    # ── Carga y cálculo ───────────────────────────────────────────────────────
    t, ace_y, ace = Mat_obj1_AD(path)
    FM             = Mat_obj2_FM(t)

    ace_real       = ace * np.sign(ace_y)          # m/s²  (con signo)
    sua_ace        = Mat_obj3_Sua(ace_real, FM)
    g_media        = Mat_obj5_GR(ace_real, FM)
    ace_neta       = sua_ace - g_media              # aceleración neta

    velocidad      = Mat_obj6_Integra(ace_neta, t, 0)          # m/s
    desplazamiento = Mat_obj6_Integra(velocidad,  t, 0)         # m
    fuerza         = peso_kg * ace_real                          # N  (F = m·a)
    potencia       = fuerza  * velocidad                         # W  (P = F·v)
    masa_aparente  = fuerza  / 9.81                              # kg (m = F/g)

    # ── Figura ────────────────────────────────────────────────────────────────
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    fig.patch.set_facecolor('#1a1108')
    fig.suptitle("Análisis del Salto", fontsize=18, fontweight='bold', color='white')

    graficas = [
        (ace_real,       "Aceleración",    "m/s²"),
        (velocidad,      "Velocidad",      "m/s"),
        (desplazamiento, "Desplazamiento", "m"),
        (fuerza,         "Fuerza",         "N"),
        (potencia,       "Potencia",       "W"),
        (masa_aparente,  "Masa",           "kg"),
    ]
    colores = ['#00ff99', '#ff6666', '#6699ff', '#ffcc00', '#ff99cc', '#99ffff']

    for ax, (y, titulo, unidad), color in zip(axes.flatten(), graficas, colores):
        ax.set_facecolor('#2a2118')
        ax.plot(t, y, color=color, linewidth=1.5)
        ax.set_title(titulo, color='white', fontsize=13, fontweight='bold')
        ax.set_xlabel("Tiempo (s)",          color='#aaaaaa', fontsize=10)
        ax.set_ylabel(f"{titulo} ({unidad})", color='#aaaaaa', fontsize=10)
        ax.tick_params(colors='#aaaaaa')
        for spine in ax.spines.values():
            spine.set_color('#555555')
        ax.grid(True, color='#333333', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.show()


def abrir_graficas_en_hilo(path, peso_kg):
    """Lanza Graficas_salto en un hilo separado para no bloquear tkinter."""
    hilo = threading.Thread(target=Graficas_salto, args=(path, peso_kg), daemon=True)
    hilo.start()