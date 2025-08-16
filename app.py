import streamlit as st
import asyncio
import pandas as pd
import json
import re
from Main import run_neuro_navigator
from dotenv import load_dotenv
# Import the specific error from the groq library to catch it
from groq import APIStatusError

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(page_title="NeuroNavigator", layout="wide")

# --- UI Elements ---
st.title("🌐 NeuroNavigator")
st.markdown(
    "Enter your travel goal below, and the AI agents will collaborate to create a comprehensive plan for your mission.")
goal = st.text_input("✏️ **Enter your mission goal:**",
                     placeholder="e.g., a 7-day cultural trip to Kyoto, Japan on a $2000 budget")

# --- Main Application Logic ---
if st.button("🚀 Run AI Mission"):
    if goal.strip():
        st.markdown("---")
        st.info("🧠 Running agents in parallel... Please wait for the mission to complete.")

        # Placeholders for streaming agent output
        plan_ph = st.empty()
        research_ph = st.empty()
        budget_ph = st.empty()
        execution_ph = st.empty()

        # Overall progress bar
        overall_progress = st.progress(0, text="Starting mission...")

        # Dictionary to store parsed results from each agent
        results = {}


        async def process():
            """
            Asynchronously runs the AI agents, using their direct dictionary output,
            and updates the UI. Includes error handling for API limits.
            """
            try:
                steps_done = 0
                total_steps = 4
                agent_placeholders = {
                    "plan": plan_ph,
                    "research": research_ph,
                    "budget": budget_ph,
                    "execution": execution_ph
                }
                agent_titles = {
                    "plan": "📝 Mission Plan",
                    "research": "🔍 Research Insights",
                    "budget": "💰 Budget Breakdown",
                    "execution": "⚙️ Execution Itinerary"
                }

                # The 'content' is now a dictionary directly from Main.py, no parsing needed here.
                async for label, content in run_neuro_navigator(goal):
                    data = content  # Use the dictionary directly
                    results[label] = data

                    placeholder = agent_placeholders.get(label)
                    if placeholder:
                        with placeholder.container():
                            st.subheader(agent_titles.get(label, "Agent Output"))
                            if label == "plan" and "steps" in data:
                                for i, step in enumerate(data.get("steps", []), 1):
                                    st.markdown(f"**Step {i}:** {step}")
                            elif label == "research" and ("insights" in data or "sources" in data):
                                st.markdown("**Key Insights:**")
                                for insight in data.get("insights", []):
                                    st.markdown(f"- {insight}")
                                st.markdown("**Sources:**")
                                for source in data.get("sources", []):
                                    st.markdown(f"- {source}")
                            elif label == "budget" and "daily_budget" in data:
                                try:
                                    df = pd.DataFrame(data['daily_budget'])
                                    st.table(df)
                                    col1, col2 = st.columns(2)
                                    total = data.get('total_budget', 'N/A')
                                    remaining = data.get('remaining_balance', 'N/A')
                                    col1.metric("Total Budget", f"${total}")
                                    col2.metric("Remaining Balance", f"${remaining}")
                                except Exception:
                                    st.write(data.get("raw_text", content))
                            elif label == "execution" and "itinerary" in data:
                                for day in data.get("itinerary", []):
                                    st.markdown(f"### 📅 {day.get('day', 'Day')}")
                                    for activity in day.get("activities", []):
                                        st.markdown(f"- {activity}")
                            else:
                                # Fallback for raw text or errors from the agent
                                st.markdown(f"```\n{data.get('raw_text', content)}\n```")

                    steps_done += 1
                    progress_percentage = int((steps_done / total_steps) * 100)
                    overall_progress.progress(progress_percentage,
                                              text=f"Mission Progress: {steps_done}/{total_steps} agents complete")

                overall_progress.progress(100, text="🎯 Mission Completed!")
                st.success("All agents have completed their tasks. See the final summary below.")
                st.divider()
                display_final_summary(results)

            # --- ERROR HANDLING BLOCK ---
            except APIStatusError as e:
                overall_progress.progress(100, text="Mission Failed!")
                st.error(f"""
                **Mission Failed: Request is Too Large**

                The request sent to the AI model exceeded its processing limit. This often happens if the mission goal is very long or complex.

                **💡 How to fix this:**
                - Try making your mission goal shorter and more specific.
                - Rerun the mission with the simplified goal.

                **Error Details:** {e}
                """)
            except Exception as e:
                overall_progress.progress(100, text="Mission Failed!")
                st.error(f"""
                **An Unexpected Error Occurred**

                The mission could not be completed due to an unexpected error. Please check your setup and try again.

                **Error Details:** {e}
                """)


        def display_final_summary(final_results):
            """
            Displays a consolidated summary from the parsed results.
            """
            st.header("📌 Final Mission Summary")
            plan_data = final_results.get("plan", {})
            budget_data = final_results.get("budget", {})
            destination = plan_data.get("destination", "Unknown")
            duration = plan_data.get("duration", "N/A")
            total_budget = budget_data.get("total_budget", "N/A")
            st.metric("📍 Destination", destination)
            col1, col2 = st.columns(2)
            col1.metric("⏳ Duration", f"{duration} days" if duration != "N/A" else "N/A")
            col2.metric("💵 Total Budget", f"${total_budget}")


        asyncio.run(process())
    else:
        st.warning("Please enter a mission goal before running the AI.")
