def __init__(self, neo4j_uri, neo4j_user, neo4j_password, groq_api_key):
    self.neo4j_uri = neo4j_uri
    self.neo4j_user = neo4j_user
    self.neo4j_password = neo4j_password
    self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    self.llm = ChatGroq(api_key=groq_api_key, model_name="mixtral-8x7b-32768")
