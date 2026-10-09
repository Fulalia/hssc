# -*- coding: utf-8 -*-
"""Direct LaBSE embedder via transformers (pooler_output + L2 norm), replicating official usage."""
import torch
import numpy as np

class LabseEmbedder:
    def __init__(self, path):
        from transformers import AutoTokenizer, AutoModel
        self.tok = AutoTokenizer.from_pretrained(path)
        self.model = AutoModel.from_pretrained(path)
        self.model.eval()

    @torch.no_grad()
    def encode(self, texts, batch_size=32, max_length=256):
        out = []
        for i in range(0, len(texts), batch_size):
            chunk = [t if len(t) > 0 else ' ' for t in texts[i:i + batch_size]]
            enc = self.tok(chunk, padding=True, truncation=True, max_length=max_length, return_tensors='pt')
            emb = self.model(**enc).pooler_output
            emb = torch.nn.functional.normalize(emb, p=2, dim=1)
            out.append(emb.numpy().astype(np.float32))
        return np.vstack(out)

if __name__ == '__main__':
    m = LabseEmbedder(r'C:\Users\1\Desktop\韩国国防白皮书\_tmp_hssc\labse_model')
    import numpy as np
    v = m.encode(['우리 정부는 평화를 구축한다.', 'Our government builds peace.', 'The cat sat on the mat.'])
    print('dim', v.shape)
    print('ko-en cos: %.4f' % float(v[0] @ v[1]))
    print('ko-unrel cos: %.4f' % float(v[0] @ v[2]))
