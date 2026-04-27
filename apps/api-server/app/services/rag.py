import httpx

from app.config import settings
from app.services.vector import vector_service


class RAGService:
    def __init__(self):
        self.ollama_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self._embedding_model = None

    def _get_embedding_model(self):
        if self._embedding_model is None:
            from sentence_transformers import SentenceTransformer

            self._embedding_model = SentenceTransformer(settings.embedding_model)
        return self._embedding_model

    def embed_query(self, text: str) -> list[float]:
        model = self._get_embedding_model()
        return model.encode(text).tolist()

    def retrieve_context(self, query: str, top_k: int = 5) -> list[dict]:
        query_vector = self.embed_query(query)
        return vector_service.search(query_vector, top_k=top_k)

    async def generate_answer(self, query: str, contexts: list[dict]) -> dict:
        context_text = "\n\n---\n\n".join(
            f"[来源: {ctx['filename']}]\n{ctx['content']}" for ctx in contexts
        )

        prompt = f"""你是一个知识库问答助手。请根据以下参考资料回答用户的问题。
如果参考资料中没有相关信息，请诚实地说明你无法从现有资料中找到答案。
请用中文回答，并在回答末尾标注引用的来源文件。

参考资料：
{context_text}

用户问题：{query}

回答："""

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
            )
            response.raise_for_status()
            result = response.json()

        return {
            "answer": result.get("response", ""),
            "sources": [
                {"filename": ctx["filename"], "document_id": ctx["document_id"]}
                for ctx in contexts
            ],
        }

    async def chat(self, query: str, top_k: int = 5) -> dict:
        contexts = self.retrieve_context(query, top_k=top_k)
        if not contexts:
            return {
                "answer": "抱歉，知识库中没有找到与您问题相关的内容。",
                "sources": [],
            }
        return await self.generate_answer(query, contexts)


rag_service = RAGService()
