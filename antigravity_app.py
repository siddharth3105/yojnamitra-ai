import streamlit as st
import math
import time

st.set_page_config(page_title="Antigravity Simulator", page_icon="🚀", layout="wide")

st.title("🚀 Antigravity Simulator")
st.markdown("*Defying physics, one float at a time*")

# Sidebar controls
st.sidebar.header("Antigravity Controls")
gravity_strength = st.sidebar.slider("Gravity Strength", -10.0, 10.0, -9.8, 0.1)
object_mass = st.sidebar.slider("Object Mass (kg)", 1, 100, 10)
antigravity_power = st.sidebar.slider("Antigravity Power", 0, 100, 50)

# Main content
col1, col2 = st.columns(2)

with col1:
    st.subheader("Physics Parameters")
    st.metric("Gravity", f"{gravity_strength} m/s²")
    st.metric("Mass", f"{object_mass} kg")
    st.metric("Antigravity Force", f"{antigravity_power}%")
    
    # Calculate net force
    gravity_force = object_mass * abs(gravity_strength)
    antigravity_force = (antigravity_power / 100) * gravity_force * 1.5
    net_force = antigravity_force - gravity_force
    
    st.metric("Net Force", f"{net_force:.2f} N", 
              delta="Floating!" if net_force > 0 else "Falling!")

with col2:
    st.subheader("Visualization")
    
    # Calculate position based on forces
    if net_force > 0:
        position = min(90, 50 + (net_force / 10))
        status = "🎈 FLOATING"
        color = "green"
    elif net_force < -5:
        position = max(10, 50 + (net_force / 10))
        status = "⬇️ FALLING"
        color = "red"
    else:
        position = 50
        status = "⚖️ BALANCED"
        color = "orange"
    
    st.markdown(f"### Status: :{color}[{status}]")
    
    # Visual representation
    st.markdown(f"""
    <div style="height: 300px; border: 2px solid #ccc; border-radius: 10px; position: relative; background: linear-gradient(to bottom, #87CEEB, #f0f0f0);">
        <div style="position: absolute; bottom: {position}%; left: 50%; transform: translateX(-50%); font-size: 48px;">
            🚀
        </div>
    </div>
    """, unsafe_allow_html=True)

# Easter egg
if st.sidebar.button("🎯 Import Antigravity"):
    with st.spinner("Importing antigravity module..."):
        time.sleep(1)
    try:
        import antigravity
        st.sidebar.success("Antigravity imported! Check your browser 😉")
    except:
        st.sidebar.info("Classic Python easter egg - opens xkcd.com/353")

# Fun facts
st.markdown("---")
st.subheader("💡 Antigravity Fun Facts")
facts = [
    "In Python, `import antigravity` opens the famous xkcd comic about Python",
    "Real antigravity would require exotic matter with negative mass",
    "NASA studies 'antigravity' through electromagnetic propulsion concepts",
    "Superconductors can create magnetic levitation - the closest thing to antigravity!"
]
st.info(facts[int(time.time()) % len(facts)])
