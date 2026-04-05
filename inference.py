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
from openenv.core.env_server.client import EnvClient

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
        resp = httpx.post(f"{self.base_url}/env/step", json=action, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

def parse_action(response_text: str) -> Dict[str, Any]:
    try:
        # Simple extraction of JSON from response
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0]
        else:
            json_str = response_text
        return json.loads(json_str)
    except Exception as e:
        # Fallback to finish action if parsing fails to avoid crash
        print(f"Error parsing action: {e}. Text: {response_text}")
        return {"action_type": "finish"}

def run_task(client: SimpleAtomClient, llm: OpenAI, model_name: str, task_id: int):
    print(f"\n--- Starting Task {task_id} ---")

    obs = client.reset(task_id=task_id)
    observation = obs["observation"]

    max_steps = observation["max_steps"]

    for step in range(max_steps):
        # 1. Generator Proposes Action
        prompt = f"""
You are an expert medicinal chemist. Your goal is to optimize a molecule.
Current SMILES: {observation['current_smiles']}
Current Properties: {observation['current_properties']}
Target Profile (TPP): {observation['target_profile']}
Previous feedback: {observation['message']}

Available actions:
1. "get_valid_sites" -> returns valid_sites with descriptions.
2. "add_fragment" -> requires fragment_name (e.g. "Methyl", "Hydroxyl", "Fluorine", "Phenyl", "Trifluoromethyl", "Amino") and site_id (from get_valid_sites).
3. "finish" -> ends the optimization.

If you don't know the valid sites yet, you MUST use "get_valid_sites".
If you have valid sites, use "add_fragment".
If the TPP is satisfied, use "finish".

Respond ONLY with valid JSON in this format:
{{
  "action_type": "get_valid_sites" | "add_fragment" | "finish",
  "fragment_name": "string",
  "site_id": integer
}}
        """

        # Give context of valid sites if available
        if observation.get("valid_sites"):
            prompt += f"\n\nValid Sites:\n{json.dumps(observation['valid_sites'], indent=2)}"

        generator_resp = llm.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )

        proposed_action = parse_action(generator_resp.choices[0].message.content)
        print(f"Step {step+1}: Proposed Action: {proposed_action}")

        # 2. Critic Evaluates Proposed Action
        critic_prompt = f"""
You are an expert medicinal chemistry critic. Review the proposed action for a molecule optimization task.

Current SMILES: {observation['current_smiles']}
Proposed Action: {json.dumps(proposed_action)}

Critique the action on chemical validity, potential rule violations (like PAINS or Lipinski), and strategic value.
If the action is flawed, you can override it with a better action.
If the action is sound, output the exact same action.

Respond ONLY with valid JSON in this format:
{{
  "action_type": "get_valid_sites" | "add_fragment" | "finish",
  "fragment_name": "string",
  "site_id": integer
}}
        """

        critic_resp = llm.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": critic_prompt}],
            temperature=0.0
        )

        final_action = parse_action(critic_resp.choices[0].message.content)
        print(f"Step {step+1}: Critic Action: {final_action}")

        # 3. Execute Action
        result = client.step(final_action)
        observation = result["observation"]

        if observation["done"]:
            print(f"Task finished. Final Score: {result['reward']}")
            return result['reward']

    # Auto-finish if max steps reached without agent calling finish
    result = client.step({"action_type": "finish"})
    print(f"Task max steps reached. Final Score: {result['reward']}")
    return result['reward']

def main():
    api_key = os.environ.get("HF_TOKEN", "dummy")
    base_url = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
    model_name = os.environ.get("MODEL_NAME", "gpt-4o-mini")

    # ATOM server API key (generated on server boot, printed in console)
    atom_api_key = os.environ.get("ATOM_API_KEY", "")
    atom_server_url = os.environ.get("ATOM_SERVER_URL", "http://localhost:8000")

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
