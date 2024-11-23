from mesa import Agent

#Classe de Obstáculos:
#São agentes simples e imóveis
class ContinuousObstacle(Agent):
    def __init__(self, pos, model):
        super().__init__(model)
        self.pos = pos

#Classe de Recursos
#São agentes simples e imóveis, nesse caso, com valores atribuidos
class Resources(Agent):
    def __init__(self, pos, model, valor):
        super().__init__(model)
        self.pos = pos
        self.valor = valor

#Classe Agente "PAI?"
#Contém os atributos comuns a maioria dos agentes (eu acho :D)
class AgentIA(Agent):
    def __init__(self, pos, model):
        super().__init__(model)
        self.pos = pos
        self.inventory = 0

    #Função de coleta de recursos IMCOMPLETA
    #Cenário faltante: Estruturas antigas exigem 2 agentes!!!!!!!!!
    def collect(self, resources):
        self.inventory += resources.valor
        self.model.grid.remove_agent(resources)

    #Função para verificar agentes vizinhos, buscando recursos (pode melhorar)
    #Falta teste para agente cercado de recursos
    def check_neigbors(self):
        neighbors = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False)
        for neighbor in neighbors:
            if isinstance(neighbor, Resources):
                self.collect(neighbor)

    def move(self):
        pass


#Agente reativo simples -> Filho do vagabundo de cima
class AgentRS(AgentIA):
    def move(self):
        self.check_neigbors()

        #Função de movimento aleatório simples de uma célula por vez no grid
        #Foi a forma mais burrinha de evitar sobreposição de agentes :D
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=False, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        while not self.model.grid.is_cell_empty(new_position):
            new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)
