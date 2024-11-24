from mesa import Agent

#Classe para a Base:
#São agentes simples e imóveis
class Base(Agent):
    def __init__(self, pos, model):
        super().__init__(model)
        self.pos = pos

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
        neighbors = self.model.grid.get_neighbors(resources.pos, moore=False, include_center=False)
        print(len(neighbors))
        if resources.valor == 50 and len(neighbors) >= 2:
            self.inventory += resources.valor
            self.model.grid.remove_agent(resources)
        elif resources.valor == 10 or resources.valor == 20:
            self.inventory += resources.valor
            self.model.grid.remove_agent(resources)

    def deliver(self):
        for obj in self.model.array_points:
            obj.point += self.inventory
            self.inventory = 0


    #Função para verificar agentes vizinhos, buscando recursos (pode melhorar)
    #Falta teste para agente cercado de recursos
    def check_neigbors(self):
        neighbors = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False)
        for neighbor in neighbors:
            if isinstance(neighbor, Resources):
                self.collect(neighbor)
            elif isinstance(neighbor, Base):
                self.deliver()
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

class AgentBDI(AgentIA):
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.moving = False
        self.waiting = False

    def check_neigbors(self):
        neighbors = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False)
        for neighbor in neighbors:
            if isinstance(neighbor, Resources):
                if neighbor.valor == 50 and neighbor not in self.model.pos_resources:
                    self.model.pos_resources.append(neighbor)
                else:
                    self.collect(neighbor)
                    self.model.pos_resources.remove(neighbor)
                    self.moving = False
            elif isinstance(neighbor, Base):
                self.deliver()

    def move(self):
        self.check_neigbors()
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=False, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        while not self.model.grid.is_cell_empty(new_position):
            new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def move_to_pos(self, pos):
        self.moving = True

        x_atual = self.pos[0]
        y_atual = self.pos[1]
        x_destino = pos[0]
        y_destino = pos[1]
        if x_atual < x_destino and self.model.grid.is_cell_empty((x_atual+1,y_atual)):
            x_atual += 1
        elif x_atual > x_destino and self.model.grid.is_cell_empty((x_atual-1,y_atual)):
            x_atual -= 1
        elif y_atual < y_destino and self.model.grid.is_cell_empty((x_atual,y_atual+1)):
            y_atual += 1
        elif y_atual > y_destino and self.model.grid.is_cell_empty((x_atual,y_atual-1)):
            y_atual -= 1


        new_position = (x_atual, y_atual)

        self.model.grid.move_agent(self, new_position)
        self.check_neigbors()


    def check(self):
        if self.model.pos_resources:
            position = self.model.pos_resources[0].pos
            self.move_to_pos(position)
        else:
            self.move()
        print(self.moving)
        print(self.model.pos_resources)