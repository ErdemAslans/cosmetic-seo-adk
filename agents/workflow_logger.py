"""
Agent Workflow Logger - N8N Style Execution Tracking
"""

import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from loguru import logger

@dataclass
class AgentExecution:
    agent_name: str
    task_id: str
    start_time: float
    end_time: Optional[float] = None
    status: str = "running"
    input_data: Dict[str, Any] = None
    output_data: Dict[str, Any] = None
    prompt_sent: str = ""
    ai_response: str = ""
    urls_processed: List[str] = None
    error_message: str = ""
    execution_duration: float = 0.0
    
    def __post_init__(self):
        if self.input_data is None:
            self.input_data = {}
        if self.urls_processed is None:
            self.urls_processed = []
    
    def complete(self, output_data: Dict[str, Any] = None, ai_response: str = ""):
        self.end_time = time.time()
        self.execution_duration = self.end_time - self.start_time
        self.status = "completed"
        if output_data:
            self.output_data = output_data
        if ai_response:
            self.ai_response = ai_response
    
    def error(self, error_message: str):
        self.end_time = time.time()
        self.execution_duration = self.end_time - self.start_time
        self.status = "error"
        self.error_message = error_message
    
    def to_dict(self):
        return asdict(self)

class WorkflowLogger:
    def __init__(self):
        self.executions: Dict[str, List[AgentExecution]] = {}
        self.agent_connections = {
            "scout": ["scraper"],
            "scraper": ["analyzer"],
            "analyzer": ["seo"],
            "seo": ["quality"],
            "quality": ["storage"],
            "storage": []
        }
    
    def start_execution(self, task_id: str, agent_name: str, input_data: Dict[str, Any] = None, prompt: str = "") -> str:
        """Yeni agent execution başlat"""
        if task_id not in self.executions:
            self.executions[task_id] = []
        
        execution = AgentExecution(
            agent_name=agent_name,
            task_id=task_id,
            start_time=time.time(),
            input_data=input_data or {},
            prompt_sent=prompt
        )
        
        self.executions[task_id].append(execution)
        
        logger.info(f"🤖 Agent '{agent_name}' started for task {task_id}")
        return f"{task_id}_{agent_name}_{int(time.time())}"
    
    def complete_execution(self, task_id: str, agent_name: str, output_data: Dict[str, Any] = None, 
                          ai_response: str = "", urls_processed: List[str] = None):
        """Agent execution'ı tamamla"""
        executions = self.executions.get(task_id, [])
        
        # En son aynı agent'ın execution'ını bul
        for execution in reversed(executions):
            if execution.agent_name == agent_name and execution.status == "running":
                execution.complete(output_data, ai_response)
                if urls_processed:
                    execution.urls_processed = urls_processed
                
                logger.info(f"✅ Agent '{agent_name}' completed for task {task_id} in {execution.execution_duration:.2f}s")
                break
    
    def error_execution(self, task_id: str, agent_name: str, error_message: str):
        """Agent execution'da hata"""
        executions = self.executions.get(task_id, [])
        
        for execution in reversed(executions):
            if execution.agent_name == agent_name and execution.status == "running":
                execution.error(error_message)
                logger.error(f"❌ Agent '{agent_name}' failed for task {task_id}: {error_message}")
                break
    
    def get_workflow_state(self, task_id: str) -> Dict[str, Any]:
        """N8N tarzı workflow durumunu döndür"""
        if task_id not in self.executions:
            return {"nodes": [], "connections": [], "executions": []}
        
        executions = self.executions[task_id]
        
        # Nodes oluştur (her agent için)
        nodes = []
        node_positions = {
            "scout": {"x": 100, "y": 150},
            "scraper": {"x": 300, "y": 150},
            "analyzer": {"x": 500, "y": 150},
            "seo": {"x": 700, "y": 150},
            "quality": {"x": 900, "y": 150},
            "storage": {"x": 1100, "y": 150}
        }
        
        for agent_name, position in node_positions.items():
            # Bu agent için execution'ları bul
            agent_executions = [ex for ex in executions if ex.agent_name == agent_name]
            
            node_status = "pending"
            execution_data = None
            
            if agent_executions:
                latest_execution = agent_executions[-1]
                node_status = latest_execution.status
                execution_data = latest_execution.to_dict()
            
            nodes.append({
                "id": agent_name,
                "name": agent_name.title() + " Agent",
                "type": "agent",
                "position": position,
                "status": node_status,
                "execution": execution_data,
                "icon": self._get_agent_icon(agent_name),
                "color": self._get_status_color(node_status)
            })
        
        # Connections oluştur
        connections = []
        for source, targets in self.agent_connections.items():
            for target in targets:
                connections.append({
                    "source": source,
                    "target": target,
                    "type": "data"
                })
        
        return {
            "nodes": nodes,
            "connections": connections,
            "executions": [ex.to_dict() for ex in executions],
            "total_duration": sum(ex.execution_duration for ex in executions if ex.execution_duration),
            "completed_agents": len([ex for ex in executions if ex.status == "completed"]),
            "failed_agents": len([ex for ex in executions if ex.status == "error"]),
            "total_agents": len(set(ex.agent_name for ex in executions))
        }
    
    def _get_agent_icon(self, agent_name: str) -> str:
        icons = {
            "scout": "fas fa-search",
            "scraper": "fas fa-globe",
            "analyzer": "fas fa-microscope",
            "seo": "fas fa-sparkles",
            "quality": "fas fa-chart-line",
            "storage": "fas fa-database"
        }
        return icons.get(agent_name, "fas fa-robot")
    
    def _get_status_color(self, status: str) -> str:
        colors = {
            "pending": "#9ca3af",
            "running": "#3b82f6",
            "completed": "#10b981",
            "error": "#ef4444"
        }
        return colors.get(status, "#9ca3af")
    
    def clear_task(self, task_id: str):
        """Task'ı temizle"""
        if task_id in self.executions:
            del self.executions[task_id]

# Global workflow logger instance
workflow_logger = WorkflowLogger()