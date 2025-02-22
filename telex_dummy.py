from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/slack-webhook")
async def mock_slack(request: Request):
    data = await request.json()
    print("\n📩 Received Slack Message:", data)
    return {"message": "Mock Slack received!"}

# Run this with: uvicorn slack_dummy:app --reload --port 5000
