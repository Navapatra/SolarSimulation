def simulate_electrical(layers):
    
    total_thickness = sum(layer["thickness"] for layer in layers)
    unique_materials = len(set(layer["material"] for layer in layers))

   
    iv_curve = [i * 0.05 + 0.01 * total_thickness / 1000 for i in range(100)]

    
    pce = round(10 + 0.1 * unique_materials + 0.005 * total_thickness, 2)
    voc = round(0.6 + 0.01 * unique_materials, 2)
    jsc = round(20 + 0.02 * total_thickness, 1)

    return {
        "pce": pce,
        "voc": voc,
        "jsc": jsc,
        "iv_curve": iv_curve
    }
