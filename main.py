from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic
from anthropic import HUMAN_PROMPT, AI_PROMPT
import os
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Anthropic client for v0.2.10
api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"DEBUG: API key from environment: {'Found' if api_key else 'Not found'}")
print(f"DEBUG: All environment variables: {list(os.environ.keys())}")

if not api_key:
    print("ERROR: ANTHROPIC_API_KEY not found in environment!")
    raise HTTPException(status_code=500, detail="API key not configured")

print(f"DEBUG: API key loaded successfully")
client = anthropic.Client(api_key)

class RelationshipSituation(BaseModel):
    situation: str

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/philosophy-mix")
async def get_philosophy_mix():
    philosophy_weights = {
        'christian': 0.30,
        'buddhist': 0.30,
        'taoist': 0.10,
        'secular_humanist': 0.10,
        'stoic': 0.20
    }
    
    philosophy_display = {}
    display_names = {
        'christian': 'Christian',
        'buddhist': 'Buddhist',
        'taoist': 'Taoist',
        'secular_humanist': 'Secular Humanist',
        'stoic': 'Stoic'
    }
    
    for philosophy, weight in philosophy_weights.items():
        philosophy_display[philosophy] = {
            'name': display_names[philosophy],
            'percentage': round(weight * 100, 1),
            'weight': weight
        }
    
    return {
        'philosophy_mix': philosophy_display,
        'total_traditions': len(philosophy_weights),
        'description': 'Babushka draws wisdom from diverse global traditions.'
    }

@app.post("/advice")
async def get_relationship_advice(situation: RelationshipSituation):
    try: 
        print(f"DEBUG: Received situation: {situation.situation}")
        
        philosophy_weights = {
            'christian': 0.30,
            'buddhist': 0.30,
            'taoist': 0.10,
            'secular_humanist': 0.10,
            'stoic': 0.20
        }
        
        available_philosophies = [k for k, v in philosophy_weights.items() if v > 0]
        available_weights = [philosophy_weights[k] for k in available_philosophies]
        
        selected_philosophies = random.choices(
            available_philosophies,
            weights=available_weights,
            k=min(3, len(available_philosophies))
        )
        
        print(f"DEBUG: Selected philosophies: {selected_philosophies}")
        
        philosophy_prompts = {
            'christian': "Focus on love, forgiveness, patience, and treating others with dignity and respect.",
            'buddhist': "Emphasize compassion, wisdom, truth, emancipation from earthly desires and delusion.",
            'taoist': "Emphasize natural flow, balance, not forcing situations, and finding harmony.",
            'secular_humanist': "Focus on reason, empathy, human dignity, and evidence-based problem solving.",
            'stoic': "Emphasize acceptance of what you cannot control and focusing on your own actions and responses."
        }
        
        philosophy_guidance = "\n".join([
            f"- {philosophy_prompts[phil]}" for phil in selected_philosophies
        ])
        
        prompt = f"""You are Babushka, a wise relationship advisor who draws from the collective wisdom of many cultures and generations. You speak with the warm, caring voice of a grandmother who has seen many relationships succeed and fail.

Your advice should incorporate these philosophical perspectives:
{philosophy_guidance}

Situation: {situation.situation}

Provide warm, practical relationship advice that:
1. Shows empathy and understanding
2. Offers concrete, actionable steps
3. Draws from traditional wisdom while being relevant to modern relationships
4. Is encouraging but realistic
5. Uses gentle, grandmother-like language

Keep your response between 100-200 words. Address the person as "dearest child" or similar endearing terms."""

        print("DEBUG: About to call Anthropic API")
        
        response = client.completion(
            prompt=f"{HUMAN_PROMPT} {prompt}{AI_PROMPT}",
            model="claude-instant-1",
            max_tokens_to_sample=300,
            stop_sequences=[HUMAN_PROMPT]
        )

        print(f"DEBUG: Anthropic response received successfully")
        return {"advice": response["completion"]}
        
    except Exception as e:
        print(f"DEBUG: Exception caught: {str(e)}")
        print(f"DEBUG: Exception type: {type(e)}")
        import traceback
        print(f"DEBUG: Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error generating advice: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
