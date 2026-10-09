# -*- coding: utf-8 -*-
"""Optional: regenerate the EN-LLM comparator arm with an OpenAI-compatible endpoint.

Requires: pip install openai ; export OPENAI_API_KEY=...
This script is NOT needed to reproduce the deposited results (the GLM-generated arm is
deposited in corpus/en_llm_translations.tsv). It exists so that the comparator can be
swapped for another model and every downstream statistic re-derived.
"""
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT = ("Translate the following Korean defense white paper excerpt into accurate, "
          "fluent English. Preserve the original agency, modality, and information "
          "structure without additions, omissions, or evaluative intensification.")

def main(model="gpt-4o", out="en_llm_translations_regenerated.tsv"):
    from openai import OpenAI
    client = OpenAI()
    sample = json.load(open(os.path.join(BASE, 'corpus', 'sample150.json'), encoding='utf-8'))
    with open(os.path.join(BASE, 'corpus', out), 'w', encoding='utf-8') as f:
        for s in sample:
            r = client.chat.completions.create(
                model=model,
                temperature=0.1,
                messages=[{"role": "user", "content": PROMPT + "\n\n" + s['text']}])
            en = r.choices[0].message.content.strip().replace('\n', ' ')
            f.write('%d\t%s\n' % (s['idx'], en))
            print(s['idx'], 'ok')

if __name__ == '__main__':
    main()
