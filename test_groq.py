import streamlit as st
from groq import Groq

api_key = st.secrets["GROQ_API_KEY"]

client = Groq(api_key=api_key)

try:
    models = client.models.list()

    print("\nAVAILABLE GROQ MODELS:\n")

    for model in models.data:
        print(model.id)

except Exception as e:
    print("\nERROR:")
    print(e)