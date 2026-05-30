"""
Streamlit interface for the AI Travel Planning Assistant.

Run with:  streamlit run app.py
"""

import streamlit as st
from agent import run_agent

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="plane",
    layout="centered",
)

st.title("AI Travel Planning Assistant")
st.caption("Powered by LangChain and Claude — plan your next trip in seconds.")

st.markdown("---")

with st.sidebar:
    st.header("Quick Trip Builder")
    st.write("Fill in the details below to auto-generate a query.")

    origin = st.selectbox(
        "From",
        ["Delhi", "Mumbai", "Bangalore", "Chennai", "Hyderabad", "Kolkata", "Jaipur", "Goa"],
    )
    destination = st.selectbox(
        "To",
        ["Goa", "Delhi", "Mumbai", "Bangalore", "Chennai", "Hyderabad", "Kolkata", "Jaipur"],
    )
    days = st.slider("Duration (days)", 1, 7, 3)
    budget = st.number_input("Hotel budget per night (Rs.)", min_value=0, value=5000, step=500)
    min_stars = st.selectbox("Minimum hotel stars", [1, 2, 3, 4, 5], index=2)

    if st.button("Build Query", use_container_width=True):
        query = (
            f"Plan a {days}-day trip from {origin} to {destination}. "
            f"Hotel budget is Rs.{budget} per night with at least {min_stars} stars."
        )
        st.session_state["prefilled_query"] = query

st.subheader("Describe your trip")
default_query = st.session_state.get("prefilled_query", "")
user_query = st.text_area(
    "What kind of trip are you planning?",
    value=default_query,
    placeholder="e.g. Plan a 3-day trip from Delhi to Goa with a hotel budget of Rs.4000 per night.",
    height=100,
)

if st.button("Plan My Trip", type="primary", use_container_width=True):
    if not user_query.strip():
        st.warning("Please enter a trip description before clicking Plan My Trip.")
    else:
        with st.spinner("Planning your trip... this may take a moment."):
            try:
                result = run_agent(user_query)
                st.session_state["last_result"] = result
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if "last_result" in st.session_state:
    st.markdown("---")
    st.subheader("Your Trip Plan")
    st.text(st.session_state["last_result"])

    st.download_button(
        label="Download Itinerary",
        data=st.session_state["last_result"],
        file_name="trip_itinerary.txt",
        mime="text/plain",
    )
