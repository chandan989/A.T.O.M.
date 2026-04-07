# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

"""
Baseline inference script for ATOM Environment.
Runs a Dual-Agent (Generator + Critic) loop.
"""

import os
import json
import time
from typing import Dict, Any, List

from openai import OpenAI

# We mock EnvClient by importing the generated client or manually creating a thin wrapper.
# OpenEnv client expects standard http/ws calls to reset/step endpoints.
import httpx

class SimpleAtomClient:
    def __init__(self, base_url: str, api_key: str = ""):
        self.base_url = base_url
        self.headers = {}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def reset(self, task_id: int):
        resp = httpx.post(f"{self.base_url}/env/reset", params={"task_id": task_id}, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def step(self, action: Dict[str, Any]):
        resp = httpx.post(f"{self.base_url}/env/step", json={"action": action}, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

def parse_action(response_text: str) -> Dict[str, Any]:
    import re
    try:
        # Try structured ```json blocks first
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0]
            return json.loads(json_str)
        
        # Try to find any JSON object with action_type in the response
        # This handles verbose models that write explanations around the JSON
        matches = re.findall(r'\{[^{}]*"action_type"[^{}]*\}', response_text)
        if matches:
            return json.loads(matches[-1])  # Use the last match (usually the final answer)
        
        # Last resort: try parsing the whole thing
        return json.loads(response_text)
    except Exception as e:
        print(f"Error parsing action: {e}. Text: {response_text[:200]}...")
        return {"action_type": "get_valid_sites"}

def run_task(client: SimpleAtomClient, llm: OpenAI, model_name: str, task_id: int):
    print(f"\n--- Starting Task {task_id} ---")

    obs = client.reset(task_id=task_id)
    observation = obs["observation"]

    max_steps = observation["max_steps"]

    for step in range(max_steps):
        # 1. Generator Proposes Action
        prompt = f"""You are an expert medicinal chemist optimizing a molecule to match a Target Product Profile (TPP).

Current SMILES: {observation['current_smiles']}
Current Properties: {json.dumps(observation['current_properties'], indent=2)}
Target Profile (TPP): {json.dumps(observation['target_profile'], indent=2)}
Previous feedback: {observation['message']}
Step: {step+1}/{max_steps}

RULES:
- You MUST call "get_valid_sites" FIRST before any "add_fragment" action. This returns the valid site_id values.
- Only use "add_fragment" AFTER you have received valid_sites from a previous step.
- Use "finish" when you believe the TPP is satisfied or you cannot improve further.

Available fragment names (use EXACTLY these names, case-sensitive):
Halogens: Fluorine, Chlorine, Bromine, Trifluoromethyl, Trifluoromethoxy
Polar: Hydroxyl, Amino, Methylamino, Dimethylamino, Carboxyl, Methoxy, Ethoxy, Cyano, Nitro
Carbonyl: Formyl, Acetyl, Amide, Sulfonamide, Methylsulfonyl
Aliphatic: Methyl, Ethyl, Propyl, Isopropyl, tert-Butyl, Cyclopropyl
Aromatic: Phenyl, Pyridine, Thiophene, Imidazole, Pyrazole, Triazole

Respond with ONLY a JSON object, no explanation:
{{"action_type": "get_valid_sites"}}
or {{"action_type": "add_fragment", "fragment_name": "Methyl", "site_id": 0}}
or {{"action_type": "finish"}}"""

        # Give context of valid sites if available
        if observation.get("valid_sites"):
            prompt += f"\n\nValid Sites (use these site_id values):\n{json.dumps(observation['valid_sites'], indent=2)}"

        generator_resp = llm.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        proposed_action = parse_action(generator_resp.choices[0].message.content)
        print(f"Step {step+1}: Proposed Action: {proposed_action}")

        # 2. Critic — SKIP for reconnaissance/finish actions, only critique modifications
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

            critic_resp = llm.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": critic_prompt}],
                temperature=0.1
            )
            final_action = parse_action(critic_resp.choices[0].message.content)

        print(f"Step {step+1}: Final Action: {final_action}")

        # 3. Execute Action
        result = client.step(final_action)
        observation = result["observation"]

        if result.get("done", False) or result.get("observation", {}).get("done", False):
            reward = result.get("reward", 0.0)
            print(f"Task finished. Final Score: {reward}")
            return reward

    # Auto-finish if max steps reached without agent calling finish
    result = client.step({"action_type": "finish"})
    reward = result.get("reward", 0.0)
    print(f"Task max steps reached. Final Score: {reward}")
    return reward

def main():
    # ==============================================================
    # CONFIGURATION: Paste your keys between the quotes below!
    # ==============================================================
    
    # 1. Your Hugging Face Token (starts with hf_...)
    api_key = os.environ.get("HF_TOKEN", "")
    
    # 2. Your ATOM Server Key (from the Hugging Face Logs)
    atom_api_key = os.environ.get("ATOM_API_KEY", "d66af663a5b7f8282317329035869279c83deacc9188ee909d439a3c28b550aa")
    
    # 3. Your Space URL (No trailing slash)
    atom_server_url = os.environ.get("ATOM_SERVER_URL", "https://nikhhil07-atom-env.hf.space")

    # ==============================================================
    
    base_url = os.environ.get("API_BASE_URL", "https://router.huggingface.co/v1/")
    model_name = os.environ.get("MODEL_NAME", "meta-llama/Llama-4-Scout-17B-16E-Instruct")

    print(f"Using Model: {model_name}")
    print(f"Using API Base: {base_url}")
    print(f"Using ATOM Server: {atom_server_url}")

    # We will use the OpenAI client
    llm = OpenAI(api_key=api_key, base_url=base_url)

    # Connect to ATOM server with API key auth
    client = SimpleAtomClient(atom_server_url, api_key=atom_api_key)

    # Check if server is up
    try:
        httpx.get(f"{atom_server_url}/health")
    except Exception:
        print("Server not running. Start it with `python server/app.py`")
        return

    if atom_api_key:
        print("API key configured. Authenticating...")
    else:
        print("WARNING: No ATOM_API_KEY set. Requests may be rejected by the server.")

    scores = {}

    for task_id in [1, 2, 3, 4]:
        score = run_task(client, llm, model_name, task_id)
        scores[f"Task {task_id}"] = score

    print("\n=== Final Scores ===")
    for task, score in scores.items():
        print(f"{task}: {score:.4f}")

if __name__ == "__main__":
    main()
