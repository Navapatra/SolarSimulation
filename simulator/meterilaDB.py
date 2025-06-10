def get_material_properties(material):
    db = {
        "Si": {"bandgap": 1.12, "toxicity": "Low", "type": "Absorber"},
        "ITO": {"bandgap": 3.5, "toxicity": "Medium", "type": "TCO"},
        "Al": {"bandgap": None, "toxicity": "Low", "type": "Back Contact"},
        "Perovskite": {"bandgap": 1.55, "toxicity": "High", "type": "Absorber"},
        "TiO2": {"bandgap": 3.2, "toxicity": "Low", "type": "ETL"}
    }
    return db.get(material, {})
