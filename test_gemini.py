
import streamlit as st
from google import genai

st.title("🤖 Gemini AI Connection Test")

if st.button("Test Gemini Connection"):

    try:
        client = genai.Client(
            api_key=st.secrets["GEMINI_API_KEY"]
        )

        with st.spinner("Gemini is responding..."):

            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=(
                    "You are the Game Master of a chemical laboratory "
                    "escape room. Introduce yourself in one sentence."
                )
            )

        st.success("Gemini connected successfully!")
        st.write(response.text)

    except Exception as e:
        st.error("Connection failed.")
        st.code(str(e))




