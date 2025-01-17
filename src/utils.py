import ast

import pandas as pd


def load_cocktails_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df['ingredients'] = df['ingredients'].apply(parse_list)
    df['ingredientMeasures'] = df['ingredientMeasures'].apply(parse_list)
    return df

def parse_list(list_str: str) -> list:
    try:
        return ast.literal_eval(list_str)
    except (ValueError, SyntaxError):
        return []

def preprocess_text(text: str) -> str:
    return text.lower().strip()
