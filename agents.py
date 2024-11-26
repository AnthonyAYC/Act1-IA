
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
        if self.inventory == 0:
            self.inventory += resources.valor
            self.model.grid.remove_agent(resources)

    def deliver(self):
        for obj in self.model.array_points:
            if obj.agent_type is type(self):
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
        self.waiting = False
        self.moving = False

    def collect(self, resources):
        if self.inventory == 0:
            self.inventory += resources.valor
            self.model.grid.remove_agent(resources)
            self.model.pos_resources.remove(resources)

    def check_neigbors(self):
        neighbors = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False)
        for neighbor in neighbors:
            if isinstance(neighbor, Resources):
                if neighbor not in self.model.pos_resources:
                    self.model.pos_resources.append(neighbor)
                if self.inventory == 0 and neighbor.valor == 50 and self.moving == False:
                    self.waiting = True
                    agents_around = self.model.grid.get_neighbors(neighbor.pos, moore=False, include_center=False)
                    cont = 0
                    for i in agents_around:
                        if isinstance(i, AgentBDI):
                            cont += 1
                    if cont >= 2:
                        self.waiting = False
                        for i in agents_around:
                            if isinstance(i, AgentBDI):
                                i.moving = False
                        self.collect(neighbor)
                if neighbor.valor != 50:
                    self.collect(neighbor)

            elif isinstance(neighbor, Base):
                self.deliver()

    def move(self):
        if not self.waiting:
            possible_steps = self.model.grid.get_neighborhood(
                self.pos, moore=False, include_center=False
            )
            new_position = self.random.choice(possible_steps)
            while not self.model.grid.is_cell_empty(new_position):
                new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)

    def move_to_pos(self, pos):
        if not self.waiting:
            x_atual, y_atual = self.pos
            x_destino, y_destino = pos

            # Cálculo de direções possíveis
            direcoes = [
                ((x_atual + 1, y_atual), x_atual < x_destino),
                ((x_atual, y_atual + 1), y_atual < y_destino),
                ((x_atual - 1, y_atual), x_atual > x_destino),
                ((x_atual, y_atual - 1), y_atual > y_destino),
            ]

            # Tentar mover na direção mais lógica disponível
            for nova_posicao, condicao in direcoes:
                if condicao and self.model.grid.is_cell_empty(nova_posicao):
                    self.model.grid.move_agent(self, nova_posicao)

                    return

            for i in range(3):
                self.move()




    def priority(self):
        x_atual = self.pos[1]
        y_atual = self.pos[0]
        pos_final = (0,0)
        min_x = 100000
        min_y = 100000

        for i in self.model.pos_resources:
            around_resources = self.model.grid.get_neighbors(i.pos, moore=False, include_center=False)
            for j in around_resources:
                if isinstance(j, AgentBDI) and j.waiting == True:
                    pos_final = i.pos
                    if self.waiting == False:
                        self.moving = True
                    return pos_final

            x_destino = i.pos[1]
            y_destino = i.pos[0]
            if abs(x_atual-x_destino) < min_x and abs(y_atual-y_destino) < min_y:
                min_x = x_destino
                min_y = y_destino
                pos_final = i.pos
        return pos_final


    def check(self):
        self.check_neigbors()
        if self.inventory != 0:
            self.move_to_pos((1,1))
        elif self.model.pos_resources and self.inventory == 0:
            self.move_to_pos(self.priority())
        else:
            self.moving = False
            self.move()
        print("--------------------")
        print("ARRAY DE RECURSOS")
        print(self.model.pos_resources)
        print("--------------------")
        print(self.waiting)
        print(self.moving)