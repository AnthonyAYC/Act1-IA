from mesa import Model
from agents import AgentBDI, AgentRS, AgentBE, ContinuousObstacle, Resources, Base, AgentCoop, AgentBO
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
            entity = entity_type((x, y), model, random.choice([10,20,50]))
        elif entity_type is ContinuousObstacle:
            entity = entity_type((x, y), model)
        else:
            entity = entity_type((x, y), model)
            agent_point = AgentsPoints(entity_type)
            if not(any(agent.agent_type == agent_point.agent_type for agent in model.array_points)):
                model.array_points.append(agent_point)
        model.grid.place_agent(entity,entity.pos)

class AgentsPoints:
    def __init__(self, agent_type):
        self.agent_type = agent_type
        self.point = 0

#Classe modelo do MESA.
class ModelIA(Model):

    #Tamanho do GRID
    def __init__(self, width=25, height=25):
        super().__init__()
        self.width = width
        self.height = height
        self.grid = MultiGrid(width, height, torus=True)
        self.base_size = 3
        self.array_points = []
        self.pos_resources = []
        self.anc_resources = []
        #Definir quantidades de cada entidade!
        place_base(self, self.base_size)

        place_entities_random(self, 15, ContinuousObstacle)
        place_entities_random(self, 30, Resources)
        place_entities_random(self, 2, AgentBDI)
        place_entities_random(self, 2, AgentBE)
        place_entities_random(self, 2, AgentCoop)
        place_entities_random(self, 2, AgentRS)
        place_entities_random(self, 2, AgentBO)


        self.running = True


    #Função do step para visualizar
    #Mesa ajuda a chamar funções de agentes especificos bom demaizi
    def step(self):
        self.agents_by_type[AgentRS].do("step")
        self.agents_by_type[AgentBE].do("check")
        self.agents_by_type[AgentCoop].do("check")
        self.agents_by_type[AgentBDI].do("check")
        self.agents_by_type[AgentBO].do("step")


        for i in self.array_points:
            print("Tipo: {} | Pontos: {}".format(i.agent_type, i.point))

        if self.steps == 100000:
            self.running = False