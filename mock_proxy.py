import json
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    headers = dict(request.headers)
    body = await request.json()
    
    print("\n--- [MOCK PROXY] RECEIVED REQUEST ---")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Payload: {json.dumps(body, indent=2)}")
    print("---------------------------------------\n")
    
    # Check for Authorization header (validator's primary check)
    if not headers.get("authorization"):
        print("[MOCK PROXY] WARNING: Missing Authorization header!")
    
    # Return a generic mock response
    # Returning 'finish' allows inference.py to wrap up quickly during testing.
    return JSONResponse(content={
        "id": "mock-completion-123",
        "object": "chat.completion",
        "created": 123456789,
        "model": body.get("model", "mock-model"),
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": '{"action_type": "finish"}'
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 10,
            "total_tokens": 20
        }
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5050)
