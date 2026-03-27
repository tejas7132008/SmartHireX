from __future__ import annotations

import logging
import random
from dataclasses import asdict
from statistics import mean
from typing import Any, Dict, List, Tuple

from .config import SmartHireXConfig
from .models import GlobalHiringState, InterviewTurn

try:
    from app.integrations.brightdata_client import BrightDataError, fetch_page
except Exception:
    from integrations.brightdata_client import BrightDataError, fetch_page


logger = logging.getLogger("smarthirex")


DIMENSIONS = [
    "problem_framing",
    "data_judgement",
    "evaluation_design",
    "failure_analysis_and_iteration",
    "ml_system_delivery",
    "communication",
]

QUESTION_BANK = {
    "problem_framing": [
        "Tell me about a time you transformed a vague business request into a measurable ML problem.",
        "How do you decide which success metric is decision-relevant before building a model?",
        "Describe how you set guardrails before deploying a model that affects users.",
    ],
    "data_judgement": [
        "How did you detect that your training data stopped reflecting production behavior?",
        "Walk me through how you validate labels when stakes are high.",
        "What is your process for catching leakage before model training starts?",
    ],
    "evaluation_design": [
        "When is a random split misleading, and what do you use instead?",
        "How do you evaluate uncertainty and calibration before launch?",
        "Describe an evaluation plan you used to prevent silent regressions.",
    ],
    "failure_analysis_and_iteration": [
        "Share an example where your first model failed and how you diagnosed root cause.",
        "How do you design ablations that isolate the true failure driver?",
        "What is your loop for validating that a fix is robust and not a lucky seed?",
    ],
    "ml_system_delivery": [
        "How do you keep model-serving interfaces stable as experiments move quickly?",
        "What safeguards do you add to productionize a model safely?",
        "Describe your rollout and rollback strategy for risky ML changes.",
    ],
    "communication": [
        "How do you explain trade-offs to non-technical stakeholders during a deadline crunch?",
        "Describe how you communicate uncertainty when model evidence is mixed.",
        "Tell me about a time your documentation changed a project decision.",
    ],
}

RESPONSE_TEMPLATES = {
    "good": [
        "I start from the decision owner and define a measurable objective, then align offline metrics to online impact before implementation.",
        "I usually audit assumptions and define failure slices early, then iterate with clear acceptance thresholds.",
        "I can give a concrete example where we found a leakage path pre-launch and redesigned data collection to avoid it.",
    ],
    "average": [
        "I usually pick a practical baseline and iterate quickly, then tighten metrics once we have directional signal.",
        "I review major risks and document caveats, but I focus more on delivery speed than exhaustive analysis at first.",
        "I compare a few alternatives and move with the best-performing one, then improve monitoring after launch.",
    ],
    "poor": [
        "I mostly optimize for the top-line metric and adjust if issues appear later.",
        "I usually trust the available dataset and do deeper checks only when results look strange.",
        "I prefer trying model variants quickly instead of spending too much time on diagnostics.",
    ],
}


class CandidateDiscoveryAgent:
    def __init__(self, rng: random.Random, config: SmartHireXConfig):
        self.rng = rng
        self.config = config

    def _extract_web_signals(self, html: str) -> Dict[str, float]:
        lowered = html.lower()
        keywords = ["ai", "ml", "machine learning", "api", "llm", "backend", "python", "docker", "kubernetes"]
        keyword_hits = sum(1 for word in keywords if word in lowered)

        project_patterns = ["project", "repository", "repo", "case study", "portfolio"]
        project_mentions = sum(lowered.count(pat) for pat in project_patterns)

        activity_patterns = ["commit", "contribution", "star", "fork", "pull request", "issue"]
        activity_mentions = sum(lowered.count(pat) for pat in activity_patterns)

        project_hint = min(12.0, float(project_mentions) / 8.0)
        keyword_hint = min(10.0, float(keyword_hits))
        activity_hint = min(12.0, float(activity_mentions) / 10.0)

        return {
            "web_projects": project_hint,
            "keyword_strength": keyword_hint,
            "web_activity": activity_hint,
        }

    def _fallback_dynamic_web_signals(self, skills_count: int, projects_count: int) -> Dict[str, float]:
        # Dynamic fallback is intentionally random-bounded and seed-controlled via orchestrator RNG.
        return {
            "web_projects": min(12.0, max(0.0, 1.0 + projects_count * 0.8 + self.rng.uniform(0.0, 3.5))),
            "keyword_strength": min(10.0, max(0.0, 1.0 + skills_count * 0.7 + self.rng.uniform(0.0, 3.0))),
            "web_activity": min(12.0, max(0.0, 1.0 + self.rng.uniform(0.0, 5.0))),
        }

    def run(self, state: GlobalHiringState) -> Dict[str, Any]:
        logger.info("[SmartHireX] Analyzing candidate profile and supporting signals.")
        candidate = state.candidate
        skills = candidate.get("skills", [])
        years_exp = float(candidate.get("years_experience", 0))
        projects = candidate.get("projects", [])
        artifacts = candidate.get("artifacts", [])
        activity = candidate.get("activity", {})

        commits_per_week = float(activity.get("commits_per_week", 0))
        projects_completed = float(activity.get("projects_completed", 0))
        open_source_contributions = float(activity.get("open_source_contributions", 0))

        github_url = candidate.get("github_url")
        portfolio_url = candidate.get("portfolio_url")
        urls = [u for u in [github_url, portfolio_url] if isinstance(u, str) and u.strip()]

        web_signal_source = "fallback_dynamic"
        web_signals: Dict[str, float]
        if urls:
            logger.info("[SmartHireX] Fetching candidate data using Bright Data...")
            merged = {"web_projects": 0.0, "keyword_strength": 0.0, "web_activity": 0.0}
            successful_fetches = 0
            for url in urls:
                try:
                    html = fetch_page(url)
                    page_signals = self._extract_web_signals(html)
                    for k, v in page_signals.items():
                        merged[k] += v
                    successful_fetches += 1
                except BrightDataError as exc:
                    logger.warning("[SmartHireX] Bright Data fetch failed for %s: %s", url, exc)

            if successful_fetches > 0:
                web_signal_source = "brightdata"
                web_signals = {
                    k: round(v / successful_fetches, 3)
                    for k, v in merged.items()
                }
            else:
                web_signals = self._fallback_dynamic_web_signals(len(skills), len(projects))
        else:
            web_signals = self._fallback_dynamic_web_signals(len(skills), len(projects))

        web_projects = float(web_signals["web_projects"])
        keyword_strength = float(web_signals["keyword_strength"])
        web_activity = float(web_signals["web_activity"])

        baseline = min(
            0.95,
            0.32
            + 0.04 * years_exp
            + 0.02 * len(skills)
            + 0.03 * len(projects)
            + 0.03 * len(artifacts)
            + 0.004 * commits_per_week
            + 0.012 * projects_completed
            + 0.02 * open_source_contributions,
        )
        baseline += min(0.09, 0.005 * web_projects + 0.004 * keyword_strength + 0.003 * web_activity)
        baseline += self.rng.uniform(-0.08, 0.08)
        baseline = max(0.2, min(0.95, baseline))

        skill_score = max(0.05, min(0.99, 0.35 + 0.045 * len(skills) + self.rng.uniform(-0.06, 0.06)))
        initiative_score = max(
            0.05,
            min(
                0.99,
                0.30 + 0.04 * len(artifacts) + 0.004 * commits_per_week + self.rng.uniform(-0.06, 0.06),
            ),
        )
        consistency_score = max(
            0.05,
            min(
                0.99,
                0.30
                + 0.004 * commits_per_week
                + 0.02 * projects_completed
                + 0.03 * open_source_contributions
                + self.rng.uniform(-0.06, 0.06),
            ),
        )
        communication_score = max(
            0.05,
            min(0.99, 0.32 + 0.025 * len(projects) + 0.015 * len(artifacts) + self.rng.uniform(-0.06, 0.06)),
        )

        scores: Dict[str, float] = {}
        for dim in DIMENSIONS:
            drift = self.rng.uniform(-0.12, 0.12)
            score = max(0.05, min(0.99, baseline + drift))
            scores[dim] = round(score, 3)

        scores.update(
            {
                "skill": round(skill_score, 3),
                "initiative": round(initiative_score, 3),
                "consistency": round(consistency_score, 3),
                "communication": round((scores.get("communication", communication_score) + communication_score) / 2.0, 3),
            }
        )

        state.scores = scores
        state.reasoning_trace.append(
            "CandidateDiscoveryAgent: built initial score priors from candidate profile evidence."
        )
        if artifacts:
            state.reasoning_trace.append(
                "CandidateDiscoveryAgent: work artifacts increased technical evidence depth."
            )
        if activity:
            state.reasoning_trace.append(
                "CandidateDiscoveryAgent: activity signals increased confidence in consistency and initiative."
            )
        state.reasoning_trace.append(
            f"CandidateDiscoveryAgent: web signals source={web_signal_source}, projects={web_projects:.2f}, keywords={keyword_strength:.2f}, activity={web_activity:.2f}."
        )

        return {
            "name": candidate.get("name", "Unknown Candidate"),
            "target_role": candidate.get("target_role", "ML Engineer"),
            "years_experience": years_exp,
            "skills_count": len(skills),
            "projects_count": len(projects),
            "artifacts_count": len(artifacts),
            "activity_signal": {
                "commits_per_week": commits_per_week,
                "projects_completed": projects_completed,
                "open_source_contributions": open_source_contributions,
            },
            "web_signal": {
                "source": web_signal_source,
                "projects_detected": web_projects,
                "keyword_strength": keyword_strength,
                "activity_indicators": web_activity,
            },
            "reasoning": {
                "skill": "Estimated from explicit technical skills/projects and baseline quality signal.",
                "initiative": "Estimated from depth of artifacts and sustained development activity.",
                "consistency": "Estimated from weekly output regularity and completion behavior.",
                "communication": "Estimated from project articulation proxies and artifact narrative depth.",
                "web_signal": "Derived from Bright Data fetched pages when URLs are available; otherwise dynamic fallback simulation.",
            },
            "initial_signal_strength": round(mean(scores.values()), 3),
        }


class EvaluationAgent:
    def __init__(self, rng: random.Random, config: SmartHireXConfig):
        self.rng = rng
        self.config = config

    def evaluate_turn(
        self,
        state: GlobalHiringState,
        dimension: str,
        evaluation: Dict[str, float],
    ) -> float:
        response_score = evaluation["composite"]
        prior = state.scores[dimension]
        updated = 0.75 * prior + 0.25 * response_score
        state.scores[dimension] = round(max(0.01, min(0.99, updated)), 3)

        trend_point = round(mean(state.scores.values()), 3)
        state.performance_trend.append(trend_point)

        confidence = self._confidence(state)
        state.reasoning_trace.append(
            f"EvaluationAgent: updated {dimension} from {prior:.3f} to {state.scores[dimension]:.3f}; confidence={confidence:.3f}."
        )
        return confidence

    def _confidence(self, state: GlobalHiringState) -> float:
        if len(state.performance_trend) < 2:
            return 0.45

        recent = state.performance_trend[-4:]
        stability = 1.0 - min(1.0, (max(recent) - min(recent)) * 2.2)
        quality = mean(state.scores.values())
        confidence = 0.55 * quality + 0.45 * stability
        return round(max(0.0, min(1.0, confidence)), 3)


class InterviewAgent:
    def __init__(self, rng: random.Random, config: SmartHireXConfig):
        self.rng = rng
        self.config = config

    def run_loop(
        self,
        state: GlobalHiringState,
        evaluator: EvaluationAgent,
    ) -> Dict[str, Any]:
        logger.info("[SmartHireX] Running adaptive interview.")
        interview_cfg = self.config.interview
        min_turns = interview_cfg["min_turns"]
        max_turns = interview_cfg["max_turns"]
        target_confidence = interview_cfg["stop_criteria"]["confidence_target"]

        difficulty = 2
        last_confidence = 0.45

        while True:
            turn_number = len(state.interview_history) + 1
            dimension = self._select_focus_dimension(state)
            question = self._generate_question(dimension, difficulty, turn_number)
            response, quality_label, response_score = self._simulate_response(state, difficulty)
            evaluation, evaluation_reasoning = self._evaluate_response(response_score, difficulty)

            last_confidence = evaluator.evaluate_turn(state, dimension, evaluation)

            state.interview_history.append(
                InterviewTurn(
                    turn=turn_number,
                    dimension=dimension,
                    difficulty=difficulty,
                    question=question,
                    response=response,
                    response_quality=quality_label,
                    response_score=round(response_score, 3),
                    evaluation=evaluation,
                    evaluation_reasoning=evaluation_reasoning,
                    running_confidence=last_confidence,
                )
            )

            state.reasoning_trace.append(
                f"InterviewAgent: turn={turn_number}, dimension={dimension}, difficulty={difficulty}, quality={quality_label}."
            )

            difficulty = self._adjust_difficulty(difficulty, response_score)

            if self._should_stop(state, last_confidence, min_turns, max_turns, target_confidence):
                break

        return {
            "turns": [asdict(t) for t in state.interview_history],
            "turn_count": len(state.interview_history),
            "final_confidence": last_confidence,
            "final_difficulty": difficulty,
            "performance_trend": state.performance_trend,
        }

    def _select_focus_dimension(self, state: GlobalHiringState) -> str:
        interview_scores = {k: state.scores[k] for k in DIMENSIONS if k in state.scores}
        ordered = sorted(interview_scores.items(), key=lambda x: x[1])
        low_band = ordered[:2]
        return self.rng.choice(low_band)[0]

    def _generate_question(self, dimension: str, difficulty: int, turn_number: int) -> str:
        base = self.rng.choice(QUESTION_BANK[dimension])
        if difficulty >= 4:
            return f"Turn {turn_number} (advanced): {base} Please include trade-offs and what evidence would change your plan."
        if difficulty <= 2:
            return f"Turn {turn_number} (foundational): {base}"
        return f"Turn {turn_number} (intermediate): {base} Please share one concrete example."

    def _simulate_response(self, state: GlobalHiringState, difficulty: int) -> Tuple[str, str, float]:
        profile_strength = mean(state.scores.values())
        artifacts = state.candidate.get("artifacts", [])
        activity = state.candidate.get("activity", {})

        artifact_bonus = min(0.12, 0.025 * len(artifacts))
        activity_bonus = min(
            0.10,
            0.003 * float(activity.get("commits_per_week", 0))
            + 0.01 * float(activity.get("projects_completed", 0))
            + 0.015 * float(activity.get("open_source_contributions", 0)),
        )
        pressure_penalty = max(0.0, (difficulty - 3) * 0.08)
        volatility = self.rng.uniform(-0.2, 0.2)
        latent_quality = profile_strength + artifact_bonus + activity_bonus - pressure_penalty + volatility

        if latent_quality >= 0.72:
            quality = "good"
            score = self.rng.uniform(0.74, 0.97)
        elif latent_quality >= 0.48:
            quality = "average"
            score = self.rng.uniform(0.45, 0.75)
        else:
            quality = "poor"
            score = self.rng.uniform(0.15, 0.52)

        candidate_name = state.candidate.get("name", "the candidate")
        response = f"{candidate_name}: {self.rng.choice(RESPONSE_TEMPLATES[quality])}"
        return response, quality, score

    def _evaluate_response(self, response_score: float, difficulty: int) -> Tuple[Dict[str, float], str]:
        correctness = max(0.0, min(1.0, response_score + self.rng.uniform(-0.05, 0.05)))
        thinking = max(0.0, min(1.0, response_score + (difficulty - 3) * 0.04 + self.rng.uniform(-0.08, 0.08)))
        clarity = max(0.0, min(1.0, response_score + self.rng.uniform(-0.1, 0.1)))
        consistency = max(0.0, min(1.0, response_score + self.rng.uniform(-0.07, 0.07)))
        composite = 0.35 * correctness + 0.30 * thinking + 0.20 * clarity + 0.15 * consistency

        evaluation = {
            "correctness": round(correctness, 3),
            "thinking": round(thinking, 3),
            "clarity": round(clarity, 3),
            "consistency": round(consistency, 3),
            "composite": round(composite, 3),
        }
        reasoning = (
            "Composite built from correctness, structured thinking, clarity, and consistency; "
            f"difficulty={difficulty} influenced thinking pressure."
        )
        return evaluation, reasoning

    def _adjust_difficulty(self, difficulty: int, response_score: float) -> int:
        scaling = self.config.interview["difficulty_scaling"]
        increase_if = float(scaling["increase_if_score_above"]) / 10.0
        decrease_if = float(scaling["decrease_if_score_below"]) / 10.0

        if response_score > increase_if:
            return min(5, difficulty + 1)
        if response_score < decrease_if:
            return max(1, difficulty - 1)
        return difficulty

    def _should_stop(
        self,
        state: GlobalHiringState,
        confidence: float,
        min_turns: int,
        max_turns: int,
        target_confidence: float,
    ) -> bool:
        turn_count = len(state.interview_history)
        if turn_count >= max_turns:
            state.reasoning_trace.append("InterviewAgent: stop triggered by max_turns limit.")
            return True

        if turn_count < min_turns:
            return False

        stability_window = int(self.config.interview["stop_criteria"]["stability_window"])
        recent = state.performance_trend[-stability_window:]
        stable = len(recent) == stability_window and (max(recent) - min(recent)) < 0.03
        confident = confidence >= target_confidence

        if stable and confident:
            state.reasoning_trace.append(
                "InterviewAgent: stop triggered by stable trend and sufficient confidence."
            )
            return True
        return False


class DecisionAgent:
    def __init__(self, rng: random.Random, config: SmartHireXConfig):
        self.rng = rng
        self.config = config

    def run(self, state: GlobalHiringState) -> Tuple[str, Dict[str, Dict[str, Any]]]:
        logger.info("[SmartHireX] Running stakeholder decision process.")
        overall = mean(state.scores.values())
        communication = state.scores.get("communication", overall)
        delivery = state.scores.get("ml_system_delivery", overall)
        technical = mean(
            [
                state.scores.get("problem_framing", overall),
                state.scores.get("data_judgement", overall),
                state.scores.get("evaluation_design", overall),
                state.scores.get("failure_analysis_and_iteration", overall),
            ]
        )
        consistency = state.scores.get("consistency", overall)
        artifacts = state.candidate.get("artifacts", [])
        activity = state.candidate.get("activity", {})

        evidence_bonus = min(0.08, 0.015 * len(artifacts))
        consistency_bonus = min(
            0.06,
            0.002 * float(activity.get("commits_per_week", 0))
            + 0.01 * float(activity.get("open_source_contributions", 0)),
        )
        adjusted_overall = max(0.0, min(1.0, overall + evidence_bonus + consistency_bonus))

        technical_10 = technical * 10.0
        communication_10 = communication * 10.0
        consistency_10 = consistency * 10.0

        hard_fail_reasons: List[str] = []
        if communication_10 < 4.0 and consistency_10 < 4.0:
            hard_fail_reasons.append("communication_score < 4 AND consistency_score < 4")
        if technical_10 < 3.0:
            hard_fail_reasons.append("technical_score < 3")

        recruiter_agent = RecruiterAgent(self.rng, self.config)
        hiring_manager_agent = HiringManagerAgent(self.rng, self.config)
        tech_lead_agent = TechLeadAgent(self.rng, self.config)

        stakeholders = {
            "recruiter": recruiter_agent.vote(adjusted_overall, communication),
            "hiring_manager": hiring_manager_agent.vote(adjusted_overall, delivery),
            "tech_lead": tech_lead_agent.vote(adjusted_overall, state.scores),
        }

        recruiter_veto = communication_10 < 3.0
        tech_veto = technical_10 < 3.0
        if recruiter_veto:
            stakeholders["recruiter"]["reason"] += " Recruiter veto triggered (communication < 3)."
        if tech_veto:
            stakeholders["tech_lead"]["reason"] += " Tech lead veto triggered (technical < 3)."

        votes = [v["decision"] for v in stakeholders.values()]
        final_decision, disagreement_summary = self._aggregate(
            votes=votes,
            weighted_score=self._weighted_score(stakeholders),
            technical_score=technical,
            recruiter_veto=recruiter_veto,
            tech_veto=tech_veto,
            hard_fail=bool(hard_fail_reasons),
        )

        state.final_decision = final_decision
        state.stakeholder_decisions = stakeholders
        state.reasoning_trace.append(
            f"DecisionAgent: stakeholders voted {votes}; final_decision={final_decision}."
        )
        if disagreement_summary:
            state.reasoning_trace.append(f"DecisionAgent: {disagreement_summary}")
        if hard_fail_reasons:
            state.reasoning_trace.append(f"DecisionAgent: hard fail conditions met: {hard_fail_reasons}")
        return final_decision, stakeholders

    def _vote(self, base_score: float, noise: float, rationale: str) -> Dict[str, Any]:
        adjusted = max(0.0, min(1.0, base_score + self.rng.uniform(-noise, noise)))
        decision = self._label_from_threshold(adjusted)

        return {
            "decision": decision,
            "score": round(adjusted, 3),
            "reason": f"{rationale} Confidence={adjusted:.2f} from observed evidence.",
        }

    def _aggregate(
        self,
        votes: List[str],
        weighted_score: float,
        technical_score: float,
        recruiter_veto: bool,
        tech_veto: bool,
        hard_fail: bool,
    ) -> Tuple[str, str]:
        disagreement_summary = ""
        if hard_fail or recruiter_veto or tech_veto:
            return "reject", "Hard fail/veto policy triggered immediate rejection."

        if len(set(votes)) > 1:
            disagreement_summary = "Stakeholder disagreement detected; resolved using weighted consensus plus overall evidence score."
        if votes.count("strong_hire") >= 2:
            return "strong_hire", disagreement_summary
        if votes.count("reject") >= 2:
            return "reject", disagreement_summary
        if votes.count("hire") + votes.count("strong_hire") >= 2:
            return "hire", disagreement_summary

        if self.config.decision["tie_break_policy"] == "favor_tech_strength_unless_hr_veto" and technical_score >= 0.7:
            return "hire", disagreement_summary

        return self._label_from_threshold(weighted_score), disagreement_summary

    def _weighted_score(self, stakeholders: Dict[str, Dict[str, Any]]) -> float:
        weights = self.config.stakeholders["weights"]
        return (
            stakeholders["recruiter"]["score"] * float(weights["recruiter"])
            + stakeholders["hiring_manager"]["score"] * float(weights["hiring_manager"])
            + stakeholders["tech_lead"]["score"] * float(weights["tech_lead"])
        )

    def _label_from_threshold(self, value: float) -> str:
        thresholds = self.config.decision["confidence_thresholds"]
        if value >= float(thresholds["strong_hire"]):
            return "strong_hire"
        if value >= float(thresholds["hire"]):
            return "hire"
        if value >= float(thresholds["hold"]):
            return "hold"
        return "reject"


class RecruiterAgent(DecisionAgent):
    def vote(self, adjusted_overall: float, communication: float) -> Dict[str, Any]:
        weighted = adjusted_overall * 0.65 + communication * 0.35
        return self._vote(weighted, 0.05, "Recruiter emphasis on communication and delivery readiness.")


class HiringManagerAgent(DecisionAgent):
    def vote(self, adjusted_overall: float, delivery: float) -> Dict[str, Any]:
        weighted = adjusted_overall * 0.55 + delivery * 0.45
        return self._vote(weighted, 0.03, "Hiring manager emphasis on execution reliability and team impact.")


class TechLeadAgent(DecisionAgent):
    def vote(self, adjusted_overall: float, scores: Dict[str, float]) -> Dict[str, Any]:
        technical = mean(
            [
                scores.get("problem_framing", adjusted_overall),
                scores.get("data_judgement", adjusted_overall),
                scores.get("evaluation_design", adjusted_overall),
                scores.get("failure_analysis_and_iteration", adjusted_overall),
            ]
        )
        weighted = adjusted_overall * 0.50 + technical * 0.50
        return self._vote(weighted, 0.04, "Tech lead emphasis on technical depth and debugging rigor.")
