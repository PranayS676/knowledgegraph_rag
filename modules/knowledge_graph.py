from neo4j import GraphDatabase
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings  # Updated import
from langchain_community.vectorstores import Neo4jVector  # Updated import
from langchain.chains import RetrievalQA
import re
import networkx as nx
import plotly.graph_objects as go
import os

class KnowledgeGraphRAG:
    def __init__(self, neo4j_uri, neo4j_user, neo4j_password, groq_api_key):
        # Initialize Neo4j driver and other components
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        self.llm = ChatGroq(api_key=groq_api_key, model_name="mixtral-8x7b-32768")

    def delete_database(self):
        """Delete all nodes and relationships from the Neo4j database."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            try:
                session.run("CALL db.index.vector.drop('document_vectors')")
            except Exception:
                pass  # Ignore if the vector index does not exist

    def create_vector_store(self, documents):
        """Create a vector store in Neo4j."""
        return Neo4jVector.from_documents(
            documents,
            self.embeddings,
            url=self.neo4j_uri,
            username=self.neo4j_user,
            password=self.neo4j_password,
            index_name="document_vectors",
            node_label="Document",
            embedding_node_property="embedding",
            text_node_property="text",
        )

    def _parse_relationships(self, llm_response):
        """Parse LLM response to extract relationships."""
        pattern = r"\(([^)]+)\)-\[([^\]]+)\]->\(([^)]+)\)"
        return [
            {"entity1": e1.strip(), "relationship": rel.strip(), "entity2": e2.strip()}
            for e1, rel, e2 in re.findall(pattern, llm_response)
        ]

    def create_knowledge_graph(self, documents):
        """Extract relationships and create the knowledge graph in Neo4j."""
        with self.driver.session() as session:
            for doc in documents:
                response = self.llm.predict(f"Extract relationships: {doc.page_content}")
                for rel in self._parse_relationships(response):
                    session.run(
                        """
                        MERGE (e1:Entity {name: $entity1})
                        MERGE (e2:Entity {name: $entity2})
                        MERGE (e1)-[:RELATES {type: $relationship}]->(e2)
                        """,
                        rel,
                    )

    def create_3d_graph(self):
        """Generate a 3D graph visualization using NetworkX and Plotly."""
        G = nx.DiGraph()
        with self.driver.session() as session:
            result = session.run(
                "MATCH (e1:Entity)-[r:RELATES]->(e2:Entity) RETURN e1.name, r.type, e2.name"
            )
            for record in result:
                G.add_edge(record["e1.name"], record["e2.name"])

        pos = nx.spring_layout(G, dim=3)
        return G, pos

    def query(self, question):
        """Query the vector store and return answers."""
        retriever = Neo4jVector(
            self.embeddings,
            url=self.neo4j_uri,
            username=self.neo4j_user,
            password=self.neo4j_password,
            index_name="document_vectors",
        ).as_retriever()
        qa_chain = RetrievalQA.from_chain_type(llm=self.llm, retriever=retriever)
        return qa_chain.run(question)
