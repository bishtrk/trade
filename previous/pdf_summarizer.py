import os
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import HuggingFaceHub
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate

# 1. Custom Prompt for Summarization
# This instructs the model to be brief (50 words max).
initial_prompt_template = """You are given the following document:
"{text}"

Please provide a concise summary (no more than 200 words) focusing on the key points and main arguments.
"""

# When refining, the model sees both the existing summary and the new chunk:
refine_prompt_template = """Your job is to refine the existing summary with new information.
Existing summary:
"{existing_answer}"

New text to refine the summary with:
"{text}"

Improve the summary above, ensuring it remains under 300 words in total.
"""

INITIAL_PROMPT = PromptTemplate(
    template=initial_prompt_template, 
    input_variables=["text"]
)

REFINE_PROMPT = PromptTemplate(
    template=refine_prompt_template, 
    input_variables=["existing_answer", "text"]
)

def summarize_pdf(pdf_path: str) -> str:
    # 2. (Optional) Set your Hugging Face Hub API token
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"

    # 3. Load the PDF with pypdf (via LangChain)
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    # 4. Split the PDF text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # you can tweak
        chunk_overlap=100
    )
    split_docs = text_splitter.split_documents(docs)

    # 5. Initialize an LLM from Hugging Face Hub
    llm = HuggingFaceHub(
        repo_id="google/flan-t5-large", #good
        #repo_id="facebook/bart-large-cnn",

#        repo_id = "microsoft/phi-4", #google/flan-t5-xxl",

#        
#nvidia/Llama-3.1-Nemotron-70B-Instruct-HF
#mistralai/Mistral-7B-Instruct-v0.3

#meta-llama/Llama-3.2-1B


#        


        model_kwargs={
            "temperature": 0.1,   
            "max_length": 500     # reduce to encourage shorter output
        },
    )

    # 6. Load a refine summarization chain with custom prompts
    summarize_chain = load_summarize_chain(
        llm, 
        chain_type="refine",
        question_prompt=INITIAL_PROMPT,
        refine_prompt=REFINE_PROMPT
    )

    # 7. Run the chain to get the summary
    summary = summarize_chain.run(split_docs)
    return summary

if __name__ == "__main__":
    pdf_file_path = "three.pdf"  # your PDF file
    summary = summarize_pdf(pdf_file_path)
    print("FINAL SUMMARY (refine chain, custom prompts):\n", summary)