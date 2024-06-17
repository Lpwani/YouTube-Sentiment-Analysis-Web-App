# random_forest_model.py

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder

class RandomForestSentimentClassifier:
    def __init__(self):
        self.model = self._build_model()

    def _build_model(self):
        vectorizer = TfidfVectorizer()
        encoder = LabelEncoder()
        classifier = RandomForestClassifier(n_estimators=100, random_state=42)

        model = make_pipeline(vectorizer, classifier)
        return model

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X)
