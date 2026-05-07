from matemáticas import *

def compute_net_acceleration(ace, FM):
    g = Mat_obj5_GR(ace,FM)
    ace_sua = Mat_obj3_Sua(ace, FM)
    ace_neta = ace_sua - g 
    return ace_neta

def compute_velocity(ace_neta,t):
    velocidad = Mat_obj6_Integra(ace_neta, t, 0)
    return velocidad

def compute_displacement(velocidad, t):
    desplazamiento = Mat_obj6_Integra(velocidad, t, 0)
    return desplazamiento

def compute_height_from_fly_time(t_aire):
    h1 = 9.81 * t_aire**2 / 8
    return h1

def compute_height_from_velocity(velocidad, idx_T0):
    h2 = velocidad[idx_T0]**2 / (2 * 9.81)
    return h2

def compute_height_from_displacement(desplazamiento, idx_T0, idx_L):
    h3 = max(desplazamiento[idx_T0:idx_L])
    return h3

def select_best_height(h1,h2,h3):
    return h1
