from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class CalculatorInput(BaseModel):
    name: str
    description: str
    unit: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    type: str = "number"  # "number", "boolean", "enum"
    options: Optional[List[str]] = None

class CalculatorResult(BaseModel):
    score: float
    interpretation: str
    evidence_reference: Optional[str] = None
    metadata: Dict[str, Any] = {}

class MedicalCalculator(ABC):
    @property
    @abstractmethod
    def id(self) -> str: pass
    
    @property
    @abstractmethod
    def name(self) -> str: pass
    
    @property
    @abstractmethod
    def version(self) -> str: pass
    
    @property
    @abstractmethod
    def description(self) -> str: pass
    
    @property
    @abstractmethod
    def required_inputs(self) -> List[CalculatorInput]: pass
    
    @abstractmethod
    def calculate(self, inputs: Dict[str, Any]) -> CalculatorResult:
        """Computes the score deterministically."""
        pass

class BMICalculator(MedicalCalculator):
    @property
    def id(self) -> str: return "bmi"
    @property
    def name(self) -> str: return "Body Mass Index"
    @property
    def version(self) -> str: return "1.0"
    @property
    def description(self) -> str: return "Calculates Body Mass Index from height and weight."
    
    @property
    def required_inputs(self) -> List[CalculatorInput]:
        return [
            CalculatorInput(name="weight_kg", description="Weight in kilograms", unit="kg", min_value=1.0),
            CalculatorInput(name="height_cm", description="Height in centimeters", unit="cm", min_value=10.0)
        ]
        
    def calculate(self, inputs: Dict[str, Any]) -> CalculatorResult:
        weight = float(inputs.get("weight_kg", 0))
        height_m = float(inputs.get("height_cm", 0)) / 100.0
        
        if height_m <= 0:
            raise ValueError("Height must be positive.")
            
        bmi = weight / (height_m * height_m)
        
        if bmi < 18.5:
            interp = "Underweight"
        elif bmi < 25:
            interp = "Normal weight"
        elif bmi < 30:
            interp = "Overweight"
        else:
            interp = "Obese"
            
        return CalculatorResult(
            score=round(bmi, 1),
            interpretation=interp,
            evidence_reference="WHO BMI Guidelines"
        )

# Registry for calculators
class CalculatorRegistry:
    def __init__(self):
        self.calculators: Dict[str, MedicalCalculator] = {}
        
    def register(self, calc: MedicalCalculator):
        self.calculators[calc.id] = calc
        
    def get(self, calc_id: str) -> Optional[MedicalCalculator]:
        return self.calculators.get(calc_id)
        
    def list_all(self) -> List[Dict[str, Any]]:
        return [{"id": c.id, "name": c.name, "description": c.description} for c in self.calculators.values()]

calculator_registry = CalculatorRegistry()
calculator_registry.register(BMICalculator())
