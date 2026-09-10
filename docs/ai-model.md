# AI Model

## Pipeline

1. **Text extraction** – `pypdf` for PDF, `python-docx` for DOCX, plain read for TXT; `text_cleaner.py` normalises whitespace and strips non-printables.
2. **Skill extraction** – `skill_extractor.py` holds a canonical taxonomy (`skill -> aliases`). Aliases are compiled into word-boundary-aware regexes so `c#`, `c++`, `node.js` match correctly. Output is a sorted, deduplicated list of canonical skills. Extend by adding entries to `SKILL_TAXONOMY`.
3. **CV analysis** – `cv_analyzer.py` extracts degree lines (bachelor/master/PhD/...), experience entries (lines under an "Experience" heading or containing year ranges) and estimates years of experience (explicit "N years experience" wins; otherwise summed year ranges).
4. **Job analysis** – `job_analyzer.py` applies the same skill extractor to job text and pulls a minimum years requirement.
5. **Embeddings** – `embeddings.py` uses `sentence-transformers` (`all-MiniLM-L6-v2`, 384-d, normalised). If the model can't be loaded (offline / slim image) it falls back to a deterministic hashed bag-of-words vector of the same dimension so the system stays functional.
6. **Scoring** – `ranking.py`:

   ```
   score = 0.50 * skill_overlap        # |cv ∩ job| / |job skills|
         + 0.35 * semantic_similarity  # (cosine + 1) / 2
         + 0.15 * experience_fit       # min(1, cv_years / required_years)
   ```
   Reported as 0–100. Matches ≥ 60 trigger notifications.

## Improving the model

- Replace regex skill extraction with a NER model (e.g. spaCy + custom skill entity) or an LLM prompt.
- Learn weights from user feedback (applied / dismissed).
- Store embeddings in pgvector for ANN search when the job corpus grows.
- Add location and salary preference filters before ranking.
