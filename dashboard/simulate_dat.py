import random
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
CACHE_TTL = os.environ['CACHE_TTL']

st.cache(persist=True, ttl=CACHE_TTL)
def generate_toy_data(n: int) -> list:

    list_of_jsons = []

    for i in range(n):
        pm25 = round(random.random() * 15, 2)
        pm10 = round(random.random() * 25, 2)
        sample_reading = {
            "pm2_5": pm25,
            "pm10": pm10,
        }
        list_of_jsons.append(sample_reading)

    return list_of_jsons

if __name__ == "__main__":

    sample = generate_toy_data(10)
    print(sample)
    pass
