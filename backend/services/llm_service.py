from __future__ import annotations

import json
import os
from typing import Any

from openai import AsyncOpenAI


class LLMService:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        requested_provider = (os.getenv("LLM_PROVIDER") or "").strip().lower()

        # Prefer Featherless by default when available, since it is mandatory for this deployment.
        if requested_provider == "featherless" or (
            not requested_provider and os.getenv("FEATHERLESS_API_KEY")
        ):
            provider = "featherless"
            selected_api_key = api_key or os.getenv("FEATHERLESS_API_KEY")
            selected_model = model or os.getenv("FEATHERLESS_MODEL") or "moonshotai/Kimi-K2-Instruct"
            selected_base_url = os.getenv("FEATHERLESS_BASE_URL") or "https://api.featherless.ai/v1"
        elif requested_provider == "groq" or (
            not requested_provider and os.getenv("GROQ_API_KEY")
        ):
            provider = "groq"
            selected_api_key = api_key or os.getenv("GROQ_API_KEY")
            selected_model = model or os.getenv("GROQ_MODEL") or "llama-3.3-70b-versatile"
            selected_base_url = os.getenv("GROQ_BASE_URL") or "https://api.groq.com/openai/v1"
        else:
            provider = "openai"
            selected_api_key = api_key or os.getenv("OPENAI_API_KEY")
            selected_model = model or os.getenv("OPENAI_MODEL") or "gpt-4.1-mini"
            selected_base_url = os.getenv("OPENAI_BASE_URL")

        self.provider = provider
        self.api_key = selected_api_key
        self.model = selected_model
        self.base_url = selected_base_url
        self.request_timeout = self._env_float("REQUEST_TIMEOUT", 10.0)
        self.max_tokens = self._env_int("MAX_TOKENS", 500)
        self.max_retries = self._env_int("MAX_RETRIES", 1)

        if not self.api_key:
            raise RuntimeError(
                "Missing API key for configured provider. Set FEATHERLESS_API_KEY (preferred), "
                "or configure LLM_PROVIDER with matching provider key."
            )
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.request_timeout,
            max_retries=self.max_retries,
        )

    async def analyze_candidate(self, candidate_data: dict[str, Any]) -> dict[str, Any]:
        prompt = (
            "You are an expert hiring analyst. Analyze the candidate payload and respond with JSON only "
            "with keys: summary (string), inferred_skills (array of strings), skill_score (0-100 number), "
            "project_score (0-100 number), communication_score (0-100 number), rationale (array of strings)."
        )

        parsed = await self._json_chat(
            system_prompt=prompt,
            user_payload=candidate_data,
            temperature=0.2,
        )

        return {
            "summary": str(parsed.get("summary", "")).strip(),
            "inferred_skills": [str(item) for item in parsed.get("inferred_skills", []) if str(item).strip()],
            "skill_score": self._clamp_score(parsed.get("skill_score", 0)),
            "project_score": self._clamp_score(parsed.get("project_score", 0)),
            "communication_score": self._clamp_score(parsed.get("communication_score", 0)),
            "rationale": [str(item) for item in parsed.get("rationale", []) if str(item).strip()],
        }

    async def generate_interview_question(
        self,
        candidate_context: dict[str, Any],
        transcript: list[dict[str, Any]],
        question_index: int,
        previous_answer_eval: dict[str, Any] | None,
    ) -> dict[str, Any]:
        prompt = (
            "You are an adaptive technical interviewer. Respond with JSON only and keys: "
            "question (string), focus_area (string), difficulty (string in {basic,intermediate,advanced}), "
            "why_this_question (string). Never return a generic or static question."
        )
        payload = {
            "candidate_context": candidate_context,
            "transcript": transcript,
            "question_index": question_index,
            "previous_answer_eval": previous_answer_eval,
            "instruction": "Generate the next best adaptive question.",
        }
        parsed = await self._json_chat(system_prompt=prompt, user_payload=payload, temperature=0.3)
        question = str(parsed.get("question", "")).strip()
        if not question:
            raise RuntimeError("LLM returned empty adaptive interview question")

        return {
            "question": question,
            "focus_area": str(parsed.get("focus_area", "general reasoning")).strip() or "general reasoning",
            "difficulty": str(parsed.get("difficulty", "intermediate")).strip() or "intermediate",
            "why_this_question": str(parsed.get("why_this_question", "")).strip(),
        }

    async def evaluate_interview_answer(
        self,
        candidate_context: dict[str, Any],
        question: str,
        answer: str,
        transcript: list[dict[str, Any]],
    ) -> dict[str, Any]:
        prompt = (
            "You are evaluating an interview answer. Respond JSON only with keys: "
            "depth (0-1), clarity (0-1), confidence (0-1), follow_up_needed (boolean), "
            "recommended_focus (string), evaluation_notes (array of strings)."
        )
        payload = {
            "candidate_context": candidate_context,
            "question": question,
            "answer": answer,
            "transcript": transcript,
        }
        parsed = await self._json_chat(system_prompt=prompt, user_payload=payload, temperature=0.2)

        return {
            "depth": self._clamp_ratio(parsed.get("depth", 0)),
            "clarity": self._clamp_ratio(parsed.get("clarity", 0)),
            "confidence": self._clamp_ratio(parsed.get("confidence", 0)),
            "follow_up_needed": bool(parsed.get("follow_up_needed", False)),
            "recommended_focus": str(parsed.get("recommended_focus", "")).strip() or "advanced problem solving",
            "evaluation_notes": [
                str(item) for item in parsed.get("evaluation_notes", []) if str(item).strip()
            ],
        }

    async def evaluate_hiring_agent(
        self,
        agent_name: str,
        rubric: str,
        candidate_context: dict[str, Any],
        transcript: list[dict[str, Any]],
        signals: dict[str, Any],
    ) -> dict[str, Any]:
        prompt = (
            "You are one stakeholder in a hiring panel. Respond JSON only with keys: "
            "score (0-1), reasoning (array of strings), risks (array of strings), strengths (array of strings)."
        )
        payload = {
            "agent_name": agent_name,
            "rubric": rubric,
            "candidate_context": candidate_context,
            "interview_transcript": transcript,
            "signals": signals,
        }
        parsed = await self._json_chat(system_prompt=prompt, user_payload=payload, temperature=0.2)

        return {
            "score": self._clamp_ratio(parsed.get("score", 0)),
            "reasoning": [str(item) for item in parsed.get("reasoning", []) if str(item).strip()],
            "risks": [str(item) for item in parsed.get("risks", []) if str(item).strip()],
            "strengths": [str(item) for item in parsed.get("strengths", []) if str(item).strip()],
        }

    async def summarize_final_report(self, report_input: dict[str, Any]) -> dict[str, Any]:
        prompt = (
            "You are a hiring report summarizer. Return JSON only with keys: "
            "executive_summary (string), recommendation_reasoning (array of strings), "
            "key_strengths (array of strings), key_risks (array of strings)."
        )
        parsed = await self._json_chat(system_prompt=prompt, user_payload=report_input, temperature=0.2)
        return {
            "executive_summary": str(parsed.get("executive_summary", "")).strip(),
            "recommendation_reasoning": [
                str(item) for item in parsed.get("recommendation_reasoning", []) if str(item).strip()
            ],
            "key_strengths": [str(item) for item in parsed.get("key_strengths", []) if str(item).strip()],
            "key_risks": [str(item) for item in parsed.get("key_risks", []) if str(item).strip()],
        }

    async def _json_chat(self, system_prompt: str, user_payload: dict[str, Any], temperature: float) -> dict[str, Any]:
        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=True)},
            ],
        )

        content = response.choices[0].message.content or "{}"
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise RuntimeError("LLM response was not a JSON object")
        return parsed

    @staticmethod
    def _clamp_score(value: Any) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(100.0, numeric))

    @staticmethod
    def _clamp_ratio(value: Any) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(1.0, numeric))

    @staticmethod
    def _env_int(key: str, default: int) -> int:
        raw = (os.getenv(key) or "").strip()
        if not raw:
            return default
        try:
            value = int(raw)
        except ValueError:
            return default
        return max(1, value)

    @staticmethod
    def _env_float(key: str, default: float) -> float:
        raw = (os.getenv(key) or "").strip()
        if not raw:
            return default
        try:
            value = float(raw)
        except ValueError:
            return default
        return max(1.0, value)
