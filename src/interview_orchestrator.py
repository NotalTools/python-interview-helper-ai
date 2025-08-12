from __future__ import annotations
from typing import List

from .agents.base import AgentContext, AgentMessage
from .agents.system_design import ArchitectAgent, StorageAgent, ReliabilityAgent, TradeoffsAgent
from .agents.algorithms import TaskmasterAgent, ComplexityAgent, TestGenAgent, AlgOptimizerAgent
from .agents.databases import DBModelerAgent, QueryOptimizerAgent, ConsistencyAgent, ReplicationAgent
from .agents.networking import ProtocolAnalystAgent, LatencyOptimizerAgent, LoadBalancerAgent, ChaosAgent
from .agents.security import ThreatModelerAgent, SecureCoderAgent, CryptoReviewerAgent, ComplianceAgent
from .agents.backend import APIDesignerAgent, PerfProfilerAgent, ReliabilityEngineerAgent, ObservabilityAgent
from .config import AppConstants


AGENT_REGISTRY = {
    "architect": ArchitectAgent,
    "storage": StorageAgent,
    "reliability": ReliabilityAgent,
    "tradeoffs": TradeoffsAgent,
    # algorithms
    "alg_taskmaster": TaskmasterAgent,
    "alg_complexity": ComplexityAgent,
    "alg_testgen": TestGenAgent,
    "alg_optimizer": AlgOptimizerAgent,
    # databases
    "db_modeler": DBModelerAgent,
    "db_query_optimizer": QueryOptimizerAgent,
    "db_consistency": ConsistencyAgent,
    "db_replication": ReplicationAgent,
    # networking
    "net_protocols": ProtocolAnalystAgent,
    "net_latency": LatencyOptimizerAgent,
    "net_lb": LoadBalancerAgent,
    "net_chaos": ChaosAgent,
    # security
    "sec_threats": ThreatModelerAgent,
    "sec_secure_code": SecureCoderAgent,
    "sec_crypto": CryptoReviewerAgent,
    "sec_compliance": ComplianceAgent,
    # backend
    "be_api": APIDesignerAgent,
    "be_perf": PerfProfilerAgent,
    "be_reliability": ReliabilityEngineerAgent,
    "be_obs": ObservabilityAgent,
}


class InterviewOrchestrator:
    """Мультиагентный конвейер для интервью по категориям. MVP: system_design."""

    def __init__(self, category: str):
        self.category = category
        names = AppConstants.INTERVIEW_CATEGORY_PIPELINES.get(category, [])
        self.agents = [AGENT_REGISTRY[name]() for name in names if name in AGENT_REGISTRY]

    async def critique(self, ctx: AgentContext) -> List[AgentMessage]:
        outputs: List[AgentMessage] = []
        for agent in self.agents:
            msg = await agent.act(ctx)
            ctx.history.append(msg)
            outputs.append(msg)
        return outputs
