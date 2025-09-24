"""
Reads:
 - data/Food Commodity.csv
 - data/validation_field_title.csv
 - data/mapping.csv

Produces:
 - data/remapped_mapping.csv  (columns: rst_4_extended,new_tag,source,matched_term,original_validation_field_title)

Matching priority:
 1) Food Commodity tags (preferred)
 2) validation_field_title tags
 3) fuzzy fallback (difflib) against Food Commodity
"""
import csv
import re
from pathlib import Path
from difflib import get_close_matches

BASE = Path(__file__).resolve().parents[1] / "kantar_processing/data"

def load_list_csv(path, col_name=None):
    path = Path(path)
    with path.open(newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        return []
    header = [c.strip() for c in rows[0]]
    start = 1
    if col_name and col_name in header:
        idx = header.index(col_name)
        return [r[idx].strip() for r in rows[start:] if len(r) > idx]
    # otherwise return first column values (skip header if single header)
    return [r[0].strip() for r in rows[start:] if r]

def norm(s):
    if s is None:
        return ""
    return re.sub(r'[^a-z0-9\s]', ' ', s.lower())

def tokens(s):
    return [t for t in re.split(r'\s+', norm(s)) if t]

def main():
    food_path = BASE / "Food Commodity.csv"
    val_path = BASE / "validation_field_title.csv"
    map_path = BASE / "mapping.csv"
    out_path = BASE / "remapped_mapping.csv"

    food_list = load_list_csv(food_path, col_name="Food Commodity")
    val_list = load_list_csv(val_path, col_name="validation_field_title")
    print(food_list)

    # Build normalized lookup for exact phrase matching and token matching
    food_norm_map = {}
    for f in food_list:
        nf = norm(f).strip()
        if nf:
            food_norm_map[nf] = f

    val_norm_map = {}
    for v in val_list:
        nv = norm(v).strip()
        if nv:
            val_norm_map[nv] = v

    # read mapping.csv header to get rst_4_extended and original validation_field_title if present
    with map_path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    out_rows = []
    food_phrases = list(food_norm_map.keys())
    for r in rows:
        rst = r.get('rst_4_extended', '').strip()
        orig_val = r.get('validation_field_title', '').strip() if 'validation_field_title' in r else ''
        n_rst = norm(rst)
        chosen = None
        source = None
        matched_term = ""

        # 1) direct phrase containment check against Food Commodity (preferred)
        for fp in sorted(food_phrases, key=lambda x: -len(x)):
            if fp and fp in n_rst:
                chosen = food_norm_map[fp]
                source = "food_commodity_phrase"
                matched_term = fp
                break

        # 2) token match: any token of commodity appears in rst words (avoid tiny tokens)
        if not chosen:
            rst_toks = set(tokens(rst))
            best = None
            for fp, orig in food_norm_map.items():
                f_toks = [t for t in tokens(fp) if len(t) >= 3]
                if f_toks and any(t in rst_toks for t in f_toks):
                    # prefer multi-token matches and longer matches
                    if best is None or len(tokens(fp)) > len(tokens(best[0])):
                        best = (fp, orig)
            if best:
                chosen = best[1]
                source = "food_commodity_token"
                matched_term = best[0]
                #print(best[0])

        # 3) fallback to validation_field_title phrase match
        if not chosen:
            for vp in sorted(val_norm_map.keys(), key=lambda x: -len(x)):
                if vp and vp in n_rst:
                    chosen = val_norm_map[vp]
                    source = "validation_phrase"
                    matched_term = vp
                    break

        # 4) fuzzy match against Food Commodity names (difflib)
        if not chosen:
            candidates = get_close_matches(n_rst, food_phrases, n=1, cutoff=0.78)
            if candidates:
                chosen = food_norm_map[candidates[0]]
                source = "food_commodity_fuzzy"
                matched_term = candidates[0]

        # 5) use original validation mapping if present
        if not chosen and orig_val:
            chosen = orig_val
            source = "original_mapping"
            matched_term = norm(orig_val)


        if not chosen:
            chosen = ""
            source = "unmapped"
            matched_term = ""

        out_rows.append({
            'rst_4_extended': rst,
            'new_tag': chosen,
            'source': source,
            'matched_term': matched_term,
            'original_validation_field_title': orig_val
        })

    # write output
    with out_path.open('w', newline='', encoding='utf-8') as f:
        fieldnames = ['rst_4_extended','new_tag','source','matched_term','original_validation_field_title']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    print("Wrote remapped file to:", out_path)

if __name__ == "__main__":
    main()