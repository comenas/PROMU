from core.matemáticas import *
import matplotlib.pyplot as plt

def Grafica_aceleracion(path):
    """
    utilizando los datos de Mat_obj1_AD con matplotlib.pyplot se dibuja la gráfica de aceleración en función del tiempo
    para conseguir la aceleración verdadera se multiplica por el signo de ace_y también de Mat_obj1_AD 
    """
    t,ace_y,ace = Mat_obj1_AD(path)
    ace_real = ace * np.sign(ace_y) 
    plt.plot(t, ace_real)
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Aceleración (m/s²)")
    plt.title("Gráfica de Aceleración vs Tiempo")
    plt.grid()
    plt.show()
    
def Grafica_velocidad(path):
    """
    utilizando los datos de Mat_obj1_AD con matplotlib.pyplot se dibuja la gráfica de velocidad en función del tiempo
    para conseguir la aceleración verdadera se multiplica por el signo de ace_y también de Mat_obj1_AD 
    y luego se integra para conseguir la velocidad pero al integrar se estropea el signo por lo que se integra la aceleración neta que es la aceleración verdadera menos la gravedad media
    """
    t,ace_y,ace = Mat_obj1_AD(path)
    ace_real = ace * np.sign(ace_y) 
    FM = Mat_obj2_FM(t)
    sua_ace = Mat_obj3_Sua(ace, FM) # datos necesario ace suavizada
    g_media = Mat_obj5_GR(ace, FM) # gravedad media
    ace_neta = sua_ace - g_media  # aceleración neta
    velocidad = Mat_obj6_Integra(ace_neta,t,0) # velocidad 
    plt.plot(t, velocidad)
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Velocidad (m/s)")
    plt.title("Gráfica de Velocidad vs Tiempo")
    plt.grid()
    plt.show()

