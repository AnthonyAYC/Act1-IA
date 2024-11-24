from mesa import Model
from agents import AgentBDI, AgentRS, ContinuousObstacle, Resources, Base
from mesa.space import MultiGrid
import random

#Função para colocar as entidades (agentes, recursos, obstaculos)
#Python é bom demais pra isso
def place_base(model, size):
    for i in range(size):
        for j in range(size):
            base_spot = Base((i,j), model)
            model.grid.place_agent(base_spot, base_spot.pos)

def place_entities_random(model, num_entities, entity_type):

    for i in range(num_entities):
        while True:
            x = model.random.randrange(model.grid.width)
            y = model.random.randrange(model.grid.height)
            if model.grid.is_cell_empty((x, y)):
                break
        if entity_type is Resources:
            entity = entity_type((x, y), model, random.choice([50]))
        elif entity_type is ContinuousObstacle:
            entity = entity_type((x, y), model)
        else:
            entity = entity_type((x, y), model)
            agent_point = agents_points(entity_type)
            model.array_points.append(agent_point)
        model.grid.place_agent(entity,entity.pos)

class agents_points:
    def __init__(self, agent_type):
        self.agent_type = agent_type
        self.point = 0

#Classe modelo do MESA.
class ModelIA(Model):

    #Tamanho do GRID
    def __init__(self, width=9, height=9):
        super().__init__()

        self.grid = MultiGrid(width, height, torus=True)
        self.array_points = []
        self.pos_resources = []
        #Definir quantidades de cada entidade!
        place_base(self, 2)
        place_entities_random(self, 0, AgentRS)
        place_entities_random(self, 0, ContinuousObstacle)
        place_entities_random(self, 4, Resources)
        place_entities_random(self, 2, AgentBDI)

        self.running = True


    #Função do step para visualizar
    #Mesa ajuda a chamar funções de agentes especificos bom demaizi
    def step(self):
        #self.agents_by_type[AgentRS].do("move")
        self.agents_by_type[AgentBDI].do("check")
        #print(self.array_points[0].point)
        if self.steps == 100000:
            self.running = False
