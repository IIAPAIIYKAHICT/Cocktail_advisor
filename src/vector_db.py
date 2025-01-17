import os
import json
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer


class VectorDB:
    def __init__(self, model_name="all-MiniLM-L6-v2", index_path="models/cocktails_index.faiss",
                 preferences_index_path="models/preferences_index.faiss", data_path="data/cocktails.csv"):
        self.model = SentenceTransformer(model_name)
        self.index_path = index_path
        self.preferences_index_path = preferences_index_path
        self.data_path = data_path
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.dimension)
        self.preferences_index = faiss.IndexFlatL2(self.dimension)
        self.preferences = {}

        self.data = self.load_data()
        self.load_indices()

    def load_data(self):
        if os.path.exists(self.data_path):
            return pd.read_csv(self.data_path)
        else:
            raise FileNotFoundError(f"Data file not found at {self.data_path}")

    def add_user_preferences(self, user_id: str, preferences: dict):
        current_preferences = self.get_user_preferences(user_id)
        updated_ingredients = list(set(current_preferences["ingredients"] + preferences["ingredients"]))
        updated_cocktails = list(set(current_preferences["cocktails"] + preferences["cocktails"]))

        combined_text = f"Ingredients: {', '.join(updated_ingredients)}. Cocktails: {', '.join(updated_cocktails)}."
        embedding = self.model.encode([combined_text], convert_to_numpy=True)

        self.preferences_index.add(embedding)

        self.preferences[user_id] = {
            "ingredients": updated_ingredients,
            "cocktails": updated_cocktails,
        }
        self.save_indices()

    def get_user_preferences(self, user_id: str) -> dict:
        return self.preferences.get(user_id, {"ingredients": [], "cocktails": []})

    def save_indices(self):
        """
        Сохраняет основной и пользовательский FAISS-индексы, а также словарь пользовательских предпочтений.
        Перед записью убеждаемся, что директории для index_path и preferences_index_path существуют.
        """
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.preferences_index_path), exist_ok=True)

        faiss.write_index(self.index, self.index_path)
        faiss.write_index(self.preferences_index, self.preferences_index_path)

        with open(f"{self.preferences_index_path}.json", "w") as f:
            json.dump(self.preferences, f, indent=4)

    def load_indices(self):
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)

        if os.path.exists(self.preferences_index_path):
            self.preferences_index = faiss.read_index(self.preferences_index_path)
            with open(f"{self.preferences_index_path}.json", "r") as f:
                self.preferences = json.load(f)

    def prepare_cocktail_index(self):
        """
        Строит заново FAISS-индекс коктейлей на основе data/cocktails.csv.
        Перед записью индекса убеждаемся, что нужные директории существуют.
        """
        data_path = "data/cocktails.csv"
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Cocktail data file not found at {data_path}. Please include it.")

        self.data = pd.read_csv(data_path)

        # Формируем текст для каждого коктейля: название + список ингредиентов
        combined_text = self.data.apply(
            lambda row: f"{row['name']} " + " ".join(row['ingredients']),
            axis=1
        ).tolist()

        embeddings = self.model.encode(combined_text, convert_to_numpy=True)
        self.index.add(embeddings)

        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)

    def search_cocktails(self, query: str, top_k: int = 5) -> pd.DataFrame:
        if self.index.ntotal == 0:
            raise ValueError("The cocktail index is empty. Ensure that 'prepare_cocktail_index' has been called.")

        query_embedding = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding, top_k)

        results = self.data.iloc[indices[0]].copy()
        results["distance"] = distances[0]
        return results
