import glob
import os
import re

import pandas as pd

AREA_NAMES = {
    "matematica.csv": "Matemática",
    "linguagens.csv": "Linguagens",
    "ciencias-humanas.csv": "Ciências Humanas",
    "ciencias-natureza.csv": "Ciências da Natureza",
}


def clean_text(x) -> str:
    if pd.isna(x):
        return ""
    x = str(x)
    x = re.sub(r"\n\s*\n+", "\n", x)
    x = re.sub(r"[ \t]+", " ", x)
    x = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", x)
    return x.strip()


def consolidate(data_source_dir: str) -> pd.DataFrame:
    rows = []
    for year_dir in sorted(glob.glob(os.path.join(data_source_dir, "enem-*"))):
        year = os.path.basename(year_dir).replace("enem-", "")
        for csv_name, area_label in AREA_NAMES.items():
            csv_path = os.path.join(year_dir, csv_name)
            if not os.path.exists(csv_path):
                continue
            df = pd.read_csv(csv_path)
            for _, r in df.iterrows():
                img_paths = []
                raw = r.get("context-images")
                if pd.notna(raw):
                    for p in str(raw).split(","):
                        p = p.strip()
                        if p:
                            img_paths.append(p)
                rows.append({
                    "year": int(year),
                    "area": area_label,
                    "number": int(r["number"]) if pd.notna(r.get("number")) else 0,
                    "context": clean_text(r.get("context")),
                    "statement": clean_text(r.get("question")),
                    "options": [clean_text(r.get(letter)) for letter in "ABCDE"],
                    "correct_answer": clean_text(r.get("answer")).upper(),
                    "image_paths": img_paths,
                })
    out = pd.DataFrame(rows)
    return out.sort_values(["year", "area", "number"]).reset_index(drop=True)
