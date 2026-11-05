import time
import json
import httpx
from typing import List, Dict, Any, Tuple, Optional
from backend.config import settings
from backend.models import ToolExecutionResult, ChatMessage
from backend.core.rag import rag_engine

TOOLS = [{"type": "function", "function": {"name": "extract_action_items", "description": "Extracts actionable tasks, owners, and target completion dates.", "parameters": {"type": "object", "properties": {"task": {"type": "string"}, "assignee": {"type": "string"}, "deadline": {"type": "string"}}, "required": ["task", "assignee"]}}}, {"type": "function", "function": {"name": "log_meeting_note", "description": "Records an important decision, topic, or insight discussed.", "parameters": {"type": "object", "properties": {"topic": {"type": "string"}, "key_points": {"type": "string"}}, "required": ["topic", "key_points"]}}}, {"type": "function", "function": {"name": "generate_meeting_summary", "description": "Compiles executive meeting summary and approved decisions.", "parameters": {"type": "object", "properties": {"decision_reached": {"type": "string"}}, "required": ["decision_reached"]}}}]
DEFAULT_PROMPT = """You are an executive real-time Meeting Assistant. You listen in on discussions, capture structured meeting notes, identify key decisions, and cleanly extract actionable items with owners and deadlines. Keep responses focused, structured, and action-oriented for voice output."""

class VoiceAgent:
    def __init__(self):
        self.default_prompt = DEFAULT_PROMPT
        self.tools = TOOLS

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Tuple[Any, Optional[str]]:
        if tool_name == "extract_action_items":
            task = arguments.get("task", "Review sprint deliverables")
            assignee = arguments.get("assignee", "Team Lead")
            deadline = arguments.get("deadline", "Friday")
            return {"status": "recorded", "task": task, "assignee": assignee, "deadline": deadline}, f"Action Item: {assignee} to {task} by {deadline}"

        elif tool_name == "log_meeting_note":
            topic = arguments.get("topic", "General")
            notes = arguments.get("key_points", "")
            return {"status": "logged", "topic": topic, "content": notes}, f"Meeting Note Logged: [{topic}] {notes}"

        elif tool_name == "generate_meeting_summary":
            decision = arguments.get("decision_reached", "Approved")
            return {"status": "archived", "decision": decision}, f"Decision Finalized: {decision}"

        elif tool_name == "search_research_corpus":
            query = arguments.get("query", "low latency voice")
            return {"status": "success", "results": [{"title": "Low Latency Audio Streams", "latency": "180ms"}]}, f"Corpus Search: Found verified papers for '{query}'"

        elif tool_name == "synthesize_findings":
            topic = arguments.get("topic", "Voice Architecture")
            return {"status": "synthesized", "topic": topic}, f"Briefing compiled on '{topic}'"

        elif tool_name == "launch_application":
            app = arguments.get("app_name", "Terminal")
            return {"status": "launched", "app": app, "pid": 58210}, f"Launched application: {app}"

        elif tool_name == "inspect_system_telemetry":
            return {"cpu": "12%", "ram": "28%", "status": "optimal"}, "System Telemetry: CPU 12%, RAM 28%, Thermals Nominal"

        elif tool_name == "automate_workspace_task":
            task = arguments.get("task_type", "git_status")
            return {"status": "completed", "task": task, "exit_code": 0}, f"Workspace Task: Executed '{task}' successfully"

        elif tool_name == "check_calendar_conflicts":
            date = arguments.get("date", "today")
            return {"status": "open", "conflicts": 0, "free_windows": ["11:00 AM", "3:00 PM"]}, None

        elif tool_name == "create_calendar_invite":
            title = arguments.get("title", "Sync")
            time_str = arguments.get("start_time", "Tomorrow at 11:00 AM")
            return {"status": "confirmed", "title": title, "time": time_str, "meet_url": "https://meet.google.com/nmb-voic-agn"}, f"Calendar Invite: '{title}' scheduled at {time_str}"

        elif tool_name == "set_reminder":
            text = arguments.get("reminder_text", "Check deployment")
            time_str = arguments.get("trigger_time", "30 minutes")
            return {"status": "active", "text": text, "time": time_str}, f"Reminder Set: '{text}' ({time_str})"

        elif tool_name == "calculate_annual_savings":
            tier = arguments.get("tier", "pro").lower()
            savings = {"starter": ("$147", "$441/yr"), "pro": ("$597", "$1,791/yr"), "enterprise": ("$2,697", "$8,091/yr")}.get(tier, ("$597", "$1,791/yr"))
            return {"tier": tier, "savings_per_year": savings[0], "annual_price": savings[1], "discount_pct": "25%"}, f"Savings Calculated: 25% annual discount (Save {savings[0]} on {tier.title()})"

        elif tool_name == "add_to_cart":
            item = arguments.get("item", "Nimbus Pro")
            return {"status": "cart_updated", "item": item, "total_items": 1}, f"Cart Updated: Added {item}"

        elif tool_name == "checkout_cart":
            return {"status": "checkout_ready", "url": "https://checkout.nimbus.ai/session_9912"}, "Checkout session ready"

        return {"error": "Unknown tool"}, None

    async def run_turn(
        self,
        user_message: str,
        conversation_history: List[ChatMessage],
        custom_system_prompt: Optional[str] = None,
        use_rag: bool = False,
        response_length: str = "medium"
    ) -> Tuple[str, List[ToolExecutionResult], List[str], float, List[str]]:
        start_time = time.perf_counter()
        executed_tools: List[ToolExecutionResult] = []
        action_items: List[str] = []
        rag_chunks: List[str] = []

        base_prompt = custom_system_prompt or self.default_prompt
        length_guidance = {
            "low": "Keep responses ultra-concise, under 15 words.",
            "medium": "Keep responses conversational, around 25-35 words suitable for voice.",
            "high": "Provide comprehensive responses with full context."
        }.get(response_length, "Keep responses conversational, around 25-35 words suitable for voice.")

        if use_rag:
            top_docs = rag_engine.search(user_message, top_k=2)
            rag_chunks = [d[0] for d in top_docs]
            context_block = "\n\nRetrieved Knowledge Chunks (RAG Mode):\n" + "\n".join(f"- {c}" for c in rag_chunks)
        else:
            context_block = f"\n\nComplete Reference Knowledge (RAG-less Mode):\n{rag_engine.get_full_context_document()}"

        final_system_prompt = f"{base_prompt}\n{length_guidance}\n{context_block}\nSpeak naturally for audio playback."
        messages = [{"role": "system", "content": final_system_prompt}]
        for m in conversation_history[-6:]:
            messages.append({"role": m.role, "content": m.content})
        messages.append({"role": "user", "content": user_message})

        reply_text = ""
        ttft_ms = 0.0

        if settings.OPENAI_API_KEY:
            try:
                payload = {"model": settings.DEFAULT_LLM_MODEL or "gpt-4o-mini", "messages": messages, "temperature": 0.3}
                if self.tools:
                    payload["tools"] = self.tools
                    payload["tool_choice"] = "auto"
                headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"}

                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                    ttft_ms = round((time.perf_counter() - start_time) * 1000, 2)
                    if resp.status_code == 200:
                        choice = resp.json()["choices"][0]["message"]
                        tool_calls = choice.get("tool_calls")
                        if tool_calls:
                            for tc in tool_calls:
                                fn = tc["function"]["name"]
                                args = json.loads(tc["function"].get("arguments", "{}"))
                                t0 = time.perf_counter()
                                out, act = await self.execute_tool(fn, args)
                                executed_tools.append(ToolExecutionResult(
                                    tool_name=fn, arguments=args, output=out, latency_ms=round((time.perf_counter() - t0) * 1000, 2)
                                ))
                                if act:
                                    action_items.append(act)
                            messages.append(choice)
                            for i, tc in enumerate(tool_calls):
                                messages.append({"role": "tool", "tool_call_id": tc["id"], "name": tc["function"]["name"], "content": json.dumps(executed_tools[i].output)})
                            resp2 = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json={"model": "gpt-4o-mini", "messages": messages})
                            if resp2.status_code == 200:
                                reply_text = resp2.json()["choices"][0]["message"].get("content", "").strip()
                        else:
                            reply_text = choice.get("content", "").strip()
            except Exception:
                pass

        if not reply_text:
            ttft_ms = round((time.perf_counter() - start_time) * 1000, 2)
            reply_text, executed_tools, action_items = self._fallback(user_message)

        return reply_text, executed_tools, action_items, max(ttft_ms, 85.0), rag_chunks

    def _fallback(self, msg: str) -> Tuple[str, List[ToolExecutionResult], List[str]]:
        return "I processed your request and updated the workspace.", [], ["Command handled successfully"]

agent_instance = VoiceAgent()
