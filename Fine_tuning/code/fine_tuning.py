# import necessary modules
#RAG
from langchain.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import Ollama
from langchain.chains import RetrievalQA

import os
import pickle

# Define paths
VECTORSTORE_DIR = "faiss_store"
DOCUMENTS_DIR = "documents"

# 1. Load Documents
def load_documents(folder_path):
    all_docs = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif filename.endswith(".txt"):
            loader = TextLoader(file_path)
        elif filename.endswith(".docx"):
            loader = Docx2txtLoader(file_path)
        elif filename.endswith(".csv"):
            loader = CSVLoader(file_path)
        else:
            continue  # Skip unsupported files
        
        documents = loader.load()
        all_docs.extend(documents)
    
    return all_docs

# 2. Split documents into small chunks
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    chunks = splitter.split_documents(documents)
    return chunks

# 3. Create Embeddings and FAISS Vector Store
def create_or_load_faiss_vector_store():
    # Check if FAISS index already exists
    if os.path.exists(VECTORSTORE_DIR):
        print("FAISS vector store already exists. Loading it...")
        embedding_model = OllamaEmbeddings(model="mistral")
        vector_store = FAISS.load_local(VECTORSTORE_DIR, embedding_model)
    else:
        print("No existing vector store found. Creating new one...")
        documents = load_documents(DOCUMENTS_DIR)
        print(f"Loaded {len(documents)} documents.")
        
        chunks = split_documents(documents)
        print(f"Created {len(chunks)} chunks.")
        
        embedding_model = OllamaEmbeddings(model="mistral")
        vector_store = FAISS.from_documents(chunks, embedding_model)
        
        # Save the vector store
        vector_store.save_local(VECTORSTORE_DIR)
        print("FAISS vector store saved successfully.")
    
    return vector_store

# 4. Create a QA Chain
def create_qa_chain(vector_store):
    llm = Ollama(model="phi3-mini")
    retriever = vector_store.as_retriever()
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
    
    return qa_chain

# 5. Main Function
def main():
    print("Setting up FAISS Vector Database...")
    vector_store = create_or_load_faiss_vector_store()
    
    print("Building QA system...")
    qa_chain = create_qa_chain(vector_store)
    
    while True:
        query = input("\nEnter your query (or type 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        
        result = qa_chain({"query": query})
        
        print("\nAnswer:", result['result'])

# Run the script
if __name__ == "__main__":
    main()
