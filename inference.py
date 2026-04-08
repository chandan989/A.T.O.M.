"""
A.T.O.M. — Agentic Trajectories for Optimizing Molecules
Baseline Inference Script

Structured stdout logs follow [START], [STEP], [END] format for automated evaluation.
Uses OpenAI Client for all LLM calls as required.
"""

import os
import json
import re
import httpx
from typing import Dict, Any, List, Optional
from openai import OpenAI


# ══════════════════════════════════════════════════════════════
#  ENVIRONMENT CLIENT
# ══════════════════════════════════════════════════════════════

class SimpleAtomClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Content-Type": "application/json",
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def reset(self, task_id: int = 1):
        resp = httpx.post(
            f"{self.base_url}/env/reset",
            params={"task_id": task_id},
            headers=self.headers,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def step(self, action: Dict[str, Any]):
        resp = httpx.post(
            f"{self.base_url}/env/step",
            json={"action": action},
            headers=self.headers,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()


# ══════════════════════════════════════════════════════════════
#  ACTION PARSING (robust JSON extraction for verbose LLMs)
# ══════════════════════════════════════════════════════════════

def parse_action(response_text: str) -> Dict[str, Any]:
    try:
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0]
            return json.loads(json_str)

        matches = re.findall(r'\{[^{}]*"action_type"[^{}]*\}', response_text)
        if matches:
            return json.loads(matches[-1])

        return json.loads(response_text)
    except Exception:
        return {"action_type": "get_valid_sites"}


# ══════════════════════════════════════════════════════════════
#  SINGLE TASK RUNNER
# ══════════════════════════════════════════════════════════════

def run_task(
    client: SimpleAtomClient,
    llm: OpenAI,
    model_name: str,
    task_id: int,
) -> float:
    # ── Reset environment ─────────────────────────────────────
    obs = client.reset(task_id=task_id)
    observation = obs["observation"]
    max_steps = observation["max_steps"]

    # Structured log: [START]
    print(json.dumps({
        "event": "[START]",
        "task_id": task_id,
        "max_steps": max_steps,
        "starting_smiles": observation["current_smiles"],
        "target_profile": observation["target_profile"],
    }))

    valid_sites_cache: Optional[List] = None
    action_history: List[Dict] = []  # Track past actions + rewards for ICL

    for step in range(max_steps):
        # Track valid sites across steps
        if observation.get("valid_sites"):
            valid_sites_cache = observation["valid_sites"]

        # ── Build feedback from history ───────────────────────
        history_text = ""
        if action_history:
            history_text = "\n\nPrevious Actions & Results:\n"
            for h in action_history[-5:]:  # Last 5 actions to stay within context
                history_text += f"- Action: {json.dumps(h['action'])} → {h['feedback']} (reward: {h['reward']:.3f})\n"
            history_text += "\nUse this feedback to make BETTER choices. Avoid repeating actions that got low rewards.\n"

        # ── Build prompt with ICL feedback ────────────────────
        if valid_sites_cache:
            prompt = f"""You are an expert medicinal chemist optimizing a molecule to match a Target Product Profile (TPP).

Current SMILES: {observation['current_smiles']}
Current Properties: {json.dumps(observation['current_properties'], indent=2)}
Target Profile (TPP): {json.dumps(observation['target_profile'], indent=2)}
Step: {step+1}/{max_steps}
{history_text}
You ALREADY have valid sites. You MUST use "add_fragment" now. Do NOT call "get_valid_sites" again.
Analyze the GAP between current properties and target ranges. Pick the fragment that closes the biggest gap.

Valid Sites:
{json.dumps(valid_sites_cache, indent=2)}

Available fragments (case-sensitive):
- To INCREASE LogP: Methyl, Ethyl, Propyl, Isopropyl, tert-Butyl, Phenyl, Trifluoromethyl, Chlorine, Fluorine
- To DECREASE LogP: Hydroxyl, Amino, Carboxyl, Cyano, Amide, Morpholine
- To INCREASE MW: Phenyl, Cyclohexyl, Naphthalene, Indole, Piperidine
- To fine-tune: Methoxy, Cyclopropyl, Pyridine, Thiophene, Acetyl

Respond with ONLY JSON, no explanation:
{{"action_type": "add_fragment", "fragment_name": "Methyl", "site_id": 0}}
or {{"action_type": "finish"}}"""
        else:
            prompt = f"""You are an expert medicinal chemist. Get the valid attachment sites first.

Current SMILES: {observation['current_smiles']}
Current Properties: {json.dumps(observation['current_properties'], indent=2)}
Target Profile (TPP): {json.dumps(observation['target_profile'], indent=2)}

Respond with ONLY JSON:
{{"action_type": "get_valid_sites"}}"""

        # ── Generator LLM call ────────────────────────────────
        try:
            generator_resp = llm.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
            proposed_action = parse_action(generator_resp.choices[0].message.content)
        except Exception as e:
            proposed_action = {"action_type": "finish"}

        # ── Critic (only for add_fragment) ────────────────────
        if proposed_action.get("action_type") in ("get_valid_sites", "finish"):
            final_action = proposed_action
        else:
            critic_prompt = f"""You are a medicinal chemistry critic. Review this proposed modification ONLY.

Current SMILES: {observation['current_smiles']}
Current Properties: {json.dumps(observation.get('current_properties', {}), indent=2)}
Target Profile (TPP): {json.dumps(observation.get('target_profile', {}), indent=2)}
Proposed Action: {json.dumps(proposed_action)}

RULES:
- Check: Is the fragment_name valid? Will this move properties CLOSER to TPP ranges?
- If the fragment choice is poor, suggest a BETTER fragment but keep the same site_id.
- If the action is sound, output the EXACT same action.
- Valid fragments: Fluorine, Chlorine, Trifluoromethyl, Hydroxyl, Amino, Methyl, Ethyl, Propyl, Isopropyl, tert-Butyl, Methoxy, Cyano, Phenyl, Pyridine, Cyclopropyl, Acetyl, Amide

Respond with ONLY a JSON object:
{{"action_type": "add_fragment", "fragment_name": "FragmentName", "site_id": 0}}"""

            try:
                critic_resp = llm.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": critic_prompt}],
                    temperature=0.1,
                )
                final_action = parse_action(critic_resp.choices[0].message.content)
            except Exception:
                final_action = proposed_action

        # ── Sanitize action ───────────────────────────────────
        clean_action = {"action_type": final_action.get("action_type", "get_valid_sites")}
        if clean_action["action_type"] == "add_fragment":
            clean_action["fragment_name"] = final_action.get("fragment_name", "Methyl")
            clean_action["site_id"] = final_action.get("site_id", 0)

        # ── Execute action ────────────────────────────────────
        result = client.step(clean_action)
        if "error" in result:
            # Structured log: [STEP] with error
            print(json.dumps({
                "event": "[STEP]",
                "task_id": task_id,
                "step": step + 1,
                "action": clean_action,
                "error": result["error"],
                "reward": 0.0,
            }))
            continue

        observation = result.get("observation", observation)
        reward = result.get("reward", 0.0)
        done = result.get("done", False)

        # ── Record to history for ICL feedback loop ───────────
        action_history.append({
            "action": clean_action,
            "feedback": observation.get("message", ""),
            "reward": reward,
        })

        # Structured log: [STEP]
        print(json.dumps({
            "event": "[STEP]",
            "task_id": task_id,
            "step": step + 1,
            "action": clean_action,
            "smiles": observation.get("current_smiles", ""),
            "properties": observation.get("current_properties", {}),
            "message": observation.get("message", ""),
            "reward": reward,
            "done": done,
        }))

        if done:
            # Structured log: [END]
            print(json.dumps({
                "event": "[END]",
                "task_id": task_id,
                "final_smiles": observation.get("current_smiles", ""),
                "final_properties": observation.get("current_properties", {}),
                "final_score": reward,
                "steps_taken": step + 1,
            }))
            return reward

    # Auto-finish if max steps reached
    result = client.step({"action_type": "finish"})
    reward = result.get("reward", 0.0)

    # Structured log: [END]
    print(json.dumps({
        "event": "[END]",
        "task_id": task_id,
        "final_smiles": result.get("observation", {}).get("current_smiles", ""),
        "final_properties": result.get("observation", {}).get("current_properties", {}),
        "final_score": reward,
        "steps_taken": max_steps,
    }))
    return reward


# ══════════════════════════════════════════════════════════════
#  MAIN — Configurable via environment variables
# ══════════════════════════════════════════════════════════════

def main():
    # Required environment variables (per hackathon spec)
    api_key = os.environ.get("HF_TOKEN", "")
    base_url = os.environ.get("API_BASE_URL", "https://router.huggingface.co/v1/")
    model_name = os.environ.get("MODEL_NAME", "meta-llama/Llama-3.3-70B-Instruct")

    # ATOM Server configuration
    atom_api_key = os.environ.get("ATOM_API_KEY", "")
    atom_server_url = os.environ.get("ATOM_SERVER_URL", "http://localhost:8000")

    print(f"Using Model: {model_name}")
    print(f"Using API Base: {base_url}")
    print(f"Using ATOM Server: {atom_server_url}")

    # Initialize OpenAI client pointing to HF Router
    llm = OpenAI(base_url=base_url, api_key=api_key)

    # Initialize ATOM environment client
    client = SimpleAtomClient(atom_server_url, atom_api_key)

    # Verify connection
    if atom_api_key:
        try:
            resp = httpx.get(
                f"{atom_server_url}/auth/verify",
                headers={"Authorization": f"Bearer {atom_api_key}"},
                timeout=10,
            )
            if resp.status_code == 200:
                print("API key configured. Authenticating... OK")
            else:
                print(f"WARNING: Auth verification returned {resp.status_code}")
        except Exception as e:
            print(f"WARNING: Could not verify auth: {e}")

    # Run all 4 tasks
    scores = {}
    for task_id in [1, 2, 3, 4]:
        try:
            score = run_task(client, llm, model_name, task_id)
            scores[task_id] = score
        except Exception as e:
            print(json.dumps({
                "event": "[END]",
                "task_id": task_id,
                "error": str(e),
                "final_score": 0.0,
            }))
            scores[task_id] = 0.0

    # Final summary
    print("\n=== Final Scores ===")
    for tid, score in scores.items():
        print(f"Task {tid}: {score:.4f}")


if __name__ == "__main__":
    main()
