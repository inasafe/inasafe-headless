# coding=utf-8
import json
import os
from safe.utilities.keyword_io import KeywordIO

__author__ = 'lucernae'


def read_metadata_from_file(filename):
    keywords_io = KeywordIO()
    keywords_dict = keywords_io.read_keywords_file(filename)
    return keywords_dict


if __name__ == '__main__':

    layer_filename = os.environ['LAYER_FILENAME']
    keywords = read_metadata_from_file(layer_filename)
    print json.dumps(keywords)
