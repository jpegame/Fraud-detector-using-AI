import os
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from imblearn.over_sampling import SMOTE

def train_model():
    silver_path = "data/silver/silver_data.pkl"
    
    if not os.path.exists(silver_path):
        print("[ML] Arquivo silver nao encontrado")
        return None
    
    df = pd.read_pickle(silver_path)
    
    X = df.drop("Class", axis=1)
    y = df["Class"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    smote = SMOTE(random_state=42)
    X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train_balanced, y_train_balanced)
    
    y_pred = model.predict(X_test)
    
    print("[ML] Acuracia:", accuracy_score(y_test, y_pred))
    print("[ML] Relatorio:")
    print(classification_report(y_test, y_pred))
    
    os.makedirs("models", exist_ok=True)
    model_path = "models/fraud_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    
    print(f"[ML] Modelo salvo em {model_path}")
    return model

def predict(data):
    model_path = "models/fraud_model.pkl"
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    return model.predict(data)

if __name__ == "__main__":
    train_model()
