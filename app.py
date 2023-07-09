
from flask import Flask, render_template, request
from flask_caching import Cache
from langchain.llms import OpenAI, VertexAI
from langchain import PromptTemplate, LLMChain
import os, re, json
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate


OPENAI_API_KEY = ''
GOOGLE_APPLICATION_CREDENTIALS='round-device-391102-50b411b96a9e.json'

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

responseContents = ""

def jinja2_enumerate(iterable, start=0):
    return enumerate(iterable, start=start)


# Create the Flask app
app = Flask(__name__)
app.config['CACHE_TYPE'] = 'simple'
cache = Cache(app)

# Cache timeout in seconds (e.g., 1 hour)
CACHE_TIMEOUT = 3600

# Register the custom filter
app.jinja_env.filters['enumerate'] = jinja2_enumerate

toc = {'toc': None}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    course_name = request.form['course_name']
    course_contents = cache.get(course_name)
    if course_contents is None:
        course_contents = generate_course_contents(course_name)
        cache.set(course_name, course_contents, timeout=CACHE_TIMEOUT)    

    toc['toc'] = course_contents
    toc['course'] = course_name
    print(toc)
    return render_template('course.html', course_name=course_name, **toc)


@app.route('/fetch_content', methods=['GET'])
def fetch_content():
    content_id = request.args.get('content_id')
    print(content_id)
    # Extract the chapter index and subsection index from the content_id
    chapter_index, subsection_index = content_id.split('-')

    # Retrieve the content based on the chapter index and subsection index
    chapter = toc['toc'][int(chapter_index) - 1]  # Adjust index to 0-based
    subsection = chapter['subsections'][int(subsection_index)]

    # Use the language model to generate the content
    generated_content = generate_content(subsection, chapter)  # Replace with your language model generation logic
    generated_quiz = generate_quiz(generated_content, subsection, chapter)

    # Return the generated content as the response
    return generated_content + generated_quiz


def generate_quiz(content, topic, chapter):
    response_schemas = [
        ResponseSchema(name="question", description="A multiple choice question generated from input text snippet."),
        ResponseSchema(name="options", description="Possible choices for the multiple choice question."),
        ResponseSchema(name="answer", description="Correct answer for the question.")
    ]

    # The parser that will look for the LLM output in my schema and return it back to me
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

    # The format instructions that LangChain makes. Let's look at them
    format_instructions = output_parser.get_format_instructions()
    llm = VertexAI()
    prompt = ChatPromptTemplate(
        # messages=[
        #     HumanMessagePromptTemplate.from_template(
        #         """Given a text input, generate one multiple choice question from it along with the correct answer. 
        #         f"""You are a course content creator. Give me 1 multiple choice question on the topic of {topic} under {chapter} chapter for {toc['course']}.
        #             \n{format_instructions}""")
        # ],

        # messages=[
        #     HumanMessagePromptTemplate.from_template("""
        #     You are a course content creator. Give me 1 multiple choice question on the topic of """ +  topic + """ under """ + chapter  + """ chapter for """ + toc['course'] + """ course. 
        # \n{format_instructions}\n{user_prompt}""")
        # ],
        messages=[
            HumanMessagePromptTemplate.from_template("""Given a text input, generate multiple choice questions 
        from it along with the correct answer. 
        \n{format_instructions}\n{user_prompt}""")
        ],
        input_variables=["user_prompt"],
        partial_variables={"format_instructions": format_instructions}
    )
    user_query = prompt.format_prompt(user_prompt=content)
    llm_chain = LLMChain(prompt=prompt, llm=llm)

    user_query_output = llm_chain.run(user_query.to_messages())
    markdown_text = user_query_output
    return markdown_text if markdown_text is not None else '--> No Questions'

    # # Remove the "json " prefix from the string
    # data = re.sub(r'^json\s+', '', markdown_text)
    #
    # # Use regex pattern to match the JSON dictionary
    # pattern = r'{.*}'
    #
    # # Extract the JSON dictionary from the string
    # match = re.search(pattern, data)
    #
    # if match:
    #     json_dict = match.group(0)
    #     print("Extracted JSON Dictionary:")
    #     json_string = json.dumps(json_dict)
    #     return json_string
    # else:
    #     print("No JSON Dictionary found.")
    #     return ''

    # # Convert JSON string to  list
    # question_list = json.loads(json_string)
    #
    # # Convert MCQ choices into lists
    # for i in question_list:
    #     i['options'] = i['options'].split('\n')
    #
    # return question_list


def generate_content(topic, chapter):
    template = """Question: {question}

    Answer: Let's think step by step."""

    prompt = PromptTemplate(template=template, input_variables=["question"])

    # llm = OpenAI()
    llm = VertexAI()


    llm = VertexAI(
    model_name="text-bison@001",
    max_output_tokens=1000,
    temperature=0.1,
    top_p=0.8,
    top_k=40,
    verbose=True,
    )

    llm_chain = LLMChain(prompt=prompt, llm=llm)
    # question = f"Explain me in detail about {topic}. Give one example"

    question = f"""
        You are a course content creator. Give me content for the topic of {topic} under {chapter} for {toc['course']}. 
        First explain about the topic in detailed manner then provide examples.
    """

    ans = llm_chain.run(question)
    return ans


def fetch_course_table_of_contents(course_name):
    template = """Question: {question}

    Answer: Let's think step by step."""

    prompt = PromptTemplate(template=template, input_variables=["question"])

    # llm = OpenAI()
    llm = VertexAI(
        model_name="text-bison@001",
        max_output_tokens=500,
        temperature=0.1,
        top_p=0.9,
        top_k=40,
        verbose=True,
    )

    llm_chain = LLMChain(prompt=prompt, llm=llm)

    # question = f"I want to learn basics of {course_name}. Give me the table of contents for 5 chapters with chapter names starting " \
    #            f"with Chapter and sub sections starting with -"

    question = f"""You are a course content creator. Create a table of contents for basics of {course_name} 
    I want to have chapters and subsections. chapters should start with Chapter keyword and sub section should be with -. 
    Overall, there should be 5 chapters."""

    ans = llm_chain.run(question)
    return ans


def parse_table_of_contents():

    # with open(file_path, 'r') as file:
    #     lines = file.readlines()
    global responseContents
    lines = responseContents.split('\n')

    # print("ContentSplit>>>>>",lines)

    chapters = []
    current_chapter = None

    for line in lines:
        line = line.strip("*").strip("#")
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

    global responseContents
    responseContents = contents
    # print(responseContents)

    # with open('response.txt', 'w') as f:
    #     f.write(contents)

    parsed_contents = parse_table_of_contents()
    return parsed_contents


if __name__ == '__main__':
    # generate_course_contents("probability")
    app.run(host="0.0.0.0", port=8080, debug=True)
    # credentials, project_id = google.auth.default()
