import uvicorn
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/env/reset")
async def reset(task_id: int):
    return {
        "observation": {
            "current_smiles": "C",
            "current_properties": {"MW": 16.0, "LogP": 1.0},
            "target_profile": {"MW": [100, 200], "LogP": [2, 3]},
            "max_steps": 5,
            "valid_sites": [{"site_id": 0, "atom_index": 0}]
        }
    }

@app.post("/env/step")
async def step(request: Request):
    return {
        "observation": {
            "current_smiles": "CC",
            "current_properties": {"MW": 30.0, "LogP": 1.5},
            "target_profile": {"MW": [100, 200], "LogP": [2, 3]},
        },
        "reward": 0.5,
        "done": True
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
