import docx2txt
from random import shuffle
from itertools import combinations


class LocalSensitiveHashing:
    def __init__(self, document_dict: dict):
        self.document_dict = document_dict
        self.n_minhash_vectors = 20
        self.n_band = 10

    def prosecutor(self):
        self.shingle_set_dict = self.create_shingle_set_list()
        self.vocabulary = self.create_vocabulary(self.shingle_set_dict)
        self.one_hot_dict = self.one_hot(self.vocabulary)

        # we create 20 minhash vectors
        minhash_func = self.build_minhash_func(len(self.vocabulary), self.n_minhash_vectors)

        signature_dict = self.create_hashes(self.vocabulary, minhash_func, self.one_hot_dict)
        # similarity_search = self.jaccard(set(signature_dict['a']), set(signature_dict['b'])), self.jaccard(self.shingle_set_dict['a'], self.shingle_set_dict['b'])
        band_subvecs_dict = self.split_vector(signature_dict, self.n_band)
        self.show_candidate_pairs(band_subvecs_dict)

    def shingle(self, text: str, k: int):
        shingle_set = []
        for i in range(len(text) - k + 1):
            shingle_set.append(text[i:i+k])
        return set(shingle_set)
    
    def create_shingle_set_list(self):
        shingle_set_dict = {}
        for key,value in self.document_dict.items():
            shingle_set_dict[key] = self.shingle(value, 3)
        return shingle_set_dict
    
    def create_vocabulary(self, shingle_set_dict):
        vocabulary = set()
        for key,value in shingle_set_dict.items():
            vocabulary.update(value)
        return list(vocabulary)
    
    def one_hot(self, vocabulary):
        one_hot_dict = {}
        for key, value in self.document_dict.items():
            one_hot_dict[key] = [1 if x in value else 0 for x in vocabulary]
        return one_hot_dict
    
    def create_hash_func(self, size: int):
        # function for creating the hash vector/function
        hash_ex = list(range(1, size+1))
        shuffle(hash_ex)
        return hash_ex

    def build_minhash_func(self, vocab_size: int, nbits: int):
        # function for building multiple minhash vectors
        hashes = []
        for _ in range(nbits):
            hashes.append(self.create_hash_func(vocab_size))
        return hashes
    
    def create_hash(self, vocabulary, minhash_func, vector: list):
        # use this function for creating our signatures (eg the matching)
        signature = []
        for func in minhash_func:
            for i in range(1, len(vocabulary)+1):
                idx = func.index(i)
                signature_val = vector[idx]
                if signature_val == 1:
                    signature.append(idx)
                    break
        return signature
    
    def create_hashes(self, vocabulary, minhash_func, vector_list):
        signature_dict = {}
        for key,value in vector_list.items():
            signature_dict[key] = self.create_hash(vocabulary, minhash_func, value)
        return signature_dict
    
    def jaccard(self, x, y):
        return len(x.intersection(y)) / len(x.union(y))
    
    def split_vector(self, signature_dict, b):
        subvecs_dict = {}
        for key,value in signature_dict.items():
            assert len(value) % b == 0
            r = int(len(value) / b)
            # code splitting signature in b parts
            subvecs = []
            for i in range(0, len(value), r):
                subvecs.append(value[i : i+r])
            subvecs_dict[key] = subvecs
        return subvecs_dict
    
    def show_candidate_pairs(self, band_subvecs_dict: dict):
        band_subvecs_list = list(band_subvecs_dict.items())
        num_bands = len(band_subvecs_list)

        # for i in range(num_bands - 1):
        #     for j in range(i + 1, num_bands):
        #         for a_rows, b_rows in zip(band_subvecs_list[i][1], band_subvecs_list[j][1]):
        #             if a_rows == b_rows:
        #                 print(f"Candidate pair {band_subvecs_list[i][0]}->{band_subvecs_list[j][0]}: {a_rows} == {b_rows}")
        #                 # we only need one band to match
        #                 break

        # Generate all possible combinations of band_subvecs_list items
        for comb in combinations(band_subvecs_list, 2):
            for a_rows, b_rows in zip(comb[0][1], comb[1][1]):
                if a_rows == b_rows:
                    print(f"Candidate pair {comb[0][0]} <-> {comb[1][0]}: {a_rows} == {b_rows}")
                    # we only need one band to match
                    break

if __name__ == "__main__":
    # Extract Text From the Word document
    document_dict = {
        "D1.docx" : docx2txt.process("D1.docx"),
        "D2.docx" : docx2txt.process("D2.docx"),
        "D3.docx" : docx2txt.process("D3.docx")
    }
    lsh = LocalSensitiveHashing(document_dict)
    lsh.prosecutor()