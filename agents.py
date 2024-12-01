from mesa import Agent

# Classe para a Base:
# São agentes simples e imóveis
class Base(Agent):
    def __init__(self, pos, model):
        super().__init__(model)
        self.pos = pos


# Classe de Obstáculos:
# São agentes simples e imóveis
class ContinuousObstacle(Agent):
    def __init__(self, pos, model):
        super().__init__(model)
        self.pos = pos


# Classe de Recursos
# São agentes simples e imóveis, nesse caso, com valores atribuidos
class Resources(Agent):
    def __init__(self, pos, model, valor):
        super().__init__(model)
        self.pos = pos
        self.valor = valor
        self.can_collect = True
        if self.valor == 50:
            self.can_collect = False


# Classe Agente "PAI?"
# Contém os atributos comuns a maioria dos agentes (eu acho :D)
class AgentIA(Agent):
    def __init__(self, pos, model):
        super().__init__(model)
        self.pos = pos
        self.lastPos = pos
        self.partner = None
        self.inventory = 0

    # Funções de Coleta e Entrega
    def collect(self, resources):
        if self.inventory == 0 and resources.can_collect:
            self.inventory += resources.valor
            self.model.grid.remove_agent(resources)
            if resources in self.model.pos_resources:
                self.model.pos_resources.remove(resources)

    def deliver(self):
        for obj in self.model.array_points:
            if obj.agent_type is type(self):
                obj.point += self.inventory
                self.inventory = 0
        if self.partner is not None:
            self.partner.partner = None
            self.partner = None

    # Função para verificar agentes vizinhos, buscando recursos (pode melhorar)
    def check_neighbors(self):
        neighbors = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False)
        for neighbor in neighbors:
            if isinstance(neighbor, Resources):
                self.collect(neighbor)
            elif isinstance(neighbor, Base):
                self.deliver()

    #Funções de movimentação

    def move_random(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=False, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        while not self.model.grid.is_cell_empty(new_position):
            new_position = self.random.choice(possible_steps)
        self.lastPos = self.pos
        self.model.grid.move_agent(self, new_position)

    def move_to_pos(self, pos):
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
                self.lastPos = self.pos
                self.model.grid.move_agent(self, nova_posicao)
                return
        #Ultima opção para obstaculos
        for i in range(3):
            self.move_random()

    def move_to_base(self):
        base_pos = self.model.base_size
        base_pos = (base_pos - 1) // 2

        self.move_to_pos((base_pos, base_pos))

        if self.partner is not None:
            self.model.grid.move_agent(self.partner, self.lastPos)

# Agente reativo simples -> Filho do vagabundo de cima
class AgentRS(AgentIA):
    def step(self):
        self.check_neighbors()
        if self.inventory != 0:
            self.move_to_base()
        else:
            self.move_random()


class AgentBE(AgentIA):

    def __init__(self, pos, model, base_pos=None):
        super().__init__(pos, model)
        self.carga = False
        self.memory = {
            "path": {},
            "agents": {},
            "resources": {},
        }

        self.parceiro = None

        # informação da base
        if base_pos is None:
            base_pos = (1, 1)
        self.base_pos = base_pos

    def collect(self, resources):
        self.inventory += resources.valor
        self.carga = True
        self.model.grid.remove_agent(resources)

    def check_neighbors(self):
        neighbors = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False)
        return neighbors

    # retirar não está em uso
    def move_random(self, possible_steps):

        possible_steps_empty = [pos for pos in possible_steps if self.model.grid.is_cell_empty(pos)]
        new_position = self.random.choice(possible_steps_empty)

        self.model.grid.move_agent(self, new_position)

    def pathExplorado(self, new_position):

        if self.memory["path"].get(new_position) == "Explorado":
            return True

        return False

    def pathComRecursos(self, new_position):

        x1, y1 = new_position

        if self.pathExplorado(new_position):
            for x2 in [1, -1]:
                for y2 in [1, -1]:
                    pos = (x1 + x2, y1 + y2)
                    if not self.memory["resources"].get(pos) is None and self.memory["resources"].get(pos).valor != 50:
                        return True

        return False

    def explorar(self):

        # vizinhos (percepções)
        neighbors = self.check_neighbors()

        # atualizar modelo
        resources = []
        agents_next = []

        for neighbor in neighbors:
            if isinstance(neighbor, Resources):
                self.memory["resources"][neighbor.pos] = neighbor
                resources.append(neighbor)
            elif isinstance(neighbor, AgentIA):
                self.memory["agents"][neighbor.pos] = neighbor
                if isinstance(neighbor, AgentBE):
                    agents_next.append(neighbor)
            # Se precisar implementa para salvar obstáculos

        # decidi ação
        resource_escolhido = None

        if len(resources) > 0:
            # pegar recurso de valor 50
            recursos_valor_50 = [r for r in resources if r.valor == 50]
            if recursos_valor_50 and len(agents_next) >= 1:
                # pegar o primeiro recurso com valor 50
                resource_escolhido = recursos_valor_50[0]

                # coletar recurso
                # atualizar a gente aux
                # chamar agente aux
                # mandar agente aux a base pelas mesma posições do agente atual
                self.collect(resource_escolhido)
                self.memory["resources"][resource_escolhido.pos] = None

                agente = agents_next[0]

                agente.carga = True
                agente.parceiro = self

                return

            else:
                resources_validos = [r for r in resources if r.valor != 50]
                if resources_validos:
                    # pegar o recurso de maior valor (talvez retirar e pegar apenas o primeiro da lista)
                    resource_escolhido = max(resources_validos, key=lambda obj: obj.valor)
                    # agente coletar recurso
                    # self.model.grid.move_agent(self, resource_escolhido.pos)
                    self.collect(resource_escolhido)
                    # Atualizar modelo
                    self.memory["resources"][resource_escolhido.pos] = None
                    return

        # move agente

        # posições
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=False, include_center=False
        )

        # posições válidas
        possible_steps_validas = [pos for pos in possible_steps if
                                  self.model.grid.is_cell_empty(pos) and not self.pathExplorado(pos)]

        # verificar se tem posições válidas
        if possible_steps_validas:
            new_position = self.random.choice(possible_steps_validas)
        else:
            # pegar as posições sem obstáculos (qualquer tipo de agente)
            possible_steps_empty = [pos for pos in possible_steps if self.model.grid.is_cell_empty(pos)]
            # pegar posições que ele tem conhecimento sobre recursos próximos
            possible_steps_resource = [pos for pos in possible_steps_empty if self.pathComRecursos(pos)]

            # verificar ser tem posições com recursos
            if possible_steps_resource:
                new_position = self.random.choice(possible_steps_resource)
            else:
                new_position = self.random.choice(possible_steps_empty)

        self.memory["path"][new_position] = "Explorado"
        self.model.grid.move_agent(self, new_position)

    def retornar(self):

        if self.pos == self.base_pos:
            # Entregar recurso
            self.carga = False
            # atualizar modelo
            self.memory["path"] = {key: value for key, value in self.memory["path"].items() if value != "Não explorado"}

            # salvar recurso entrege na base
        else:
            # Caminhar na direção da base
            x, y = self.pos
            bx, by = self.base_pos

            nova_pos = (x + (1 if bx > x else -1 if bx < x else 0),
                        y + (1 if by > y else -1 if by < y else 0))

            if bx != x and by != y:
                if abs(bx - x) > abs(by - y):  # Preferir movimento horizontal
                    nova_pos = (x + (1 if bx > x else -1), y)
                else:  # Preferir movimento vertical
                    nova_pos = (x, y + (1 if by > y else -1))

            # Verificar se posição não tem obstáculos (tá considerando todos os tipos de agent)
            if not self.model.grid.is_cell_empty(nova_pos) or self.memory["path"].get(nova_pos) == "Não explorado":
                possible_steps = self.model.grid.get_neighborhood(
                    self.pos, moore=False, include_center=False
                )
                possible_steps_empty = [pos for pos in possible_steps if self.model.grid.is_cell_empty(pos)]
                nova_pos = self.random.choice(possible_steps_empty)

            self.memory["path"][nova_pos] = "Não explorado"
            self.model.grid.move_agent(self, nova_pos)

    def seguir(self):

        pos_parceiro = self.parceiro.pos

        if pos_parceiro == self.base_pos:
            self.carga = False
            self.parceiro = None

        self.model.grid.move_agent(self, pos_parceiro)

    def step(self):
        if self.carga == False:
            self.explorar()
        elif self.carga == True:
            if not self.parceiro is None:
                self.seguir()
            self.retornar()


class AgentBDI(AgentIA):
    def __init__(self, pos, model):
        super().__init__(pos, model)

        self.waiting = False

        #Tem o intuito de impedir outras ações enquanto o agente se movimenta para ajudar outro.
        self.moving_to_pos = False

    def agent_available(self):
        if self.inventory == 0 and not self.moving_to_pos and self.partner is None:
            return True
        else:
            return False

    def check_neighbors(self):
        #Verifica os vizinhos do agente
        neighbors = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False)
        for neighbor in neighbors:
            #Se o vizinho é um recurso -> Processo de coleta
            if isinstance(neighbor, Resources):

                #Se não estiver no array de recursos conhecidos, adiciona!
                if neighbor not in self.model.pos_resources:
                    self.model.pos_resources.append(neighbor)

                #Vizinhos do re
                resource_neighbors = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False)

                # Se estiver de inventário vazio e não está indo ajudar outro e não está ajudando a carregar, ele pode coleta!
                if self.agent_available():

                    #Se for uma estrutura antiga que exige ajuda e não há agentes ao redor aguardando
                    if neighbor.valor == 50 and not any(isinstance(agent, AgentBDI) and agent.waiting for agent in resource_neighbors):
                        #O agente fica aguardando
                        self.waiting = True

                        #Pensando em usos futuros > resource_neighbors = self.model.grid.get_neighbors(neighbor.pos, moore=False, include_center=False)
                        agent_neighbors = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False)

                        for i in agent_neighbors:
                            if isinstance(i, AgentBDI) and i.moving_to_pos:

                        #Se tiver "ajuda" -> Para de aguardar, coloca que nenhum agente ao redor está indo ajudar
                                i.partner = self
                                self.partner = i
                                self.waiting = False

                                agentsBDI = self.model.agents_by_type[AgentBDI]
                                for j in agentsBDI:
                                    j.moving_to_pos = False
                                neighbor.can_collect = True
                                self.collect(neighbor)
                                return

                    #Se não, é qualquer outro simples
                    else:
                        self.collect(neighbor)

            # Se o vizinho é a base ≥ Entrega o inventário
            elif isinstance(neighbor, Base):
                self.deliver()

    def priority(self):
        x_atual = self.pos[1]
        y_atual = self.pos[0]
        pos_final = (0, 0)
        min_x = 100000
        min_y = 100000

        for resource in self.model.pos_resources:

            #1° Prioridade - Recursos com agentes BDI aguardando!
            around_resources = self.model.grid.get_neighbors(resource.pos, moore=False, include_center=False)
            for agent in around_resources:
                if isinstance(agent, AgentBDI) and agent.waiting:
                    pos_final = agent.pos
                    self.moving_to_pos = True
                    return pos_final

            #2° Prioridade - Recurso mais próximo!
            x_destino = resource.pos[1]
            y_destino = resource.pos[0]
            if abs(x_atual - x_destino) < min_x and abs(y_atual - y_destino) < min_y:
                min_x = x_destino
                min_y = y_destino
                pos_final = resource.pos

        return pos_final

    def check(self):
        self.check_neighbors()
        print(self.model.pos_resources)
        print("-------------------------")
        print("Agente: {}".format(self))
        print("Parceiro: {}".format(self.partner))
        print("Aguardando: {}".format(self.waiting))
        print("Indo ajudar: {}".format(self.moving_to_pos))
        print("-------------------------")
        if self.inventory != 0:
            self.move_to_base()
        else:
            if not self.waiting and self.partner is None:
                if self.model.pos_resources:
                    self.move_to_pos(self.priority())
                else:
                    self.move_random()
