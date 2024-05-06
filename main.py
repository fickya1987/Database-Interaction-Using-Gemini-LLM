from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import sqlite3

import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_schema(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    schema = {}
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        schema[table_name] = [col[1] for col in columns]

    conn.close()
    return schema

def get_gemini_response(question, prompt, schema):
    schema_prompt = "The database schema is as follows:\n\n"
    for table, columns in schema.items():
        schema_prompt += f"Table: {table}\nColumns: {', '.join(columns)}\n\n"

    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([schema_prompt, prompt[0], question])
    return response.text.replace("```", "").strip()

def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return rows
# Retrieve the database schema
schema = get_schema("student2.db")

prompt = [
    """
    You are tasked with retriving the required data from a database by generating sql queries for the given natural language input.
    The database can consist of multiple tables. You will get the input as database. Your goal is to retrieve the data required by the user, based on their natural language query.
    Finally, you need to output the retrieved data from the database in a structured format. 
    For example, if a user asks, "Show me all the students enrolled in the Computer Science course," your response should include the SQL query needed to retrieve this information from the database. 
    The SQL query should not be enclosed in triple backticks and should not include the word "SQL" in the output.

    """
]

st.set_page_config(page_title="I can Retrieve Any SQL query")
st.header("DATABASE INTERACTION USING LLM")

question = st.text_input("Input: ", key="input")

submit = st.button("Ask the question")

if submit:
    response = get_gemini_response(question, prompt, schema)
    response = read_sql_query(response, "student2.db")
    st.subheader("The Response is")
    for row in response:
        st.write(row)
