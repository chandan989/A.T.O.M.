"""
Inference Script — A.T.O.M. (Agentic Trajectories for Optimizing Molecules)
===================================
MANDATORY
- Before submitting, ensure the following variables are defined in your environment configuration:
    API_BASE_URL   The API endpoint for the LLM.
    MODEL_NAME     The model identifier to use for inference.
    HF_TOKEN       Your Hugging Face / API key.
    LOCAL_IMAGE_NAME The name of the local image to use for the environment if you are using from_docker_image()
                     method

- Defaults are set only for API_BASE_URL and MODEL_NAME
    (and should reflect your active inference setup):
    API_BASE_URL = os.getenv("API_BASE_URL", "<your-active-endpoint>")
    MODEL_NAME = os.getenv("MODEL_NAME", "<your-active-model>")

- The inference script must be named `inference.py` and placed in the root directory of the project
- Participants must use OpenAI Client for all LLM calls using above variables

STDOUT FORMAT
- The script must emit exactly three line types to stdout, in this order:

    [START] task=<task_name> env=<benchmark> model=<model_name>
    [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
    [END]   success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>

  Rules:
    - One [START] line at episode begin.
    - One [STEP] line per step, immediately after env.step() returns.
    - One [END] line after env.close(), always emitted (even on exception).
    - reward and rewards are formatted to 2 decimal places.
    - done and success are lowercase booleans: true or false.
    - error is the raw last_action_error string, or null if none.
    - All fields on a single line with no newlines within a line.
    - Each tasks should return score in [0, 1]

  Example:
    [START] task=mol-opt-1 env=atom model=Qwen/Qwen2.5-72B-Instruct
    [STEP] step=1 action=get_valid_sites reward=0.00 done=false error=null
    [STEP] step=2 action=add_fragment(Methyl,0) reward=0.00 done=false error=null
    [STEP] step=3 action=finish reward=0.75 done=true error=null
    [END] success=true steps=3 score=0.75 rewards=0.00,0.00,0.75
"""

import json
import os
import re
import sys
import textwrap
from typing import Dict, Any, List, Optional

import httpx
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
# Phase-2 validators inject API_KEY; fall back to HF_TOKEN only for local dev.
API_KEY = os.getenv("API_KEY", "") or os.getenv("HF_TOKEN", "")

# Optional — if you use from_docker_image():
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

ATOM_SERVER_URL = os.getenv("ATOM_SERVER_URL", "http://localhost:8000")
ATOM_API_KEY = os.getenv("ATOM_API_KEY", "")

TASK_IDS = [1, 2, 3, 4]
BENCHMARK = os.getenv("ATOM_BENCHMARK", "atom")
TEMPERATURE = 0.1

# Debug: log the resolved configuration to stderr so validator logs can confirm
print(f"[CONFIG] API_BASE_URL={API_BASE_URL}", file=sys.stderr)
print(f"[CONFIG] MODEL_NAME={MODEL_NAME}", file=sys.stderr)
print(f"[CONFIG] API_KEY={'***' + API_KEY[-4:] if API_KEY and len(API_KEY) > 4 else '(not set)'}", file=sys.stderr)


# ══════════════════════════════════════════════════════════════
#  STDOUT LOGGING (strict format)
# ══════════════════════════════════════════════════════════════

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = "null" if not error else str(error).replace("\r", "\\r").replace("\n", "\\n")
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


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
#  ACTION → STRING (for log output)
# ══════════════════════════════════════════════════════════════

def action_to_str(action: Dict[str, Any]) -> str:
    action_type = action.get("action_type", "unknown")
    if action_type == "add_fragment":
        frag = action.get("fragment_name", "?")
        site = action.get("site_id", "?")
        return f"add_fragment({frag},{site})"
    if action_type == "remove_group":
        site = action.get("site_id", "?")
        return f"remove_group({site})"
    if action_type == "mutate_atom":
        site = action.get("site_id", "?")
        target = action.get("target_atom_symbol", "?")
        return f"mutate_atom({site},{target})"
    return action_type


# ══════════════════════════════════════════════════════════════
#  PROMPT CONSTRUCTION
# ══════════════════════════════════════════════════════════════

def build_prompt(observation: Dict[str, Any], valid_sites_cache: Optional[List],
                 action_history: List[Dict], step: int, max_steps: int) -> str:
    history_text = ""
    if action_history:
        history_text = "\n\nPrevious Actions & Results:\n"
        for h in action_history[-5:]:
            history_text += f"- Action: {json.dumps(h['action'])} → {h['feedback']} (reward: {h['reward']:.3f})\n"
        history_text += "\nUse this feedback to make BETTER choices. Avoid repeating actions that got low rewards.\n"

    if valid_sites_cache:
        return textwrap.dedent(f"""\
You are an expert medicinal chemist optimizing a molecule to match a Target Product Profile (TPP).

Current SMILES: {observation['current_smiles']}
Current Properties: {json.dumps(observation['current_properties'], indent=2)}
Target Profile (TPP): {json.dumps(observation['target_profile'], indent=2)}
Step: {step}/{max_steps}
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
or {{"action_type": "finish"}}""")
    else:
        return textwrap.dedent(f"""\
You are an expert medicinal chemist. Get the valid attachment sites first.

Current SMILES: {observation['current_smiles']}
Current Properties: {json.dumps(observation['current_properties'], indent=2)}
Target Profile (TPP): {json.dumps(observation['target_profile'], indent=2)}

Respond with ONLY JSON:
{{"action_type": "get_valid_sites"}}""")


def build_critic_prompt(observation: Dict[str, Any], proposed_action: Dict[str, Any]) -> str:
    return textwrap.dedent(f"""\
You are a medicinal chemistry critic. Review this proposed modification ONLY.

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
{{"action_type": "add_fragment", "fragment_name": "FragmentName", "site_id": 0}}""")


# ══════════════════════════════════════════════════════════════
#  SINGLE TASK RUNNER
# ══════════════════════════════════════════════════════════════

def run_task(client: SimpleAtomClient, llm: OpenAI, model_name: str, task_id: int) -> float:
    task_name = f"mol-opt-{task_id}"
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=task_name, env=BENCHMARK, model=model_name)

    try:
        obs = client.reset(task_id=task_id)
        observation = obs["observation"]
        max_steps = observation["max_steps"]

        valid_sites_cache: Optional[List] = None
        action_history: List[Dict] = []
        done = False

        for step in range(1, max_steps + 1):
            if observation.get("done", False):
                break

            if observation.get("valid_sites"):
                valid_sites_cache = observation["valid_sites"]

            prompt = build_prompt(observation, valid_sites_cache, action_history, step, max_steps)

            # Generator LLM call
            try:
                generator_resp = llm.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=TEMPERATURE,
                )
                proposed_action = parse_action(generator_resp.choices[0].message.content)
            except Exception:
                proposed_action = {"action_type": "finish"}

            # Critic (only for add_fragment)
            if proposed_action.get("action_type") in ("get_valid_sites", "finish"):
                final_action = proposed_action
            else:
                critic_prompt = build_critic_prompt(observation, proposed_action)
                try:
                    critic_resp = llm.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": critic_prompt}],
                        temperature=TEMPERATURE,
                    )
                    final_action = parse_action(critic_resp.choices[0].message.content)
                except Exception:
                    final_action = proposed_action

            # Sanitize action
            clean_action = {"action_type": final_action.get("action_type", "get_valid_sites")}
            if clean_action["action_type"] == "add_fragment":
                clean_action["fragment_name"] = final_action.get("fragment_name", "Methyl")
                clean_action["site_id"] = final_action.get("site_id", 0)

            # Execute action
            result = client.step(clean_action)

            if "error" in result:
                reward = 0.0
                done = False
                error_msg = result["error"]
                rewards.append(reward)
                steps_taken = step
                log_step(step=step, action=action_to_str(clean_action), reward=reward, done=done, error=error_msg)
                continue

            observation = result.get("observation", observation)
            reward = result.get("reward", 0.0)
            done = result.get("done", False)

            rewards.append(reward)
            steps_taken = step

            action_history.append({
                "action": clean_action,
                "feedback": observation.get("message", ""),
                "reward": reward,
            })

            log_step(step=step, action=action_to_str(clean_action), reward=reward, done=done, error=None)

            if done:
                break

        # If not done yet, auto-finish
        if not done:
            result = client.step({"action_type": "finish"})
            reward = result.get("reward", 0.0)
            done = True
            steps_taken += 1
            rewards.append(reward)
            log_step(step=steps_taken, action="finish", reward=reward, done=done, error=None)

        # Score is the final reward, clamped to [0, 1]
        score = reward if rewards else 0.0
        score = min(max(score, 0.0), 1.0)
        success = score > 0.0

    except Exception as exc:
        log_step(step=steps_taken + 1, action="error", reward=0.0, done=True, error=str(exc))
        steps_taken += 1

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    return score


# ══════════════════════════════════════════════════════════════
#  MAIN — Configurable via environment variables!
# ══════════════════════════════════════════════════════════════

def main():
    # Ensure we use api_key properly — if empty, use a placeholder so OpenAI
    # client does NOT fall back to OPENAI_API_KEY env var (which could bypass proxy).
    api_key = API_KEY if API_KEY else "no-key-provided"
    llm = OpenAI(base_url=API_BASE_URL, api_key=api_key)
    print(f"[CONFIG] OpenAI client initialized: base_url={llm.base_url}", file=sys.stderr)

    client = SimpleAtomClient(ATOM_SERVER_URL, ATOM_API_KEY)

    for task_id in TASK_IDS:
        run_task(client, llm, MODEL_NAME, task_id)


if __name__ == "__main__":
    main()
