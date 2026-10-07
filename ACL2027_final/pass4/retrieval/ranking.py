"""Question-visible title linking and deterministic full-corpus ranking.

No gold article ID, answers, spans, or annotation fields enter this module.
A title match changes priority; it never removes another corpus unit.
"""
from __future__ import annotations
import datetime as dt
import re
import numpy as np
from pass3.pipeline.run_matched import BM25, tok, parse_query, YEAR

VARIANTS = ["bm25", "bm25_latestyear", "title_bm25", "title_residual", "title_bm25_latestyear", "title_residual_latestyear"]

class TitleRanker:
    def __init__(self, units, k1=1.5, b=.75):
        self.units=units
        self.index=BM25(units,k1,b)
        self.titles={}
        for u in units:
            self.titles.setdefault(tuple(tok(u["title"])),set()).add(u["article_path"])
        self.titles={k:v for k,v in self.titles.items() if k}
        self.article=np.array([u["article_path"] for u in units],dtype=object)

    def link(self, question):
        words=tok(question)
        matches=[]
        for title, articles in self.titles.items():
            n=len(title)
            if any(tuple(words[i:i+n])==title for i in range(len(words)-n+1)):
                matches.append((title,articles))
        if not matches:
            return {"article_paths":[],"matched_title_tokens":[],"residual_question":question}
        # Longest exact title protects against a shorter title nested in a name.
        length=max(len(title) for title,_ in matches)
        matches=[x for x in matches if len(x[0])==length]
        paths=sorted(set().union(*(x[1] for x in matches)))
        remove=set().union(*(set(x[0]) for x in matches))
        residual=" ".join(w for w in words if w not in remove)
        return {"article_paths":paths,"matched_title_tokens":[list(x[0]) for x in matches],"residual_question":residual}

    def rank_with_metadata(self, question, variant="title_residual"):
        if variant not in VARIANTS:raise ValueError(variant)
        link=self.link(question)
        residual="residual" in variant and bool(link["article_paths"])
        order,scores=self.index.rank(link["residual_question"] if residual else question)
        if variant.startswith("title_") and link["article_paths"]:
            matched=set(link["article_paths"])
            order=sorted(order,key=lambda i: self.units[i]["article_path"] not in matched)
        window=parse_query(question)
        if "latestyear" in variant and window:
            year=dt.date.fromordinal(window[1]).year
            def latestyear(i):
                return max((int(y) for y in YEAR.findall(self.units[i]["text"]) if int(y)<=year),default=0)
            order=sorted(order[:20],key=lambda i:-latestyear(i))+order[20:]
        return order,scores,link

    def rank(self, question, variant="title_residual"):
        """Return the full strict order and lexical scores for the frozen variant."""
        order,scores,_=self.rank_with_metadata(question,variant)
        return order,scores
