from langgraph.constants import START, END
from langgraph.graph import StateGraph
from main_process.node_bge_m3 import node_bge_m3
from main_process.node_content_split import node_content_split
from main_process.node_content_to_milvus import node_content_to_milvus
from main_process.node_entry import node_entry
from main_process.node_item_recognition import node_item_recognition
from main_process.node_md_image import node_md_img
from main_process.node_pdf_2_md import node_pdf_2_md
from main_process.state import ImportGraphState


class main_process:
    def __init__(self):
        self.builder = StateGraph(state_schema=ImportGraphState)
        self.add_nodes()
        self.add_edges()
        self.graph = None


    def add_nodes(self):
        self.builder.add_node(node_entry.name,node_entry())
        self.builder.add_node(node_pdf_2_md.name,node_pdf_2_md())
        self.builder.add_node(node_md_img.name,node_md_img())
        self.builder.add_node(node_content_split.name,node_content_split())
        self.builder.add_node(node_item_recognition.name,node_item_recognition())
        self.builder.add_node(node_bge_m3.name,node_bge_m3())
        self.builder.add_node(node_content_to_milvus.name,node_content_to_milvus())

    def add_edges(self):
        self.builder.add_edge(START,node_entry.name)
        self.builder.add_conditional_edges(node_entry.name,self.after_entry_router)
        self.builder.add_edge(node_pdf_2_md.name,node_md_img.name)
        self.builder.add_edge(node_md_img.name,node_content_split.name)
        self.builder.add_edge(node_content_split.name,node_item_recognition.name)
        self.builder.add_edge(node_item_recognition.name,node_bge_m3.name)
        self.builder.add_edge(node_bge_m3.name,node_content_to_milvus.name)
        self.builder.add_edge(node_content_to_milvus.name,END)


    def after_entry_router(self,state: ImportGraphState):
        if state.get('is_pdf_read_enabled',False):
            return node_pdf_2_md.name
        elif state.get('is_md_read_enabled',False):
            return node_md_img.name
        else:
            return END


    def run(self,state: ImportGraphState):
        if not self.graph:
            self.graph = self.builder.compile()
        return self.graph.invoke(state)



    #   def __init__(self):
    #     self.builder = StateGraph(state_schema=ImportGraphState)
    #     self.add_nodes()
    #     self.add_edges()
    #     self.graph = None
    #     相当于先走一遍初始化再run
    @classmethod
    def create_and_run(cls,state: ImportGraphState):
        return cls().run(state)

if __name__ == '__main__':
    init_state = {
        'local_file_path': r'D:\kb_pro_imitation\05-device_txt\doc\hak180产品安全手册.pdf',
        'local_dir':r'D:\kb_pro_imitation\output'
    }
    # main_nigger =  main_process()
    res =main_process.create_and_run(init_state)