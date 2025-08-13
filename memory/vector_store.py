from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Create a single embeddings instance
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Keep FAISS in memory for this session
memory_store = None

def init_vector_store():
    """Initialize FAISS with a dummy doc so it's never None."""
    global memory_store
    if memory_store is None:
        memory_store = FAISS.from_texts(
            ["Initial placeholder document."],
            embedding=embeddings
        )

def add_to_vector_store(text):
    """Add new text to the FAISS memory store."""
    global memory_store
    if memory_store is None:
        init_vector_store()
    memory_store.add_texts([text])

def get_vector_store():
    """Return the FAISS memory store."""
    global memory_store
    return memory_store
