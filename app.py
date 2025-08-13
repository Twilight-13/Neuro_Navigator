import streamlit as st
from Main import run_neuro_navigator
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="NeuroNavigator", page_icon="🧠", layout="wide")

st.title("🧠 NeuroNavigator")
goal = st.text_input("Enter your goal:", "")

if st.button("Run AI Mission"):
    if goal.strip():
        st.write("🚀 Running Agents... Please wait...")

        #outputs from Main.py
        plan, research, budget, execution = run_neuro_navigator(goal)

        # Display results
        st.subheader("Plan")
        st.write(plan)

        st.subheader("Research")
        st.write(research)

        st.subheader("Budget")
        st.write(budget)

        st.subheader("Execution Simulation")
        st.write(execution)

    else:
        st.warning("Please enter a goal first!")
