import streamlit as st
import json
from simulator.optic import calculate_absorption
from simulator.electrical import simulate_electrical
from simulator.meterilaDB import get_material_properties
import matplotlib.pyplot as plt
import numpy as np

# Page config
st.set_page_config(page_title="Solar Cell Simulation Engine", layout="wide")

# Initialize session state variables
if "show_intro" not in st.session_state:
    st.session_state["show_intro"] = True
if "run_simulation" not in st.session_state:
    st.session_state["run_simulation"] = False

# Custom CSS styling
st.markdown("""
    <style>
        body {
            background-color: #fef6f8 !important;
        }
        .main > div {
            background-color: #fef6f8;
            padding: 1rem;
            border-radius: 15px;
        }
        section[data-testid="stSidebar"] {
            background-color: #f4f4f9;
            border-radius: 15px;
        }
        .block-container h1 {
            color: #cc3366;
        }
        .element-container:has(.stMarkdown) {
            padding-bottom: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# Title and introduction
st.title("⚡ Solar Cell Simulation Engine")
st.markdown("Simulate optical and electrical behavior of layered solar cells.")

# Only show intro if show_intro is True and simulation hasn't run
if st.session_state["show_intro"] and not st.session_state["run_simulation"]:
    st.markdown("""
        <div style="background-color:#ffe6f0; padding:20px; border-radius:10px; border:1px solid #ffb6c1">
            <h4 style="color:#cc3366;">🌸 Welcome to SunSolver!</h4>
            <p style="color:#333;">
                This simulation engine allows you to design custom solar cell structures using different materials, thicknesses, and configurations.
                It analyzes your design by simulating optical absorption, electrical performance (PCE, Voc, Jsc), and even shows you toxicity indicators. 🌞<br><br>
                Use the sidebar to define your layer stack and hit "Run Simulation" to see results.
            </p>
        </div>
    """, unsafe_allow_html=True)

# Sidebar Inputs
with st.sidebar:
    st.header("📐 Define Structure")

    layer_roles = ["TCO", "ETL", "Absorber", "HTL", "Back Contact", "Encapsulation"]
    material_options = {
        "TCO": ["ITO", "FTO", "AZO"],
        "ETL": ["TiO2", "SnO2", "ZnO"],
        "Absorber": ["Si", "Perovskite", "CIGS", "CdTe"],
        "HTL": ["Spiro-OMeTAD", "NiO", "CuSCN"],
        "Back Contact": ["Al", "Ag", "Au", "Mo"],
        "Encapsulation": ["Glass-Polymer", "Polymeric Coating"]
    }

    num_layers = st.slider("Number of Layers", 2, len(layer_roles))
    layers = []

    for i in range(num_layers):
        role = layer_roles[i]
        st.subheader(f"{role} Layer")
        material = st.selectbox(f"Material for {role}", material_options[role], key=f"mat_{i}")
        thickness = st.number_input(f"Thickness (nm) for {role}", 10, 1000, key=f"th_{i}")
        props = get_material_properties(material)

        st.markdown(f"_Bandgap_: {props.get('bandgap', 'N/A')} eV  |  _Toxicity_: {props.get('toxicity', 'Unknown')}")
        if props.get("toxicity") == "High":
            st.warning(f"⚠️ {material} may have environmental or health risks.")

        layers.append({
            "role": role,
            "material": material,
            "thickness": thickness,
            "toxicity": props.get("toxicity", "Unknown")
        })

    st.subheader("🧱 Selected Layer Stack")
    st.table({
        "Layer Role": [l["role"] for l in layers],
        "Material": [l["material"] for l in layers],
        "Thickness (nm)": [l["thickness"] for l in layers],
        "Toxicity": [l["toxicity"] for l in layers]
    })

    run_simulation = st.button("⚙️ Run Simulation", key="run_button")
    optimize = st.checkbox("🔬 Enable Advanced Optimization")

if run_simulation:
    st.session_state["run_simulation"] = True
    st.session_state["show_intro"] = False
    st.rerun()  # Changed from experimental_rerun() to rerun()

# Only show results if simulation has run
if st.session_state["run_simulation"]:
    valid_pairs = [("ITO", "TiO2"), ("FTO", "SnO2"), ("AZO", "ZnO")]
    tco = next((l for l in layers if l["role"] == "TCO"), None)
    etl = next((l for l in layers if l["role"] == "ETL"), None)

    if tco and etl:
        if (tco["material"], etl["material"]) not in valid_pairs:
            st.error(f"❌ The combination {tco['material']} + {etl['material']} may have poor interface compatibility.")
        else:
            st.success("✅ Basic feasibility checks passed.")

    if optimize:
        st.info("🧠 Running advanced optimization...")

    # Optical and Electrical Simulation
    optical_result = calculate_absorption(layers)
    electrical_result = simulate_electrical(layers)

    results = {
        "pce": electrical_result["pce"],
        "voc": electrical_result["voc"],
        "jsc": electrical_result["jsc"],
        "iv_curve": electrical_result["iv_curve"],
        "quantum_efficiency": optical_result["qe"]
    }

    with open("result/simulation_output.json", "w") as f:
        json.dump(results, f)

    st.success("✅ Simulation Completed!")

    
    st.subheader("📊 Simulation Results")
    st.write("**PCE:**", f"{results['pce']} %")
    st.write("**Voc:**", f"{results['voc']} V")
    st.write("**Jsc:**", f"{results['jsc']} mA/cm²")

    # Graph Data Prep
    qe_values = results["quantum_efficiency"]
    wavelengths = np.linspace(300, 900, len(qe_values))
    peak_wavelength = wavelengths[np.argmax(qe_values)]
    peak_value = max(qe_values)

    roles = [l["role"] for l in layers]
    thicknesses = [l["thickness"] for l in layers]
    bandgaps = [
    get_material_properties(l["material"]).get("bandgap") or 0
    for l in layers
]
    tox_colors = {"Low": "green", "Medium": "yellow", "High": "red"}
    colors = [tox_colors.get(l["toxicity"], "gray") for l in layers]

    # IV Curve
    st.markdown("### IV Curve")
    st.line_chart(results["iv_curve"])

    # Quantum Efficiency and Absorption
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Quantum Efficiency")
        fig_qe, ax_qe = plt.subplots()
        ax_qe.plot(wavelengths, qe_values, color='blue')
        ax_qe.set_title("Quantum Efficiency vs Wavelength")
        ax_qe.set_xlabel("Wavelength (nm)")
        ax_qe.set_ylabel("Quantum Efficiency")
        ax_qe.grid(True)
        st.pyplot(fig_qe)
        st.markdown(f"🔍 **Peak QE**: {peak_value:.3f} at ~{int(peak_wavelength)} nm")

    with col2:
        if "absorption" in optical_result:
            st.markdown("### Absorption Spectrum")
            absorption = optical_result["absorption"]
            fig_abs, ax_abs = plt.subplots()
            ax_abs.plot(wavelengths, absorption, color='green')
            ax_abs.set_title("Absorption Spectrum")
            ax_abs.set_xlabel("Wavelength (nm)")
            ax_abs.set_ylabel("Absorption Coefficient")
            ax_abs.grid(True)
            st.pyplot(fig_abs)

    # Layer Thickness and Bandgap
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("### Layer Thickness")
        fig_thick, ax_thick = plt.subplots()
        ax_thick.barh(roles[::-1], thicknesses[::-1], color='skyblue')
        ax_thick.set_xlabel("Thickness (nm)")
        ax_thick.set_title("Layer Thickness Diagram")
        st.pyplot(fig_thick)

    with col4:
        st.markdown("### Bandgaps")
        fig_bg, ax_bg = plt.subplots()
        ax_bg.bar(roles, bandgaps, color='orange')
        ax_bg.set_ylabel("Bandgap (eV)")
        ax_bg.set_title("Material Bandgaps")
        st.pyplot(fig_bg)

    # Toxicity Indicator
    st.markdown("### Toxicity Overview")
    fig_tox, ax_tox = plt.subplots(figsize=(8, 1.5))
    ax_tox.bar(roles, [1]*len(layers), color=colors)
    ax_tox.set_yticks([])
    ax_tox.set_title("Toxicity")
    st.pyplot(fig_tox)