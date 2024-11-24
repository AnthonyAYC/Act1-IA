from mesa import Model
from agents import AgentRS, AgentBE, ContinuousObstacle, Resources
from mesa.space import MultiGrid
import random

#Função para colocar as entidades (agentes, recursos, obstaculos)
#Python é bom demais pra isso
def place_entities(model, num_entities, entity_type):

    for i in range(num_entities):
        x = model.random.randrange(model.grid.width)
        y = model.random.randrange(model.grid.height)
        if entity_type is Resources:
            entity = entity_type((x, y), model, random.choice([10, 20, 50]))
        else:
            entity = entity_type((x, y), model)
        model.grid.place_agent(entity, (x, y))

#Classe modelo do MESA.
class ModelIA(Model):

    #Tamanho do GRID
    def __init__(self, width=25, height=25):
        super().__init__()

        self.grid = MultiGrid(width, height, torus=True)

        #Definir quantidades de cada entidade!
        #place_entities(self, 3, AgentRS)
        place_entities(self, 3, AgentBE)
        place_entities(self, 20, ContinuousObstacle)
        place_entities(self, 8, Resources)

    #Função do step para visualizar
    #Mesa ajuda a chamar funções de agentes especificos bom demaizi
    def step(self):
        #self.agents_by_type[AgentRS].shuffle_do("move")
        self.agents_by_type[AgentBE].shuffle_do("step")