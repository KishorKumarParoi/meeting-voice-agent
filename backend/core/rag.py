import re
import math
from typing import List, Dict, Tuple

KNOWLEDGE_DOCS = ["Meeting Protocol: Capture key decisions, action item assignees, target deadlines, and parking lot topics.", "Action Item Syntax: Assignee, specific task verb, deliverable, and explicit completion date or sprint milestone.", "Executive Summary Format: Context, 3-5 bulleted decisions, unblocking dependencies, next sync schedule.", "Speaker Diarization: Track multiple participant speech streams, isolating lead remarks and unanimous consensus.", "Integration: Direct sync capability with Notion, Slack, Jira, and Linear."]

class RAGEngine:
    STOP_WORDS = {"the", "a", "an", "is", "in", "it", "to", "for", "and", "or", "of", "on", "at", "with", "this", "that"}

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r"\w+", text.lower())
        return [w for w in words if w not in self.STOP_WORDS]

    def _compute_vector(self, tokens: List[str]) -> Dict[str, float]:
        vec: Dict[str, float] = {}
        for t in tokens:
            vec[t] = vec.get(t, 0.0) + 1.0
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        return {k: v / norm for k, v in vec.items()}

    def search(self, query: str, top_k: int = 2) -> List[Tuple[str, float]]:
        query_vec = self._compute_vector(self._tokenize(query))
        ranked = []
        for doc in KNOWLEDGE_DOCS:
            doc_vec = self._compute_vector(self._tokenize(doc))
            sim = sum(query_vec.get(k, 0) * doc_vec.get(k, 0) for k in query_vec)
            ranked.append((doc, round(sim, 4)))
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

    def get_full_context_document(self) -> str:
        return "\n".join(f"- {d}" for d in KNOWLEDGE_DOCS)

rag_engine = RAGEngine()
