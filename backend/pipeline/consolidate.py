"""
Extrai e limpa os CSVs brutos do repositório gabriel-antonelli/extract-enem-data.
Reaproveitado quase sem alterações do MVP original — a única mudança é que
agora devolve um DataFrame em memória em vez de salvar um .pkl, porque quem
chama isso (seed_db.py) vai direto para o banco.
"""
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
    """
    data_source_dir: caminho para a pasta enem-data/ do repositório de dados
    clonado (contém enem-2009/, enem-2010/, ...).
    """
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
                rows.append(
                    {
                        "year": int(year),
                        "area": area_label,
                        "number": int(r["number"]) if pd.notna(r.get("number")) else 0,
                        "context": clean_text(r.get("context")),
                        "statement": clean_text(r.get("question")),
                        "option_a": clean_text(r.get("A")),
                        "option_b": clean_text(r.get("B")),
                        "option_c": clean_text(r.get("C")),
                        "option_d": clean_text(r.get("D")),
                        "option_e": clean_text(r.get("E")),
                        "correct_answer": r.get("answer"),
                        "image_paths": img_paths,
                    }
                )

    out = pd.DataFrame(rows)
    return out.sort_values(["year", "area", "number"]).reset_index(drop=True)
