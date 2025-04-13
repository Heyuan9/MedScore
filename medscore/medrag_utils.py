"""MedRAG Retriever

Use MedRAG corpus for retrieving relevant passages in the medical domain.
Copied from MedRAG/src/utils.py and MedRAG/src/data/statpearls.py.
"""
import os
import sys
import json
from typing import List, Dict, Any, Tuple, Union
import traceback
import logging
import subprocess

from sentence_transformers.models import Transformer, Pooling
from sentence_transformers import SentenceTransformer
import faiss
import torch
import tqdm
import numpy as np

logger = logging.getLogger(__name__)


corpus_names = {
    "PubMed": ["pubmed"],
    "Textbooks": ["textbooks"],
    "StatPearls": ["statpearls"],
    "Wikipedia": ["wikipedia"],
    "MedText": ["textbooks", "statpearls"],
    "MedCorp": ["pubmed", "textbooks", "statpearls", "wikipedia"],
    "MEDIC": ["pubmed", "textbooks", "statpearls"]
}

retriever_names = {
    "BM25": ["bm25"],
    "Contriever": ["facebook/contriever"],
    "SPECTER": ["allenai/specter"],
    "MedCPT": ["ncbi/MedCPT-Query-Encoder"],
    "RRF-2": ["bm25", "ncbi/MedCPT-Query-Encoder"],
    "RRF-4": ["bm25", "facebook/contriever", "allenai/specter", "ncbi/MedCPT-Query-Encoder"]
}


def ends_with_ending_punctuation(s):
    ending_punctuation = ('.', '?', '!')
    return any(s.endswith(char) for char in ending_punctuation)


def concat(title, content):
    if ends_with_ending_punctuation(title.strip()):
        return title.strip() + " " + content.strip()
    else:
        return title.strip() + ". " + content.strip()


class CustomizeSentenceTransformer(SentenceTransformer):  # change the default pooling "MEAN" to "CLS"

    def _load_auto_model(self, model_name_or_path, *args, **kwargs):
        """
        Creates a simple Transformer + CLS Pooling model and returns the modules
        """
        print("No sentence-transformers model found with name {}. Creating a new one with CLS pooling.".format(
            model_name_or_path))
        token = kwargs.get('token', None)
        cache_folder = kwargs.get('cache_folder', None)
        revision = kwargs.get('revision', None)
        trust_remote_code = kwargs.get('trust_remote_code', False)
        if 'token' in kwargs or 'cache_folder' in kwargs or 'revision' in kwargs or 'trust_remote_code' in kwargs:
            transformer_model = Transformer(
                model_name_or_path,
                cache_dir=cache_folder,
                model_args={"token": token, "trust_remote_code": trust_remote_code, "revision": revision},
                tokenizer_args={"token": token, "trust_remote_code": trust_remote_code, "revision": revision},
            )
        else:
            transformer_model = Transformer(model_name_or_path)
        pooling_model = Pooling(transformer_model.get_word_embedding_dimension(), 'cls')
        return [transformer_model, pooling_model]


def embed(chunk_dir, index_dir, model_name, **kwarg):
    save_dir = os.path.join(index_dir, "embedding")

    if "contriever" in model_name:
        model = SentenceTransformer(model_name, device="cuda" if torch.cuda.is_available() else "cpu")
    else:
        model = CustomizeSentenceTransformer(model_name, device="cuda" if torch.cuda.is_available() else "cpu")

    model.eval()

    fnames = sorted([fname for fname in os.listdir(chunk_dir) if fname.endswith(".jsonl")])

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    with torch.no_grad():
        for fname in tqdm.tqdm(fnames, desc="Embedding"):
            fpath = os.path.join(chunk_dir, fname)
            save_path = os.path.join(save_dir, fname.replace(".jsonl", ".npy"))
            if os.path.exists(save_path):
                continue
            if open(fpath).read().strip() == "":
                continue
            texts = [json.loads(item) for item in open(fpath).read().strip().split('\n')]
            if "specter" in model_name.lower():
                texts = [model.tokenizer.sep_token.join([item["title"], item["content"]]) for item in texts]
            elif "contriever" in model_name.lower():
                texts = [". ".join([item["title"], item["content"]]).replace('..', '.').replace("?.", "?") for item in
                         texts]
            elif "medcpt" in model_name.lower():
                texts = [[item["title"], item["content"]] for item in texts]
            else:
                texts = [concat(item["title"], item["content"]) for item in texts]
            embed_chunks = model.encode(texts, **kwarg)
            np.save(save_path, embed_chunks)
        embed_chunks = model.encode([""], **kwarg)
    return embed_chunks.shape[-1]


def construct_index(index_dir, model_name, h_dim=768, HNSW=False, M=32):
    with open(os.path.join(index_dir, "metadatas.jsonl"), 'w') as f:
        f.write("")

    if HNSW:
        M = M
        if "specter" in model_name.lower():
            index = faiss.IndexHNSWFlat(h_dim, M)
        else:
            index = faiss.IndexHNSWFlat(h_dim, M)
            index.metric_type = faiss.METRIC_INNER_PRODUCT
    else:
        if "specter" in model_name.lower():
            index = faiss.IndexFlatL2(h_dim)
        else:
            index = faiss.IndexFlatIP(h_dim)

    for fname in tqdm.tqdm(sorted(os.listdir(os.path.join(index_dir, "embedding"))), desc="Loading embeddings"):
        curr_path = os.path.join(index_dir, "embedding", fname)
        curr_embed = np.load(curr_path)
        try:
            index.add(curr_embed)
        except Exception as e:
            logger.error(f"Error loading {curr_path}:\n{e}\n{traceback.format_exc()}")
            continue
        with open(os.path.join(index_dir, "metadatas.jsonl"), 'a+') as f:
            f.write("\n".join(
                [json.dumps({'index': i, 'source': fname.replace(".npy", "")}) for i in range(len(curr_embed))]) + '\n')
        logger.debug(f"Wrote meta to {os.path.join(index_dir, 'metadatas.jsonl')}")
    faiss.write_index(index, os.path.join(index_dir, "faiss.index"))
    return index


class Retriever:

    def __init__(self, retriever_name="ncbi/MedCPT-Query-Encoder", corpus_name="textbooks", db_dir="./corpus",
                 HNSW=False, **kwarg):
        self.retriever_name = retriever_name
        self.corpus_name = corpus_name

        self.db_dir = db_dir
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)
        self.chunk_dir = os.path.join(self.db_dir, self.corpus_name, "chunk")
        if not os.path.exists(self.chunk_dir):
            print("Cloning the {:s} corpus from Huggingface...".format(self.corpus_name))
            os.system("git clone https://huggingface.co/datasets/MedRAG/{:s} {:s}".format(corpus_name,
                                                                                          os.path.join(self.db_dir,
                                                                                                       self.corpus_name)))
            if self.corpus_name == "statpearls":
                print("Downloading the statpearls corpus from NCBI bookshelf...")
                os.system(
                    "wget https://ftp.ncbi.nlm.nih.gov/pub/litarch/3d/12/statpearls_NBK430685.tar.gz -P {:s}".format(
                        os.path.join(self.db_dir, self.corpus_name)))
                os.system("tar -xzvf {:s} -C {:s}".format(
                    os.path.join(db_dir, self.corpus_name, "statpearls_NBK430685.tar.gz"),
                    os.path.join(self.db_dir, self.corpus_name)))
                print("Chunking the statpearls corpus...")
                download_statpearls(self.db_dir)
        self.index_dir = os.path.join(self.db_dir, self.corpus_name, "index",
                                      self.retriever_name.replace("Query-Encoder", "Article-Encoder"))
        if "bm25" in self.retriever_name.lower():
            from pyserini.search.lucene import LuceneSearcher
            self.metadatas = None
            self.embedding_function = None
            if os.path.exists(self.index_dir):
                self.index = LuceneSearcher(os.path.join(self.index_dir))
            else:
                os.system(
                    "python -m pyserini.index.lucene --collection JsonCollection --input {:s} --index {:s} --generator DefaultLuceneDocumentGenerator --threads 16".format(
                        self.chunk_dir, self.index_dir))
                self.index = LuceneSearcher(os.path.join(self.index_dir))
        else:
            if os.path.exists(os.path.join(self.index_dir, "faiss.index")):
                self.index = faiss.read_index(os.path.join(self.index_dir, "faiss.index"))
                self.metadatas = [json.loads(line) for line in
                                  open(os.path.join(self.index_dir, "metadatas.jsonl")).read().strip().split('\n')]
            else:
                print("[In progress] Embedding the {:s} corpus with the {:s} retriever...".format(self.corpus_name,
                                                                                                  self.retriever_name.replace(
                                                                                                      "Query-Encoder",
                                                                                                      "Article-Encoder")))
                if self.corpus_name in ["textbooks", "pubmed", "wikipedia"] and self.retriever_name in [
                    "allenai/specter", "facebook/contriever", "ncbi/MedCPT-Query-Encoder"] and not os.path.exists(
                        os.path.join(self.index_dir, "embedding")):
                    print("[In progress] Downloading the {:s} embeddings given by the {:s} model...".format(
                        self.corpus_name, self.retriever_name.replace("Query-Encoder", "Article-Encoder")))
                    os.makedirs(self.index_dir, exist_ok=True)
                    if self.corpus_name == "textbooks":
                        if self.retriever_name == "allenai/specter":
                            os.system(
                                "wget -O {:s} https://myuva-my.sharepoint.com/:u:/g/personal/hhu4zu_virginia_edu/EYRRpJbNDyBOmfzCOqfQzrsBwUX0_UT8-j_geDPcVXFnig?download=1".format(
                                    os.path.join(self.index_dir, "embedding.zip")))
                        elif self.retriever_name == "facebook/contriever":
                            os.system(
                                "wget -O {:s} https://myuva-my.sharepoint.com/:u:/g/personal/hhu4zu_virginia_edu/EQqzldVMCCVIpiFV4goC7qEBSkl8kj5lQHtNq8DvHJdAfw?download=1".format(
                                    os.path.join(self.index_dir, "embedding.zip")))
                        elif self.retriever_name == "ncbi/MedCPT-Query-Encoder":
                            os.system(
                                "wget -O {:s} https://myuva-my.sharepoint.com/:u:/g/personal/hhu4zu_virginia_edu/EQ8uXe4RiqJJm0Tmnx7fUUkBKKvTwhu9AqecPA3ULUxUqQ?download=1".format(
                                    os.path.join(self.index_dir, "embedding.zip")))
                    elif self.corpus_name == "pubmed":
                        if self.retriever_name == "allenai/specter":
                            os.system(
                                "wget -O {:s} https://myuva-my.sharepoint.com/:u:/g/personal/hhu4zu_virginia_edu/Ebz8ySXt815FotxC1KkDbuABNycudBCoirTWkKfl8SEswA?download=1".format(
                                    os.path.join(self.index_dir, "embedding.zip")))
                        elif self.retriever_name == "facebook/contriever":
                            os.system(
                                "wget -O {:s} https://myuva-my.sharepoint.com/:u:/g/personal/hhu4zu_virginia_edu/EWecRNfTxbRMnM0ByGMdiAsBJbGJOX_bpnUoyXY9Bj4_jQ?download=1".format(
                                    os.path.join(self.index_dir, "embedding.zip")))
                        elif self.retriever_name == "ncbi/MedCPT-Query-Encoder":
                            os.system(
                                "wget -O {:s} https://myuva-my.sharepoint.com/:u:/g/personal/hhu4zu_virginia_edu/EVCuryzOqy5Am5xzRu6KJz4B6dho7Tv7OuTeHSh3zyrOAw?download=1".format(
                                    os.path.join(self.index_dir, "embedding.zip")))
                    elif self.corpus_name == "wikipedia":
                        if self.retriever_name == "allenai/specter":
                            os.system(
                                "wget -O {:s} https://myuva-my.sharepoint.com/:u:/g/personal/hhu4zu_virginia_edu/Ed7zG3_ce-JOmGTbgof3IK0BdD40XcuZ7AGZRcV_5D2jkA?download=1".format(
                                    os.path.join(self.index_dir, "embedding.zip")))
                        elif self.retriever_name == "facebook/contriever":
                            os.system(
                                "wget -O {:s} https://myuva-my.sharepoint.com/:u:/g/personal/hhu4zu_virginia_edu/ETKHGV9_KNBPmDM60MWjEdsBXR4P4c7zZk1HLLc0KVaTJw?download=1".format(
                                    os.path.join(self.index_dir, "embedding.zip")))
                        elif self.retriever_name == "ncbi/MedCPT-Query-Encoder":
                            os.system(
                                "wget -O {:s} https://myuva-my.sharepoint.com/:u:/g/personal/hhu4zu_virginia_edu/EXoxEANb_xBFm6fa2VLRmAcBIfCuTL-5VH6vl4GxJ06oCQ?download=1".format(
                                    os.path.join(self.index_dir, "embedding.zip")))
                    os.system(
                        "unzip {:s} -d {:s}".format(os.path.join(self.index_dir, "embedding.zip"), self.index_dir))
                    os.system("rm {:s}".format(os.path.join(self.index_dir, "embedding.zip")))
                    h_dim = 768
                else:
                    h_dim = embed(chunk_dir=self.chunk_dir, index_dir=self.index_dir,
                                  model_name=self.retriever_name.replace("Query-Encoder", "Article-Encoder"), **kwarg)

                print("[In progress] Embedding finished! The dimension of the embeddings is {:d}.".format(h_dim))
                self.index = construct_index(index_dir=self.index_dir,
                                             model_name=self.retriever_name.replace("Query-Encoder", "Article-Encoder"),
                                             h_dim=h_dim, HNSW=HNSW)
                print("[Finished] Corpus indexing finished!")
                self.metadatas = [json.loads(line) for line in
                                  open(os.path.join(self.index_dir, "metadatas.jsonl")).read().strip().split('\n')]
            if "contriever" in self.retriever_name.lower():
                self.embedding_function = SentenceTransformer(
                    self.retriever_name,
                    device="cuda" if torch.cuda.is_available() else "cpu"
                )
            else:
                self.embedding_function = CustomizeSentenceTransformer(
                    self.retriever_name,
                    device="cuda" if torch.cuda.is_available() else "cpu"
                )
            self.embedding_function.eval()

    def get_relevant_documents(self, questions, k=32, id_only=False, **kwarg):
        assert isinstance(questions, list), "Questions should be a list of strings"
        # BM25 not updated for batched
        if "bm25" in self.retriever_name.lower():
            res_ = [[] for _ in range(len(questions))]
            for idx, question in enumerate(questions):
                hits = self.index.search(question, k=k)
                res_[idx].append(np.array([h.score for h in hits]))
                ids = [h.docid for h in hits]
                indices = [{"source": '_'.join(h.docid.split('_')[:-1]), "index": eval(h.docid.split('_')[-1])} for h in
                           hits]
        else:
            logger.debug("Embedding")
            with torch.no_grad():
                query_embeds = self.embedding_function.encode(questions, **kwarg)
            # ( scores: [# questions x # docs], index IDs: [# questions x # docs] )
            logger.debug("Searching index")
            res_ = self.index.search(query_embeds, k=k)
            logger.debug(f"Gathering IDs")
            ids = [
                ['_'.join([self.metadatas[i]["source"], str(self.metadatas[i]["index"])]) for i in res_[1][idx]] for idx in range(len(questions))
            ]
            indices = [
                [self.metadatas[i] for i in res_[1][idx]] for idx in range(len(questions))
            ]
        logger.debug("Consolidating scores")
        scores = [res_[0][idx].tolist() for idx in range(len(questions))]
        if id_only:
            return [[{"id": i} for i in id_list] for id_list in ids], scores
        else:
            logger.debug("Loading documents")
            # Loading documents at this stage is slow
            return [self.idx2txt(idx_list) for idx_list in indices], scores

    def idx2txt(self, indices):  # return List of Dict of str
        """
        Input: List of Dict( {"source": str, "index": int} )
        Output: List of str
        """
        loaded_docs = []
        for i in tqdm.tqdm(indices, total=len(indices), desc="Loading documents", disable=not logger.level==logging.DEBUG):
            text_path = os.path.join(self.chunk_dir, i["source"] + ".jsonl")
            with open(text_path, "r") as f:
                whole_file = f.read().strip().split('\n')
                doc = json.loads(whole_file[i["index"]])
                loaded_docs.append(doc)
        return loaded_docs


class RetrievalSystem:

    def __init__(self, retriever_name="MedCPT", corpus_name="Textbooks", db_dir="./corpus", HNSW=False, cache=False):
        self.retriever_name = retriever_name
        self.corpus_name = corpus_name
        assert self.corpus_name in corpus_names
        assert self.retriever_name in retriever_names
        logger.debug(f"Loading {self.retriever_name}")
        self.retrievers = []
        for retriever in retriever_names[self.retriever_name]:
            self.retrievers.append([])
            for corpus in corpus_names[self.corpus_name]:
                logger.debug(f"Loading {corpus} for {retriever}")
                try:
                    r = Retriever(retriever, corpus, db_dir, HNSW=HNSW)
                except Exception as e:
                    logger.error(f"Error loading {retriever}:\n{e}\n{traceback.format_exc()}")
                    exit(1)
                self.retrievers[-1].append(r)
        self.cache = cache
        if self.cache:
            logger.debug(f"Loading cache")
            self.docExt = DocExtracter(cache=True, corpus_name=self.corpus_name, db_dir=db_dir)
        else:
            self.docExt = None

    def retrieve(self,
                 questions: List[str],
                 k: int = 32,
                 rrf_k: int = 100,
                 id_only: bool=False) -> List[Tuple[List[Dict[str, Any]], List[float]]]:
        assert isinstance(questions, list), "Questions should be a list of strings"

        # Create a placeholder for each question
        retrieval_per_question = {
            i: {
                "text": [],
                "scores": []
            }
            for i in range(len(questions))
        }

        if "RRF" in self.retriever_name:
            k_ = max(k * 2, 100)
        else:
            k_ = k
        for i in range(len(retriever_names[self.retriever_name])):
            # Keep the retrieval results in separate lists
            for q_idx in retrieval_per_question:
                retrieval_per_question[q_idx]["text"].append([])
                retrieval_per_question[q_idx]["scores"].append([])
            for j in range(len(corpus_names[self.corpus_name])):
                t, s = self.retrievers[i][j].get_relevant_documents(questions, k=k_, id_only=id_only)
                for q_idx, (t_i, s_i) in enumerate(zip(t, s)):
                    retrieval_per_question[q_idx]["text"][-1].append(t_i)
                    retrieval_per_question[q_idx]["scores"][-1].append(s_i)
        output = []
        for q_idx, ret_dict in retrieval_per_question.items():
            logger.debug("In merge")
            t, s = self.merge(ret_dict["text"], ret_dict["scores"], k=k, rrf_k=rrf_k)
            logger.debug("Out of merge")
            # The use_cache here is not compatible with MedRAGRetriever
            if not id_only:
                logger.debug(f"In cache")
                t = [self.docExt.extract(t_i) for t_i in t]
            output.append((t, s))
        return output

    def merge(self,
              texts: List[List[Dict[str, Any]]],
              scores: List[List[float]],
              k: int = 32,
              rrf_k: int = 100) -> Tuple[List[Dict[str, Any]], List[float]]:
        """Merge the texts and scores from different retrievers"""
        RRF_dict = {}
        # For each retriever
        for i in range(len(retriever_names[self.retriever_name])):
            texts_all, scores_all = None, None
            # for each corpus
            for j in range(len(corpus_names[self.corpus_name])):
                if texts_all is None:
                    texts_all = texts[i][j]
                    scores_all = scores[i][j]
                else:
                    texts_all = texts_all + texts[i][j]
                    scores_all = scores_all + scores[i][j]
            if "specter" in retriever_names[self.retriever_name][i].lower():
                sorted_index = np.array(scores_all).argsort()
            else:
                sorted_index = np.array(scores_all).argsort()[::-1]
            texts[i] = [texts_all[i] for i in sorted_index]
            scores[i] = [scores_all[i] for i in sorted_index]
            for j, item in enumerate(texts[i]):
                if item["id"] in RRF_dict:
                    RRF_dict[item["id"]]["score"] += 1 / (rrf_k + j + 1)
                    RRF_dict[item["id"]]["count"] += 1
                else:
                    RRF_dict[item["id"]] = {
                        "id": item["id"],
                        "title": item.get("title", ""),
                        "content": item.get("content", ""),
                        "score": 1 / (rrf_k + j + 1),
                        "count": 1
                    }
        RRF_list = sorted(RRF_dict.items(), key=lambda x: x[1]["score"], reverse=True)
        if len(texts) == 1:
            texts = texts[0][:k]
            scores = scores[0][:k]
        else:
            texts = [dict((key, item[1][key]) for key in ("id", "title", "content")) for item in RRF_list[:k]]
            scores = [item[1]["score"] for item in RRF_list[:k]]
        return texts, scores


class DocExtracter:

    def __init__(self, db_dir="./corpus", cache=False, corpus_name="MedCorp"):
        self.db_dir = db_dir
        self.cache = cache
        print("Initializing the document extracter...")
        for corpus in corpus_names[corpus_name]:
            if not os.path.exists(os.path.join(self.db_dir, corpus, "chunk")):
                print("Cloning the {:s} corpus from Huggingface...".format(corpus))
                os.system("git clone https://huggingface.co/datasets/MedRAG/{:s} {:s}".format(corpus,
                                                                                              os.path.join(self.db_dir,
                                                                                                           corpus)))
                if corpus == "statpearls":
                    print("Downloading the statpearls corpus from NCBI bookshelf...")
                    os.system(
                        "wget https://ftp.ncbi.nlm.nih.gov/pub/litarch/3d/12/statpearls_NBK430685.tar.gz -P {:s}".format(
                            os.path.join(self.db_dir, corpus)))
                    os.system("tar -xzvf {:s} -C {:s}".format(
                        os.path.join(self.db_dir, corpus, "statpearls_NBK430685.tar.gz"),
                        os.path.join(self.db_dir, corpus)))
                    print("Chunking the statpearls corpus...")
                    os.system("python src/data/statpearls.py")
        if self.cache:
            if os.path.exists(os.path.join(self.db_dir, "_".join([corpus_name, "id2text.json"]))):
                self.dict = json.load(open(os.path.join(self.db_dir, "_".join([corpus_name, "id2text.json"]))))
            else:
                self.dict = {}
                for corpus in corpus_names[corpus_name]:
                    for fname in tqdm.tqdm(sorted(os.listdir(os.path.join(self.db_dir, corpus, "chunk"))), desc=f"Loading {corpus} for cache"):
                        if open(os.path.join(self.db_dir, corpus, "chunk", fname)).read().strip() == "":
                            continue
                        for i, line in enumerate(
                                open(os.path.join(self.db_dir, corpus, "chunk", fname)).read().strip().split('\n')):
                            item = json.loads(line)
                            _ = item.pop("contents", None)
                            # assert item["id"] not in self.dict
                            self.dict[item["id"]] = item
                with open(os.path.join(self.db_dir, "_".join([corpus_name, "id2text.json"])), 'w') as f:
                    json.dump(self.dict, f)
        else:
            if os.path.exists(os.path.join(self.db_dir, "_".join([corpus_name, "id2path.json"]))):
                self.dict = json.load(open(os.path.join(self.db_dir, "_".join([corpus_name, "id2path.json"]))))
            else:
                self.dict = {}
                for corpus in corpus_names[corpus_name]:
                    for fname in tqdm.tqdm(sorted(os.listdir(os.path.join(self.db_dir, corpus, "chunk"))), desc=f"Loading {corpus} for cache"):
                        if open(os.path.join(self.db_dir, corpus, "chunk", fname)).read().strip() == "":
                            continue
                        for i, line in enumerate(
                                open(os.path.join(self.db_dir, corpus, "chunk", fname)).read().strip().split('\n')):
                            item = json.loads(line)
                            # assert item["id"] not in self.dict
                            self.dict[item["id"]] = {"fpath": os.path.join(corpus, "chunk", fname), "index": i}
                with open(os.path.join(self.db_dir, "_".join([corpus_name, "id2path.json"])), 'w') as f:
                    json.dump(self.dict, f, indent=4)
        print("Initialization finished!")

    def extract(self, ids: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        logger.debug(f"DocExtracter.extract() {ids=}")
        if isinstance(ids, dict):
            ids = [ids]
        if self.cache:
            output = []
            for i in ids:
                logger.debug(f"{i=}")
                item = self.dict[i] if type(i) == str else self.dict[i["id"]]
                output.append(item)
        else:
            output = []
            for i in ids:
                item = self.dict[i] if type(i) == str else self.dict[i["id"]]
                output.append(json.loads(
                    open(os.path.join(self.db_dir, item["fpath"])).read().strip().split('\n')[item["index"]]))
        return output

##############
# Copied from MedRAG/src/data/statpearls.py
##############
def download_statpearls(data_dir):
    fnames = sorted([fname for fname in os.listdir(f"{data_dir}/statpearls/statpearls_NBK430685") if fname.endswith("nxml")])
    if not os.path.exists(f"{data_dir}/statpearls/chunk"):
        os.makedirs(f"{data_dir}/statpearls/chunk")
    for fname in tqdm.tqdm(fnames):
        fpath = os.path.join(f"{data_dir}/statpearls/statpearls_NBK430685", fname)
        saved_text = extract(fpath)
        if len(saved_text) > 0:
            with open("{}/statpearls/chunk/{:s}".format(data_dir, fname.replace(".nxml", ".jsonl")), 'w') as f:
                f.write('\n'.join(saved_text))


def extract_text(element):
    text = (element.text or "").strip()

    for child in element:
        text += (" " if len(text) else "") + extract_text(child)
        if child.tail and len(child.tail.strip()) > 0:
            text += (" " if len(text) else "") + child.tail.strip()
    return text.strip()

def is_subtitle(element):
    if element.tag != 'p':
        return False
    if len(list(element)) != 1:
        return False
    if list(element)[0].tag != 'bold':
        return False
    if list(element)[0].tail and len(list(element)[0].tail.strip()) > 0:
        return False
    return True

def extract(fpath):
    fname = fpath.split("/")[-1].replace(".nxml", "")
    tree = ET.parse(fpath)
    title = tree.getroot().find(".//title").text
    sections = tree.getroot().findall(".//sec")
    saved_text = []
    j = 0
    last_text = None
    for sec in sections:
        sec_title = sec.find('./title').text.strip()
        sub_title = ""
        prefix = " -- ".join([title, sec_title])
        last_text = None
        last_json = None
        last_node = None
        for ch in sec:
            if is_subtitle(ch):
                last_text = None
                last_json = None
                sub_title = extract_text(ch)
                prefix = " -- ".join(prefix.split(" -- ")[:2] + [sub_title])
            elif ch.tag == 'p':
                curr_text = extract_text(ch)
                if len(curr_text) < 200 and last_text is not None and len(last_text + curr_text) < 1000:
                    last_text = " ".join([last_json['content'], curr_text])
                    last_json = {"id": last_json['id'], "title": last_json['title'], "content": last_text}
                    last_json["contents"] = concat(last_json["title"], last_json["content"])
                    saved_text[-1] = json.dumps(last_json)
                else:
                    last_text = curr_text
                    last_json = {"id": '_'.join([fname, str(j)]), "title": prefix, "content": curr_text}
                    last_json["contents"] = concat(last_json["title"], last_json["content"])
                    saved_text.append(json.dumps(last_json))
                    j += 1
            elif ch.tag == 'list':
                list_text = [extract_text(c) for c in ch]
                if last_text is not None and len(" ".join(list_text) + last_text) < 1000:
                    last_text = " ".join([last_json["content"]] + list_text)
                    last_json = {"id": last_json['id'], "title": last_json['title'], "content": last_text}
                    last_json["contents"] = concat(last_json["title"], last_json["content"])
                    saved_text[-1] = json.dumps(last_json)
                elif len(" ".join(list_text)) < 1000:
                    last_text = " ".join(list_text)
                    last_json = {"id": '_'.join([fname, str(j)]), "title": prefix, "content": last_text}
                    last_json["contents"] = concat(last_json["title"], last_json["content"])
                    saved_text.append(json.dumps(last_json))
                    j += 1
                else:
                    last_text = None
                    last_json = None
                    for c in list_text:
                        saved_text.append(json.dumps({"id": '_'.join([fname, str(j)]), "title": prefix, "content": c, "contents": concat(prefix, c)}))
                        j += 1
                if last_node is not None and is_subtitle(last_node):
                    sub_title = ""
                    prefix = " -- ".join([title, sec_title])
            last_node = ch
    return saved_text

