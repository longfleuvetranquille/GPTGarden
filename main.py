import os
import glob
import re
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from pydantic import BaseModel
from langchain_community.document_loaders import ObsidianLoader
import chromadb
from chromadb.utils import embedding_functions

# 🔧 Chargement config
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GARDEN_PATH = os.getenv("GARDEN_PATH", "notes")

# 📦 Embeddings OpenAI
embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY,
    model_name="text-embedding-ada-002"
)

# 🧠 Chroma client distant
import chromadb
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(
    name="concepts",
    embedding_function=embedding_fn
)

# 🚀 App FastAPI
app = FastAPI()

# 📄 Indexation
def clean_text(content: str) -> str:
    content = re.sub(r"!\[\[.*?\]\]", "", content)
    content = re.sub(r"\[\[.*?\]\]", "", content)
    content = re.sub(r"\[\^.*?\]", "", content)
    content = re.sub(r"<.*?>", "", content)
    content = re.sub(r"#+ ", "", content)
    return content.strip()

def index_notes():
    path = GARDEN_PATH  # GARDEN_PATH est déjà un chemin absolu
    files = glob.glob(os.path.join(path, "**", "*.md"), recursive=True)
    print(f"📁 {len(files)} fichiers trouvés")

    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = clean_text(f.read())
                if not content or len(content) > 20000:
                    continue
                collection.add(
                    documents=[content],
                    metadatas=[{"source": file_path}],
                    ids=[file_path]
                )
        except Exception as e:
            print(f"❌ {file_path} : {e}")

@app.on_event("startup")
def startup_event():
    print("⚙️ Indexation démarrée...")
    index_notes()

@app.get("/")
def root():
    return {"message": "✅ GPTGarden API en ligne"}

@app.get("/query")
def query_gpt(question: str = Query(...)):
    results = collection.query(query_texts=[question], n_results=3)
    return {"results": results}
