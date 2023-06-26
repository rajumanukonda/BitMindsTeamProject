# app.py
from flask import Flask, render_template, request
# import requests
# import langchain2.langchain.llms.vertexai
# import langchain2.langchain.prompts.prompt
import langchain
from getpass import getpass
from langchain.llms import OpenAI
from langchain import PromptTemplate, LLMChain
import os
from jinja2 import Environment

# import google.auth
# from google.cloud import aiplatform

OPENAI_API_KEY = ''

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


def jinja2_enumerate(iterable, start=0):
    return enumerate(iterable, start=start)


app = Flask(__name__)
app.jinja_env.filters['enumerate'] = jinja2_enumerate


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    course_name = request.form['course_name']
    course_contents = generate_course_contents(course_name)
    toc = {'toc': course_contents}
    return render_template('course.html', **toc)


def fetch_course_table_of_contents(course_name):
    template = """Question: {question}

    Answer: Let's think step by step."""

    # prompt = langchain2.langchain.prompts.prompt.PromptTemplate(template=template, input_variables=["question"])
    #
    # llm = langchain2.langchain.llms.vertexai.VertexAI()
    #
    # llm_chain = langchain2.langchain.LLMChain(prompt=prompt, llm=llm)
    prompt = PromptTemplate(template=template, input_variables=["question"])

    llm = OpenAI()
    llm_chain = LLMChain(prompt=prompt, llm=llm)

    question = f"I want to learn basics of {course_name}. Give me the table of contents with chapter names starting " \
               f"with Chapter and sub sections starting with -"

    ans = llm_chain.run(question)
    return ans


def parse_table_of_contents(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    chapters = []
    current_chapter = None

    for line in lines:
        line = line.strip()
        if line.startswith("Chapter"):
            current_chapter = {
                'title': line,
                'subsections': []
            }
            chapters.append(current_chapter)
        elif line.startswith("-"):
            if current_chapter is not None:
                subsection = line[1:].strip()
                current_chapter['subsections'].append(subsection)
            else:
                print("Subsection found without a chapter.")

    return chapters


def generate_course_contents(course_name):
    # Make a request to the Vertex AI API with the course_name
    # Extract and process the relevant information from the API response
    # Generate the course contents with href links
    contents = fetch_course_table_of_contents(course_name)
    with open('response.txt', 'w') as f:
        f.write(contents)

    parsed_contents = parse_table_of_contents('response.txt')
    return parsed_contents


if __name__ == '__main__':
    # generate_course_contents("probability")
    app.run()
    # credentials, project_id = google.auth.default()
    # aiplatform.init(
    #     # your Google Cloud Project ID or number
    #     # environment default used is not set
    #     project='silent-glow-151711',
    #
    #     # the Vertex AI region you will use
    #     # defaults to us-central1
    #     location='us-central1',
    #
    #     # Google Cloud Storage bucket in same region as location
    #     # used to stage artifacts
    #     staging_bucket='gs://my_staging_bucket',
    #
    #     # custom google.auth.credentials.Credentials
    #     # environment default credentials used if not set
    #     credentials=credentials,
    #
    #     # the name of the experiment to use to track
    #     # logged metrics and parameters
    #     experiment='My-Project',
    #
    #     # description of the experiment above
    #     experiment_description='my experiment description'
    # )
