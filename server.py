from agents import AgentRS, AgentBE, AgentBDI, ContinuousObstacle, Resources
from model import ModelIA
from mesa.visualization import (
    SolaraViz,
    make_plot_component,
    make_space_component,
)

#DISCLAIMER: ISSO AQUI É CONFUSO PORQUE É A VISUALIZAÇÃO "NOVA" DA BIBLIOTECA E NÃO TEM TUTORIAL PARA GENTE BURRA(EU)

#Função padrão para definir a visualização dos agentes!
#Acho que vamo usando isinstance até o fim da vida aqui
def agent_portrayal(agent):
    if agent is None:
        return
    portrayal = {
        "size": 50,
    }
    if isinstance(agent, ContinuousObstacle):
        portrayal["color"] = "black"
        portrayal["marker"] = "o"
    elif isinstance(agent, Resources):
        if agent.valor == 10:
            portrayal["color"] = "cyan"
        elif agent.valor == 20:
            portrayal["color"] = "gray"
        elif agent.valor == 50:
            portrayal["color"] = "gold"
        portrayal["marker"] = "o"
    elif isinstance(agent, AgentRS):
        portrayal["color"] = "green"
        portrayal["marker"] = "o"
    elif isinstance(agent, AgentBE):
        portrayal["color"] = "red"
    elif isinstance(agent, AgentBDI):
        portrayal["color"] = "purple"
        portrayal["marker"] = "o"
    return portrayal

#Números no grid e o aspect equal pra balancer x e y
def post_process(ax):
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])

#Isso aqui com certeza deve deixar muito foda as coisas, mas eu sinceramente tenho preocupações maiores
model_params = {
   
}

# Inicia o modelo
model1 = ModelIA()

#Isso aqui com certeza deve deixar muito foda as coisas, mas eu sinceramente tenho preocupações maiores
model_params = {}

#Segue a explicação do código copiado do GitHub:
# Create visualization elements. The visualization elements are solara components
# that receive the model instance as a "prop" and display it in a certain way.
# Under the hood these are just classes that receive the model instance.
# You can also author your own visualization elements, which can also be functions
# that receive the model instance and return a valid solara component.
SpaceGraph = make_space_component(
    agent_portrayal, post_process=post_process, draw_grid=True
)

#Segue a explicação do código copiado do GitHub:
# Create the SolaraViz page. This will automatically create a server and display the
# visualization elements in a web browser.
# Display it using the following command in the example directory:
# solara run app.py <- IMPORTANTE !!!!!!!!!!
# It will automatically update and display any changes made to this file
page = SolaraViz(
    model1,
    components=[SpaceGraph],
    model_params=model_params,
    name="MESA Python Test",
)
page  # noqa