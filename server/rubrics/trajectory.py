# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

"""
Trajectory tracking for ATOM environment.
"""

from typing import Dict, Any, List

class TrajectoryTracker:
    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    def add_step(self, action_dict: Dict[str, Any], properties: Dict[str, float], is_valid: bool):
        self.history.append({
            "action": action_dict,
            "properties": properties,
            "is_valid": is_valid
        })

    def get_summary(self) -> Dict[str, Any]:
        """Provides a running summary of the trajectory."""
        if not self.history:
            return {}

        fragments_used = set(step.get("action", {}).get("fragment_name") for step in self.history if step.get("action", {}).get("fragment_name"))

        return {
            "steps": len(self.history),
            "fragments_used": list(fragments_used),
            "valid_steps": sum(1 for step in self.history if step["is_valid"])
        }
