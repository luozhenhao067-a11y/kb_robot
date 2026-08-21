from langgraph.constants import START, END
from langgraph.graph import StateGraph
from query.nodes.answer_output import answer_output
from query.nodes.rerank import rerank
from query.nodes.rrf import rrf
from query.nodes.search_embedding import search_embedding
from query.nodes.know_the_fucking_item import know_the_fucking_item
from query.nodes.search_hyde import search_hyde
from query.nodes.search_web import search_web
from query.state import QueryGraphState


class fuck_nigger:
    def __init__(self):
        self.builder=StateGraph(state_schema=QueryGraphState)
        self.add_nodes()
        self.add_edges()
        self.graph=None


    def add_nodes(self):
        self.builder.add_node(know_the_fucking_item.name,know_the_fucking_item())
        self.builder.add_node(search_embedding.name,search_embedding())
        self.builder.add_node(search_hyde.name,search_hyde())
        self.builder.add_node(search_web.name,search_web())
        self.builder.add_node(rrf.name,rrf())
        self.builder.add_node(rerank.name,rerank())
        self.builder.add_node(answer_output.name,answer_output())

    def add_edges(self):
        self.builder.add_edge(START,know_the_fucking_item.name)
        # 给名字 graph自己调用
        self.builder.add_conditional_edges(know_the_fucking_item.name,self.after_item_router)
        self.builder.add_edge(search_embedding.name,rrf.name)
        self.builder.add_edge(search_hyde.name,rrf.name)
        self.builder.add_edge(search_web.name,rrf.name)
        self.builder.add_edge(rrf.name,rerank.name)
        self.builder.add_edge(rerank.name,answer_output.name)
        self.builder.add_edge(answer_output.name,END)


    def after_item_router(self,state:QueryGraphState):
        answer=state.get('answer')
        if answer: # 有answer,直接返answer
            return answer_output.name
        else:
            return [search_embedding.name,search_hyde.name,search_web.name]

    def run(self,state:QueryGraphState):
        if self.graph is None:
            self.graph=self.builder.compile()
        return self.graph.invoke(state)

    @classmethod
    def create_and_run(cls,state:QueryGraphState):
        return cls().run(state)