from typing import Dict, List, Any, Optional

class TaxonomyNode:
    def __init__(self, id: str, name: str, parent_id: Optional[str] = None):
        self.id = id
        self.name = name
        self.parent_id = parent_id
        self.children: List['TaxonomyNode'] = []
    
    def add_child(self, child: 'TaxonomyNode'):
        self.children.append(child)
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "parent_id": self.parent_id,
            "children": [c.to_dict() for c in self.children]
        }

class TaxonomyManager:
    """Manages the hierarchical structure of medical knowledge deterministically."""
    
    def __init__(self):
        self._nodes: Dict[str, TaxonomyNode] = {}
        self._roots: List[str] = []
        
    def add_node(self, id: str, name: str, parent_id: Optional[str] = None) -> TaxonomyNode:
        """Adds a taxonomy node to the hierarchy."""
        if id in self._nodes:
            return self._nodes[id]
            
        node = TaxonomyNode(id, name, parent_id)
        self._nodes[id] = node
        
        if parent_id is None:
            self._roots.append(id)
        else:
            parent = self._nodes.get(parent_id)
            if parent:
                parent.add_child(node)
                
        return node
        
    def get_node(self, id: str) -> Optional[TaxonomyNode]:
        return self._nodes.get(id)
        
    def get_hierarchy(self) -> List[Dict[str, Any]]:
        """Returns the full hierarchical structure deterministically."""
        # Sort roots to ensure determinism
        return [self._nodes[root_id].to_dict() for root_id in sorted(self._roots)]
        
    def populate_defaults(self):
        """Populates base specialties and categories deterministically."""
        # Top level specialties
        specialties = [
            ("sp_cardio", "Cardiology"),
            ("sp_neuro", "Neurology"),
            ("sp_endo", "Endocrinology"),
            ("sp_em", "Emergency Medicine"),
            ("sp_im", "Internal Medicine"),
            ("sp_peds", "Pediatrics")
        ]
        
        for sp_id, sp_name in specialties:
            self.add_node(sp_id, sp_name)
            
        # Example subcategories for Cardiology
        self.add_node("cat_arrhythmia", "Arrhythmias", "sp_cardio")
        self.add_node("cat_hf", "Heart Failure", "sp_cardio")
        
        # Example subcategories for Neurology
        self.add_node("cat_stroke", "Cerebrovascular Disease", "sp_neuro")
        self.add_node("cat_epilepsy", "Epilepsy", "sp_neuro")
