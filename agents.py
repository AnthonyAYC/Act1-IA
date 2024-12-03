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
            if resources in self.model.anc_resources:
                self.model.anc_resources.remove(resources)

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

    _RECURSO = "Recurso"
    _RECURSOCOLETADO = "Recurso Coletado"
    _EXPLORADO = "Explorado"
    _VISITADO = "Visitado"
    _OBSTACULOS = "Obstáculos"
    _AGENTE = "Agente"
    _VAZIO = "Vazio"


    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.memory = {}
        self.acao = 'moveRandom'

    

    def percepcoes(self):
        neighbors = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False)

        neighborhood = self.model.grid.get_neighborhood(
            self.pos, moore=False, include_center=False
        )

        perception = {}

        for position in neighborhood:

            perception[position] = self._VAZIO
            for neighbor in neighbors:

                if position == neighbor.pos:
                    perception[position] = neighbor
                    break

        print('Percepções:', perception)

        return perception

    def atualizarConhecimento(self, percepcoes):


        for pos, percepcao in percepcoes.items():

            if isinstance(percepcao, Resources):
                self.memory[pos] = self._RECURSO
            elif isinstance(percepcao, ContinuousObstacle):
                self.memory[pos] = self._OBSTACULOS
            elif isinstance(percepcao, AgentIA):
                self.memory[pos] = self._AGENTE
            elif self.memory.get(pos) is None:
                self.memory[pos] = self._VAZIO
                  

        if self.inventory == 0:  
            self.memory[self.pos] = self._EXPLORADO
        else:
            self.memory[self.pos] = self._VISITADO


    def ePosicaoExploradaUtil(self, pos):

        x,y = pos

        for x1, y1 in [(0, -1), (-1, 0), (1, 0), (0, 1)]: 
            if self.memory.get((x + x1, y + y1)) == self._RECURSO:
                return True
        
        return False

        
    def escolherAcao(self, percepcoes, acao_atual):

        resources = []
        agents_next = []
        obstaculos = []
        possible_steps = []
        base = []

        # Processa percepções
        for pos, percepcao in percepcoes.items():
            if isinstance(percepcao, Resources):
                resources.append(percepcao)
            elif isinstance(percepcao, ContinuousObstacle):
                obstaculos.append(percepcao)
            elif isinstance(percepcao, AgentIA):
                agents_next.append(percepcao)
            elif isinstance(percepcao, Base):
                base.append(percepcao)
            elif self.memory.get(pos) != self._EXPLORADO:
                possible_steps.append(pos)
            elif self.memory.get(pos) == self._EXPLORADO and self.ePosicaoExploradaUtil(pos):
                possible_steps.append(pos)



        if self.partner is not None and acao_atual == 'Seguir':
            if not base:
                return {'acao': acao_atual}
            
            return {'acao': 'deliver', 'base': base}

        # Determina a ação com base nas condições
        if acao_atual == 'RetornaABase':
            # Continua indo para a base se ainda não foi encontrada
            if not base:
                return {'acao': acao_atual}
            # Entregar recursos na base
            return {'acao': 'deliver', 'base': base}

        # Retorna à base após coletar recurso
        if acao_atual in ['collect', 'collect10e20']:
            return {'acao': 'RetornaABase'}

        # Coleta recursos se há agentes próximos
        if resources and agents_next:
            resources_validos = [r for r in resources if r.valor == 50]
            agente_validos = [a for a in agents_next if isinstance(a, AgentBE)]
            # Verifica se tem agentes próximos (mesmo tipo) e recursos com valor 50
            if resources_validos and agente_validos:
                return {'acao': 'collect', 'recursos': resources_validos, 'agentes': agente_validos}

        # Coleta recursos específicos (10 e 20)
        if resources:
            resources_validos = [r for r in resources if r.valor != 50]
            # Verifica se tem recursos com valores 10 e 20
            if resources_validos:
                return {'acao': 'collect10e20', 'recursos': resources_validos}

        # Move para posições não exploradas ou exploradas util
        if possible_steps:
            return {'acao': 'moveToPos', 'steps': possible_steps}

        # Move aleatoriamente se não há opções melhores
        return {'acao': 'moveRandom'}


    def excutarAcao(self, acao_regras):

        if acao_regras['acao'] == 'RetornaABase':
            self.move_to_base()
            print('Item valor: {}'.format(self.inventory))
        elif acao_regras['acao'] == 'deliver':
            self.deliver()
        elif acao_regras['acao'] == 'collect10e20':
            resource_escolhido = max(acao_regras['recursos'], key=lambda obj: obj.valor)
            self.collect(resource_escolhido)
        elif acao_regras['acao'] == 'collect':
            resource_escolhido = max(acao_regras['recursos'], key=lambda obj: obj.valor)

            agente_partner = acao_regras['agentes'][0]
            
            self.partner = agente_partner
            agente_partner.partner = self

            self.partner.acao = 'Seguir'
            
            resource_escolhido.can_collect = True

            self.collect(resource_escolhido)
        elif acao_regras['acao'] == 'moveToPos':
            possible_steps = acao_regras['steps']
            new_position = self.random.choice(possible_steps)
            print('pos: {}'.format(new_position))
            self.move_to_pos(new_position)      
        elif acao_regras['acao'] == 'moveRandom':
            self.move_random()
            
        self.acao = acao_regras['acao']

        return
    
    def check(self):

        percepcoes = self.percepcoes()
        
        self.atualizarConhecimento(percepcoes)

        acao = self.escolherAcao(percepcoes, self.acao)


        self.excutarAcao(acao)

class AgentCoop(AgentIA):
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


                #Vizinhos do re
                resource_neighbors = self.model.grid.get_neighbors(neighbor.pos, moore=False, include_center=False)

                # Se estiver de inventário vazio e não está indo ajudar outro e não está ajudando a carregar, ele pode coleta!
                if self.agent_available():

                    #Se for uma estrutura antiga que exige ajuda e não há agentes ao redor aguardando
                    if neighbor.valor == 50:
                        #O agente fica aguardando
                        if not any((isinstance(agent, AgentCoop) or isinstance(agent, AgentBDI)) and agent.waiting for agent in resource_neighbors):
                            self.waiting = True

                        if neighbor not in self.model.pos_resources:
                            self.model.pos_resources.append(neighbor)
                        #Pensando em usos futuros > resource_neighbors = self.model.grid.get_neighbors(neighbor.pos, moore=False, include_center=False)
                        agent_neighbors = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False)

                        for i in agent_neighbors:
                            if (isinstance(i, AgentCoop) or isinstance(i, AgentBDI)) and i.moving_to_pos:

                        #Se tiver "ajuda" -> Para de aguardar, coloca que nenhum agente ao redor está indo ajudar
                                i.partner = self
                                self.partner = i
                                self.waiting = False
                                if isinstance(i, AgentCoop):
                                    agentsBDI = self.model.agents_by_type[AgentCoop]
                                else:
                                    agentsBDI = self.model.agents_by_type[AgentBDI]
                                for j in agentsBDI:
                                    j.moving_to_pos = False
                                neighbor.can_collect = True
                                self.collect(neighbor)
                                return

                    #Se não, é qualquer outro simples
                    else:
                        if self.model.anc_resources:
                            if neighbor.valor == 50:
                                self.collect(neighbor)
                        else:
                            self.collect(neighbor)

            # Se o vizinho é a base ≥ Entrega o inventário
            elif isinstance(neighbor, Base):
                self.deliver()

    def scan(self):
        resources_list = []
        for cell in self.model.grid.coord_iter():

            cell_content = cell[0]  # cell[0] é o conteúdo, cell[1] e cell[2] são as coordenadas
            for agent in cell_content:
                if isinstance(agent, Resources):
                    if agent.valor == 50:
                        if agent not in self.model.anc_resources:
                            self.model.anc_resources.append(agent)
                            resources_list.append(agent)
        return resources_list

    def priority(self):
        x_atual = self.pos[1]
        y_atual = self.pos[0]
        pos_final = (0, 0)
        min_x = 100000
        min_y = 100000

        if self.model.anc_resources:
            for resource in self.model.anc_resources:

                #1° Prioridade - Recursos com agentes BDI aguardando!
                around_resources = self.model.grid.get_neighbors(resource.pos, moore=False, include_center=False)
                for agent in around_resources:
                    if (isinstance(agent, AgentCoop) or isinstance(agent, AgentBDI)) and agent.waiting:
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

        else:
            for resource in self.model.pos_resources:

                #1° Prioridade - Recursos com agentes BDI aguardando!
                around_resources = self.model.grid.get_neighbors(resource.pos, moore=False, include_center=False)
                for agent in around_resources:
                    if (isinstance(agent, AgentCoop) or isinstance(agent, AgentBDI)) and agent.waiting:
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


        if self.inventory != 0:
            self.move_to_base()
        else:
            if not self.waiting and self.partner is None:
                if self.model.pos_resources:
                    self.move_to_pos(self.priority())
                else:
                    if self.model.anc_resources:
                        self.move_to_pos(self.priority())
                    else:
                        self.move_random()


class AgentBDI(AgentIA):
    def __init__(self, pos, model):
        super().__init__(pos, model)

        self.waiting = False

        #Tem o intuito de impedir outras ações enquanto o agente se movimenta para ajudar outro.
        self.moving_to_pos = False

    def agent_available(self):
        if self.inventory == 0 and not self.moving_to_pos and self.partner is None and not self.explore():
            return True
        else:
            return False

    def explore(self):
        agents = -1
        for i in self.model.grid.agents:
            if isinstance(i, AgentCoop) or isinstance(i, AgentBDI):
                agents+=1
        resources = len(self.model.pos_resources)
        #Mais agentes que recurso -> Pode focar em explorar, caso não, coletar é principal.
        if agents > resources:
            return True
        else:
            return False

    def check_neighbors(self):
        # Verifica os vizinhos do agente
        neighbors = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False)
        for neighbor in neighbors:
            # Se o vizinho é um recurso -> Processo de coleta
            if isinstance(neighbor, Resources):

                # Se não estiver no array de recursos conhecidos, adiciona!
                if neighbor not in self.model.pos_resources:
                    self.model.pos_resources.append(neighbor)

                # Vizinhos do recurso
                resource_neighbors = self.model.grid.get_neighbors(neighbor.pos, moore=False, include_center=False)

                # Se estiver de inventário vazio e não está indo ajudar outro e não está ajudando a carregar, ele pode coleta!
                if self.agent_available():

                    # Se for uma estrutura antiga que exige ajuda e não há agentes ao redor aguardando
                    if neighbor.valor == 50:
                        # O agente fica aguardando
                        if not any((isinstance(agent, AgentCoop) or isinstance(agent, AgentBDI)) and agent.waiting for agent in resource_neighbors):
                            self.waiting = True

                        # Pensando em usos futuros > resource_neighbors = self.model.grid.get_neighbors(neighbor.pos, moore=False, include_center=False)
                        agent_neighbors = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False)

                        for i in agent_neighbors:
                            if (isinstance(i, AgentCoop) or isinstance(i, AgentBDI)) and i.moving_to_pos:

                                # Se tiver "ajuda" -> Para de aguardar, coloca que nenhum agente ao redor está indo ajudar
                                i.partner = self
                                self.partner = i
                                self.waiting = False

                                if isinstance(i, AgentCoop):
                                    agents = self.model.agents_by_type[AgentCoop]
                                else:
                                    agents = self.model.agents_by_type[AgentBDI]
                                for j in agents:
                                    j.moving_to_pos = False
                                neighbor.can_collect = True
                                self.collect(neighbor)
                                return

                    # Se não, é qualquer outro simples
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
                if (isinstance(agent, AgentCoop) or isinstance(agent, AgentBDI)) and agent.waiting:
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
        if self.inventory != 0:
            self.move_to_base()
        else:
            if not self.waiting and self.partner is None:
                if self.explore():
                    self.move_random()
                else:
                    self.move_to_pos(self.priority())
