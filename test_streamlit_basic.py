import streamlit as st

st.title("Basic Streamlit Test")
st.write("If you can see this, Streamlit is working correctly.")
st.button("Test Button")

if st.button("Click me"):
    st.success("Button clicked successfully!")
