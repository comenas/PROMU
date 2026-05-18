def format_height(value_m):
    value = f"{value_m * 100:.1f} cm"
    return value

def format_velocity(v):
    velocidad = f"{v:.2f} m/s"
    return velocidad

def format_time(t):
    tiempo = f"{t:.3f} s"
    return tiempo

def format_results(diccionario):
    resultados = {}
    for entrada in diccionario:
        if "altura" in entrada:
            resultados[entrada] = format_height(diccionario[entrada])
        elif "velocidad" in entrada:
            resultados[entrada] = format_velocity(diccionario[entrada])
        elif "tiempo" in entrada:
            resultados[entrada] = format_time(diccionario[entrada])
        else:
            raise ValueError(f"entrada no válida {entrada}")
    return resultados
            