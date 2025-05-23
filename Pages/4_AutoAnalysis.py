import streamlit as st
from google import genai
from google import genai
from google.genai import types
from SystemInstructions.instruct import instruction

headers = {
   "key" : st.secrets["GOOGLE_GEMINI_KEY"]
}

st.markdown("### Statista : An AI-powered BOT for resolving your Data related queries")

client = genai.Client(api_key = headers["key"])
user_prompt = st.text_input("Enter Your Query")
prompt = user_prompt

response = client.models.generate_content(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(
    system_instruction = instruction),
    contents = prompt
)

left, right = st.columns(2)

content_placeholder = st.empty()

with left:
    if st.button('Show Response'):
      content_placeholder.write(response.text)

with right:
    if st.button('Clear Response'):
       content_placeholder.empty()
