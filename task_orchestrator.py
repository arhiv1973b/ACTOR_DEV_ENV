import os
import sys
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Union

# Импортируем наши функциональные модули
# Предполагается, что они будут созданы в H:\ACTOR_DEV_ENV\
from hybrid_llm_engine import HybridLLMEngine

class AgentState(TypedDict):
    task: str
    plan: str
    result: str

from tool_library import ToolLibrary

class ToolAdapter:
    def __init__(self):
        self.engine = HybridLLMEngine()
        self.tools = {
            "system_health": ToolLibrary.system_health,
            "organize_files": ToolLibrary.organize_files,
            "data_analysis": ToolLibrary.data_analysis,
            "explain_codebase": ToolLibrary.explain_codebase
        }

    def run_task(self, task: str):
        # LLM определяет, какой инструмент использовать
        prompt = f"Задача: {task}. Выбери инструмент из списка: system_health, organize_files, data_analysis, explain_codebase. Верни только имя инструмента."
        tool_name = self.engine.query_ollama(prompt, model="qwen2.5:3b")["response"].strip()
        
        if tool_name in self.tools:
            return self.tools[tool_name]()
        else:
            return f"Tool {tool_name} not found or not mapped."

def orchestrator_node(state: AgentState):
    adapter = ToolAdapter()
    result = adapter.run_task(state["task"])
    return {"result": result}

# Инициализация графа
workflow = StateGraph(AgentState)
workflow.add_node("orchestrator", orchestrator_node)
workflow.set_entry_point("orchestrator")
workflow.add_edge("orchestrator", END)

app = workflow.compile()

if __name__ == "__main__":
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Organize my Downloads folder"
    initial_state = {"task": task}
    output = app.invoke(initial_state)
    print(output)
