"""
Visualizador del Juego de la Vida
Autor: Jorge Rmz Uresti
Octubre 8, 2021
"""
from RobotLimpieza import *
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule


def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "red",
                 "r": 0.5}

    portrayal2 = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "black",
                 "r": 0.3}

    portrayal3 = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "black",
                 "r": 0}
    if agent.tipo == 1:
        return portrayal
    elif agent.tipo == 0:
        return portrayal2
    else:
        return portrayal3


ancho = 10
alto = 10
agentes = 3
porcentaje_sucias = .20
pasos = 100
grid = CanvasGrid(agent_portrayal, ancho, alto, 750, 750)
total_movements_graph = ChartModule([{"Label": "Total Movements", "Color": "Green"}], data_collector_name='datacollectorR')
total_dirty_graph = ChartModule([{"Label": "Total Dirty", "Color": "Red"}], data_collector_name='datacollectorS')
server = ModularServer(LimpiezaModel,
                       [grid, total_movements_graph, total_dirty_graph],
                       "Robot de Limpieza",
                       {"width":ancho, "height":alto, "agents": agentes, "dirty": porcentaje_sucias, "steps": pasos})
server.port = 8521 # The default
server.launch()
