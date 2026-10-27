from typing import Dict, List, Any, Optional
from enum import Enum

class NodeType(str, Enum):
    DISEASE = "disease"
    SYMPTOM = "symptom"
    SIGN = "sign"
    RISK_FACTOR = "risk_factor"
    LAB_TEST = "lab_test"
    IMAGING = "imaging"
    MEDICATION = "medication"
    DRUG_INTERACTION = "drug_interaction"
    CONTRAINDICATION = "contraindication"
    PROCEDURE = "procedure"
    PATIENT_EDUCATION = "patient_education"
    CLINICAL_GUIDELINE = "clinical_guideline"
    REFERENCE = "reference"

class EdgeType(str, Enum):
    PRESENTS_WITH = "presents_with"
    TREATED_BY = "treated_by"
    DIAGNOSED_BY = "diagnosed_by"
    CONTRAINDICATES = "contraindicates"
    INTERACTS_WITH = "interacts_with"
    INCREASES_RISK_OF = "increases_risk_of"

class GraphNode:
    def __init__(self, node_id: str, node_type: NodeType, properties: Dict[str, Any]):
        self.id = node_id
        self.type = node_type
        self.properties = properties
        self.edges: List['GraphEdge'] = []

class GraphEdge:
    def __init__(self, source_id: str, target_id: str, edge_type: EdgeType, weight: float = 1.0):
        self.source_id = source_id
        self.target_id = target_id
        self.edge_type = edge_type
        self.weight = weight

class KnowledgeGraph:
    """In-memory or GraphDB-backed knowledge graph mapping relationships."""
    
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        
    def add_node(self, node: GraphNode):
        self.nodes[node.id] = node
        
    def add_edge(self, edge: GraphEdge):
        if edge.source_id in self.nodes and edge.target_id in self.nodes:
            self.nodes[edge.source_id].edges.append(edge)
            
    def get_neighbors(self, node_id: str, edge_type: Optional[EdgeType] = None) -> List[GraphNode]:
        node = self.nodes.get(node_id)
        if not node:
            return []
            
        neighbors = []
        for edge in node.edges:
            if edge_type is None or edge.edge_type == edge_type:
                neighbors.append(self.nodes[edge.target_id])
        return neighbors

knowledge_graph = KnowledgeGraph()
