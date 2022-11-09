# La clase `Model` se hace cargo de los atributos a nivel del modelo, maneja
# los agentes.
# Cada modelo puede contener múltiples agentes y todos ellos son instancias de
# la clase `Agent`.
from mesa import Agent, Model

# Debido a que necesitamos un solo agente por celda elegimos `SingleGrid` que
# fuerza un solo objeto por celda.
from mesa.space import MultiGrid

# Con `SimultaneousActivation` hacemos que todos los agentes se activen de
# manera simultanea.

from mesa.time import SimultaneousActivation
import numpy as np
from mesa.datacollection import DataCollector


class RobotLimpiezaAgent(Agent):
    '''
    Representa a un agente o una celda con estado vivo (1) o muerto (0)
    '''
    def __init__(self, uniqueID, model):
        '''
        Crea un agente con estado inicial aleatorio de 0 o 1, también se le
        asigna un identificador formado por una tupla (x,y).
        También se define un nuevo estado cuyo valor será definido por las
        reglas mencionadas arriba.
        '''
        super().__init__(uniqueID, model)
        self.tipo = 1
        self.movimientos = 0
        self.suciedad = self.model.numSuciedad

    def move(self):
        possibleSteps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False)
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        limpia = False
        if len(cellmates) != 0:
            for i in cellmates:
                if i.tipo == 0:
                    i.tipo = 3
                    limpia = True
                    self.model.numSuciedad -= 1
        if len(cellmates) == 0 or limpia is False:
            newPosition = self.random.choice(possibleSteps)
            cellmatesNewp = self.model.grid.get_cell_list_contents([newPosition])
            if len(cellmatesNewp) == 1:
                if cellmatesNewp[0].tipo != 1:
                    self.model.grid.move_agent(self, newPosition)
                    self.movimientos += 1
            elif len(cellmatesNewp) == 0:
                self.model.grid.move_agent(self, newPosition)
                self.movimientos += 1

    def step(self):
        self.move()


class SuciedadAgent(Agent):
    '''
    Representa a un agente o una celda sucia
    '''
    def __init__(self, uniqueID, model):
        super().__init__(uniqueID, model)
        self.tipo = 0


class LimpiezaModel(Model):
    '''
    Define el modelo del juego de la vida.
    '''
    def __init__(self, width, height, agents, dirty, steps):
        self.numAgents = agents
        self.width = width
        self.height = height
        self.maxSteps = steps
        self.porcentajeSucias = dirty
        self.numSuciedad = round((width * height) * self.porcentajeSucias)
        self.grid = MultiGrid(width, height, True)
        self.schedule = SimultaneousActivation(self)
        self.running = True  # Para la visualizacion usando navegador
        self.movimientos = 0
        celdas = []
        self.datacollectorR = DataCollector(
            model_reporters={"Total Movements": LimpiezaModel.calculoMovements},
            agent_reporters={}
        )
        self.datacollectorS = DataCollector(
            model_reporters={"Total Dirty": LimpiezaModel.calculoSuciedad},
            agent_reporters={}
        )

        for i in range(self.numAgents):
            a = RobotLimpiezaAgent(i, self)
            self.schedule.add(a)
            self.grid.place_agent(a, (1, 1))

        for (content, x, y) in self.grid.coord_iter():
            celdas.append([x, y])

        for i in range(self.numAgents, (self.numSuciedad + self.numAgents)):
            a = SuciedadAgent(i, self)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            pos = self.random.choice(celdas)
            self.grid.place_agent(a, (pos[0], pos[1]))
            celdas.remove(pos)

    def calculoMovements(model):
        totalMovements = 0
        robots = [agent for agent in model.schedule.agents if agent.tipo == 1]
        movements = [agent.movimientos for agent in robots]
        for x in movements:
            totalMovements += x
        return totalMovements

    def calculoSuciedad(model):
        suciedad = [agent for agent in model.schedule.agents if agent.tipo == 0]
        return len(suciedad)

    def step(self):
        if self.maxSteps > 0 and self.porcentajeSucias > 0:
            self.schedule.step()
            self.porcentajeSucias = (100 * self.numSuciedad) // (self.width * self.height)
            print(self.movimientos)
            print(self.porcentajeSucias)
            self.maxSteps -= 1
        self.datacollectorR.collect(self)
        self.datacollectorS.collect(self)
