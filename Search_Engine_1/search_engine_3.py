import pandas as pd
from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import json
from nltk.corpus import wordnet


def word_net(terms):
    # TODO: without corona
    # TODO: think if save num of words or set
    # TODO: לחשוב על דרך לתת למילים המוספות פחות משקל
    extended_terms = set(terms)
    for query_word in terms:
        # print("word: " + query_word)
        synset = wordnet.synsets(query_word)
        if len(synset) > 0:
            synset_lemmas = synset[0].lemmas()
            if len(synset_lemmas) > 3:synset_lemmas = synset_lemmas[:3]  # add not more than 3
            # print("sort list is: ")
            for syn in synset_lemmas:
                name = syn.name()
                if name.islower() and not name.__contains__('_') and not name.__contains__('-'):
                    extended_terms.add(name)
                    # print(name)
    return extended_terms


# DO NOT CHANGE THE CLASS NAME
class SearchEngine:

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation, but you must have a parser and an indexer.
    def __init__(self, config=None):
        if not config:
            self._config = ConfigClass()
        else:
            self._config = config
        self._parser = Parse()
        self._indexer = Indexer(config)
        self._model = None
        self._reader = ReadFile(self._config.get__corpusPath())

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implmentation as you see fit.
    def build_index_from_parquet(self, fn):
        """
        Reads parquet file and passes it to the parser, then indexer.
        Input:
            fn - path to parquet file
        Output:
            No output, just modifies the internal _indexer object.
        """
        df = pd.read_parquet(fn, engine="pyarrow")
        documents_list = df.values.tolist()
        # documents_list = self._reader.get_next_file()  # TODO: from old maybe delete
        # Iterate over every document in the file
        number_of_documents = 0
        # while (documents_list != None):  # TODO: from old maybe delete
        for idx, document in enumerate(documents_list):
            # parse the document
            parsed_document = self._parser.parse_doc(document)
            if not parsed_document:  # TODO: from old check if necessary
                continue
            number_of_documents += 1
            # index the document data
            self._indexer.add_new_doc(parsed_document)
        # documents_list = self._reader.get_next_file()  # TODO: from old maybe delete

        self._indexer.check_pending_list()
        self._indexer.calculate_and_add_idf()
        self._indexer.calculate_sigma_Wij()
        # save inverted index
        with open("inverted_index.json", 'w') as json_file:
            json.dump(self._indexer.inverted_idx, json_file)

        # save posting dict
        with open("posting_file.json", 'w') as json_file:
            json.dump(self._indexer.postingDict, json_file)

        print('Finished parsing and indexing.')

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implmentation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        self._indexer.load_index(fn)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implmentation as you see fit.
    def load_precomputed_model(self, model_dir=None):
        """
        Loads a pre-computed model (or models) so we can answer queries.
        This is where you would load models like word2vec, LSI, LDA, etc. and
        assign to self._model, which is passed on to the searcher at query time.
        """
        pass

    def search(self, query, k=None):
        """
        Executes a query over an existing index and returns the number of
        relevant docs and an ordered list of search results.
        Input:
            query - string.
        Output:
            A tuple containing the number of relevant search results, and
            a list of tweet_ids where the first element is the most relavant
            and the last is the least relevant result.
        """
        terms, entities = self._parser.parse_sentence(query)
        query_as_list = terms + entities
        # no need to extend large query TODO: decide hoe much
        if len(terms) > 50:
            searcher = Searcher(self._parser, self._indexer, model=self._model)
            return searcher.search(query_as_list, k)
        # word net
        else:
            extended_query = word_net(terms)
            searcher = Searcher(self._parser, self._indexer, model=self._model)
            return searcher.search(extended_query, k)
            # return extended_query


def main():
    config = ConfigClass()
    search_engine = SearchEngine(config)
    # r'C:\Users\noaa\pycharm projects\search_engine_partC\Search_Engine_1\data\benchmark_data_train.snappy.parquet'#
    search_engine.build_index_from_parquet(
        r'C:\\Users\\Ophir Porat\\PycharmProjects\\search_engine_1\\data\benchmark_data_train.snappy.parquet')
    # search_engine.build_index_from_parquet(r'C:\\Users\\Ophir Porat\\PycharmProjects\\search_engine_1\\data\covid19_07-16.snappy.parquet')
    # search_engine.build_index_from_parquet(r'C:\\Users\\Ophir Porat\\PycharmProjects\\search_engine_1\\data\covid19_07-19.snappy.parquet')
    # results =search_engine.search("covid is fun 2020 US new  wear", 40)
    # for res in results[1]:
    #     print(res)





# word = "program"
# noaa = wordnet.synsets(word)[0].lemmas()
# for i in noaa:
#     print(i.name())

# query_as_list = ["hello", "word", "program", "program", "computer"]
# extended_query = set()
# for query_word in query_as_list:
#     print("word is: " + query_word)
#     synset = wordnet.synsets(query_word)
#     if len(synset) > 0:
#         synset_lemmas = synset[0].lemmas()
#         for syn in synset_lemmas[:2]:
#             name = syn.name()
#             if not name.__contains__('_') and not name.__contains__('-'):
#                 extended_query.add(name)
#                 print(name)
# extended_query.update(query_as_list)
# print(extended_query)
#

# print("wordnet")
# se = SearchEngine()
# query = "Coronavirus is less dangerous than the flu	coronavirus less dangerous flu"
# res = se.search(query)
# print(res)
# print("\n")
#
#
# print("thes")
# se5 = se5()
# query = "Coronavirus is less dangerous than the flu	coronavirus less dangerous flu"
# res = se.search(query)
# print(res)
# print("\n")