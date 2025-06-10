import numpy as np
def simulate_electrical(layers):
    total_thickness = sum(layer["thickness"] for layer in layers)
    unique_materials = len(set(layer["material"] for layer in layers))

    # Basic physics-inspired estimations
    voc = round(0.5 + 0.02 * unique_materials, 2)
    jsc = round(10 + 0.015 * total_thickness, 2)
    ff = 0.75  # Fill factor
    pce = round(voc * jsc * ff / 100, 2)

    # IV Curve simulation (Voc to 0)
    current = [jsc * (1 - v / voc) if v <= voc else 0 for v in np.linspace(0, 1.2, 100)]

    return {
        "pce": pce,
        "voc": voc,
        "jsc": jsc,
        "iv_curve": current
    }
