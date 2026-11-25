"""Offline evaluation of the course recommender (run: python evaluate.py)."""
import pickle
import time

import numpy as np

pt = pickle.load(open("pt.pkl", "rb"))
course = pickle.load(open("course.pkl", "rb"))
sim = pickle.load(open("similarity_score.pkl", "rb"))
K = 5

subject_of = course.drop_duplicates("course name").set_index("course name")["subject"].str.strip()
rating_of = course.drop_duplicates("course name").set_index("course name")["rating"]

precisions, sims, ratings, recommended = [], [], [], set()
latencies = []
for idx, name in enumerate(pt.index):
    t0 = time.perf_counter()
    top = sorted(enumerate(sim[idx]), key=lambda x: x[1], reverse=True)[1:K + 1]
    latencies.append((time.perf_counter() - t0) * 1000)
    rec_names = [pt.index[i] for i, _ in top]
    recommended.update(rec_names)
    precisions.append(np.mean([subject_of[r] == subject_of[name] for r in rec_names]))
    sims.append(np.mean([s for _, s in top]))
    ratings.append(np.mean([rating_of[r] for r in rec_names]))

subjects = course["subject"].str.strip().value_counts()
print(f"Courses in catalogue           : {len(pt.index)}")
print(f"Subjects                       : {len(subjects)}")
print(f"Subject Precision@{K}            : {np.mean(precisions):.3f}")
print(f"Mean cosine similarity @{K}      : {np.mean(sims):.3f}")
print(f"Catalogue coverage             : {len(recommended) / len(pt.index):.1%}")
print(f"Mean rating of recommendations : {np.mean(ratings):.2f} (catalogue mean {rating_of.mean():.2f})")
print(f"Mean latency per query         : {np.mean(latencies):.3f} ms")
print(f"Subject search coverage        : {(subjects >= 10).sum()}/{len(subjects)} subjects return a full 10 results")
