import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_excel("salto.xlsx")
tiempo = df.iloc[:, 0].to_numpy(dtype=float)
ace = df.iloc[:, 4].to_numpy(dtype=float)

plt.plot(tiempo, ace)
plt.xlabel("Tiempo (s)")
plt.ylabel("Aceleración (m/s²)")
plt.title("Señal completa")
plt.grid(True)
plt.show()