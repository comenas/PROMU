import sys
from core.matemáticas import Mat_obj1_AD, Mat_obj7_Puntos, Mat_obj8_Altura
from core.data_loader import validate_file_exists, validate_file_extension
from core.formatter import format_results

def get_arguments():
    """
    Lee sys.argv y devuelve (ruta_fichero, peso_kg).
    Lanza SystemExit si faltan argumentos.
    """
    if len(sys.argv) < 3:          
        print("Uso: python cli.py <fichero.xlsx> <peso_kg>")
        sys.exit(1)                # código de error

    ruta = sys.argv[1]           
    peso = float(sys.argv[2 ])      

    return ruta, peso

def run():
    ruta, peso = get_arguments()

    # 1. Validar fichero
    validate_file_exists(ruta)
    validate_file_extension(ruta)

    # 2. Cargar datos
    tiempo, ace_x, ace_y, ace_z, ace = Mat_obj1_AD(ruta)

    # 3. Calcular resultados
    idx_T0, idx_L, t_aire, velocidad = Mat_obj7_Puntos(ace, tiempo)
    h1, h2, h3 = Mat_obj8_Altura(ace, tiempo)

    # 4. Formatear y mostrar
    resultados = {
        "altura_vuelo": h1,
        "altura_velocidad": h2,
        "altura_desplazamiento": h3,
        "tiempo_vuelo": t_aire,
        "velocidad_despegue": velocidad[idx_T0],
    }
    formateados = format_results(resultados)
    
    for clave, valor in formateados.items():
        print(f"{clave}: {valor}")

if __name__ == "__main__":
    run()