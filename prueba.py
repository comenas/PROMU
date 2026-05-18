import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from core.matemáticas import Mat_obj2_FM, Mat_obj3_Sua, Mat_obj5_GR, Mat_obj6_Integra

df = pd.read_excel("salto.xlsx")
tiempo = df.iloc[:, 0].to_numpy(dtype=float)
ace    = df.iloc[:, 4].to_numpy(dtype=float)

FM       = Mat_obj2_FM(tiempo)
sua      = Mat_obj3_Sua(ace, FM)
g        = Mat_obj5_GR(ace, FM)
ace_neta = sua - g
vel      = Mat_obj6_Integra(ace_neta, tiempo, 0)

fig, (ax1, ax2) = plt.subplots(2, 1)
ax1.plot(tiempo, ace_neta)
ax1.set_title("Aceleración neta")
ax2.plot(tiempo, vel)
ax2.set_title("Velocidad")
plt.tight_layout()
plt.show()