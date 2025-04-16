from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import numpy as np
import uvicorn
from solow_model import solve_solow_model

app = FastAPI(title="China's Growth Game Economic Model API")

# Pydantic models for API requests and responses
class InitialConditions(BaseModel):
    Y: float
    K: float
    L: float
    H: float
    A: float
    NX: float

class Parameters(BaseModel):
    alpha: float
    delta: float
    g: float
    theta: float
    phi: float
    s: float  # Savings rate (set by students)
    beta: float
    n: float
    eta: float

class SimulationRequest(BaseModel):
    initial_year: int
    initial_conditions: InitialConditions
    parameters: Parameters
    years: List[int]
    historical_data: Optional[Dict] = None

class SimulationResponse(BaseModel):
    results: Dict[str, List[float]]

@app.get("/")
def read_root():
    return {"message": "China's Growth Game Economic Model API"}

@app.post("/simulate", response_model=SimulationResponse)
def run_simulation(request: SimulationRequest):
    try:
        # Convert pydantic models to dicts
        initial_conditions = request.initial_conditions.dict()
        parameters = request.parameters.dict()
        
        # Convert years list to numpy array
        years = np.array(request.years)
        
        # Run the Solow model simulation
        results_df = solve_solow_model(
            request.initial_year,
            initial_conditions,
            parameters,
            years,
            request.historical_data
        )
        
        # Convert results to dict for response
        results_dict = {
            column: results_df[column].tolist() 
            for column in results_df.columns
        }
        
        return {"results": results_dict}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 