import numpy as np

def calculate_absorption(layers):
    wavelengths = np.linspace(300, 900, 100)  
    qe_total = np.zeros_like(wavelengths)

    
    absorption_peaks = {
        "Si": 600,
        "ITO": 450,
        "Al": 400,
        "Perovskite": 750,
        "TiO2": 350
    }

    for layer in layers:
        material = layer["material"]
        thickness = layer["thickness"]
        peak = absorption_peaks.get(material, 600)

        # Gaussian centered at the peak wavelength
        qe_layer = np.exp(-((wavelengths - peak) ** 2) / (2 * (100) ** 2))
        qe_total += qe_layer * (thickness / 1000)  # normalize effect by thickness

    qe_total = np.clip(qe_total, 0, 1)  # Ensure QE stays between 0 and 1

    # Return as list of values
    return {"qe": list(qe_total)}
