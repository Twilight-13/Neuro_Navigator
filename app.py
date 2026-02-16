import streamlit as st
import asyncio
import pandas as pd
import nest_asyncio
import altair as alt
from typing import Dict, Any

from config import Config
from orchestrator import NeuroOrchestrator
from tools.finance_tool import FinanceTool

# Apply nest_asyncio for async loop in Streamlit
nest_asyncio.apply()

# Page Config
st.set_page_config(
    page_title="NeuroNavigator | AI Travel Assistant",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Styling ---
STYLING = """
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main Container */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #f0f2f6;
        font-weight: 700;
    }
    
    /* Cards/Containers */
    .css-1r6slb0, .css-12oz5g7 {
        border-radius: 12px;
        padding: 1.5rem;
        background-color: #1a1c24;
        border: 1px solid #2d303e;
    }
    
    /* Custom divider */
    hr {
        border-color: #2d303e;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #4CAF50;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #13151b;
        border-right: 1px solid #2d303e;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        border: none;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
</style>
"""
st.markdown(STYLING, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.title("🧭 Configuration")
    st.markdown("---")
    
    # Status Indicators
    st.subheader("System Status")
    
    def status_chk(label, val):
        color = "green" if val else "red"
        icon = "✅" if val else "❌"
        st.markdown(f"**{label}**: <span style='color:{color}'>{icon}</span>", unsafe_allow_html=True)

    status_chk("LLM Provider", Config.DEFAULT_LLM_PROVIDER)
    status_chk("Groq API", Config.GROQ_API_KEY)
    status_chk("OpenAI API", Config.OPENAI_API_KEY)
    status_chk("Amadeus API", Config.AMADEUS_CLIENT_ID)
    
    st.markdown("---")
    st.info("💡 **Tip:** Use specific goals like *'7-day trip to Tokyo with $2000'* for best results.")
    st.markdown("---")
    st.caption(f"v2.0.0 | Env: {Config.ENV}")

# --- Main Interface ---
st.title("NeuroNavigator")
st.markdown("### Your AI-Powered Autonomous Agent Team")
st.markdown("Describe your mission, and watch our specialized agents **Plan**, **Research**, **Budget**, and **Execute** it in real-time.")

# Input Section
col1, col2 = st.columns([3, 1])
with col1:
    goal = st.text_input("Enter your mission objective:", 
                        placeholder="e.g. Plan a romantic weekend in Paris for under $1500...",
                        label_visibility="collapsed")
with col2:
    run_btn = st.button("🚀 Initiating Launch", type="primary", use_container_width=True)

# Detect currency for display
ft = FinanceTool()
_, user_currency = ft.detect_currency(goal)


# --- Orchestration Logic ---
if run_btn and goal:
    st.divider()
    
    # State containers
    status_container = st.status("🚀 **Mission Control Active**", expanded=True)
    
    # Layout for results
    col_plan, col_research = st.columns(2)
    col_finance, col_exec = st.columns(2)
    
    # Placeholders
    with col_plan:
        st.subheader("📝 Strategic Plan")
        plan_ph = st.empty()
    with col_research:
        st.subheader("🔍 Intelligence")
        research_ph = st.empty()
    with col_finance:
        st.subheader("💰 Financial Analysis")
        budget_ph = st.empty()
    with col_exec:
        st.subheader("⚙️ Execution Protocol")
        exec_ph = st.empty()

    async def main():
        orchestrator = NeuroOrchestrator()
        results = {}
        
        status_container.write("🧠 Agents coordinating...")
        
        try:
            async for label, data in orchestrator.run(goal):
                results[label] = data
                
                # Update Status
                status_container.write(f"✅ **{label.capitalize()} Agent** completed task.")
                
                # --- Update UI based on agent type ---
                
                # 1. PLAN
                if label == "plan":
                    with plan_ph.container():
                        if "steps" in data:
                            st.info(f"**Target:** {data.get('destination', 'Unknown')} | **Duration:** {data.get('duration', 'N/A')}")
                            for i, step in enumerate(data.get("steps", []), 1):
                                st.markdown(f"**{i}.** {step}")
                        else:
                            st.write(data)

                # 2. RESEARCH
                elif label == "research":
                    with research_ph.container():
                        if "insights" in data:
                            for insight in data["insights"]:
                                st.success(f"📌 {insight}")
                            if "sources" in data:
                                with st.expander("References"):
                                    for s in data["sources"]:
                                        st.caption(f"• {s}")
                        else:
                            st.write(data)

                # 3. BUDGET
                elif label == "budget":
                    with budget_ph.container():
                        if "daily_budget" in data:
                            # Metrics
                            total = data.get('total_budget', 0)
                            rem = data.get('remaining_balance', 0)
                            
                            c1, c2 = st.columns(2)
                            c1.metric("Total Cost", f"${total}", delta=None)
                            c2.metric("Remaining", f"${rem}", delta_color="normal" if str(rem) != "N/A" and float(rem) >= 0 else "inverse")
                            
                            # Chart
                            df = pd.DataFrame(data['daily_budget'])
                            if not df.empty and "cost" in df.columns:
                                chart = alt.Chart(df).mark_bar().encode(
                                    x=alt.X('day', axis=alt.Axis(labelAngle=0)),
                                    y='cost',
                                    tooltip=['day', 'cost']
                                ).properties(height=200)
                                st.altair_chart(chart, use_container_width=True)
                            
                            # API Sources
                            st.caption(f"Sources: {', '.join(data.get('sources', []))}")
                        else:
                            st.write(data)

                # 4. EXECUTION
                elif label == "execution":
                    with exec_ph.container():
                        if "itinerary" in data:
                            for day_plan in data["itinerary"]:
                                with st.expander(f"📅 {day_plan.get('day', 'Day')}", expanded=False):
                                    for act in day_plan.get("activities", []):
                                        st.markdown(f"- {act}")
                        else:
                            st.write(data)
                            
        except Exception as e:
            status_container.update(label="Mission Failed", state="error", expanded=True)
            st.error(f"Critical System Error: {e}")
            return

        status_container.update(label="Mission Complete", state="complete", expanded=False)
        st.success("🎉 Mission accomplished successfully.")

    # Run Loop
    asyncio.run(main())

elif run_btn and not goal:
    st.warning("⚠️ Please define a mission objective.")
