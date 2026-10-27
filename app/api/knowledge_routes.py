from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from app.api.dependencies import get_auth_session
from app.knowledge.datasets.registry import dataset_registry, DatasetManifest
from app.knowledge.index.engine import knowledge_index
from app.knowledge.calculators.framework import calculator_registry, CalculatorResult

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Platform"])

@router.get("/datasets", response_model=List[DatasetManifest])
async def list_datasets(session=Depends(get_auth_session)):
    """Returns all registered datasets in the knowledge platform."""
    return dataset_registry.list_all()

@router.get("/search")
async def search_knowledge(
    q: str,
    category: Optional[str] = None,
    top_k: int = 5,
    session=Depends(get_auth_session)
):
    """Executes a hybrid search against the Knowledge Index."""
    filters = {"category": category} if category else None
    results = await knowledge_index.search(query=q, filters=filters, top_k=top_k)
    return {"query": q, "results": results}

@router.get("/calculators")
async def list_calculators(session=Depends(get_auth_session)):
    """Lists all available medical calculators."""
    return calculator_registry.list_all()

@router.post("/calculators/{calc_id}")
async def run_calculator(
    calc_id: str,
    inputs: Dict[str, Any],
    session=Depends(get_auth_session)
) -> CalculatorResult:
    """Executes a specific medical calculator deterministically."""
    calc = calculator_registry.get(calc_id)
    if not calc:
        raise HTTPException(status_code=404, detail="Calculator not found")
        
    try:
        result = calc.calculate(inputs)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
