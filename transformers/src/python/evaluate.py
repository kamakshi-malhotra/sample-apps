#! /usr/bin/env python3

import os
import sys
import csv
import json
import time
import urllib

from transformers import AutoTokenizer


data_dir = sys.argv[2] if len(sys.argv) > 2 else "msmarco"
queries_file = os.path.join(data_dir, "test-queries.tsv")

model_name = sys.argv[1]
sequence_length = 128
tokenizer = AutoTokenizer.from_pretrained(model_name)


def vespa_search(query, tokens, hits=10):
    query_terms = [ "content CONTAINS \"{}\"".format(term) for term in query.split(" ") if len(term) > 0 ]
    tokens_str = "[" + ",".join( [ str(i) for i in tokens ]) + "]"
    url = "http://localhost:8080/search/?hits={}&timeout=10&ranking={}&yql={}&ranking.features.query(input)={}".format(
              hits,
              "transformer",
              urllib.parse.quote_plus("select * from sources * where " + " or ".join(query_terms) + ";"),
              urllib.parse.quote_plus(tokens_str)
          )
    print("Querying: " + url)
    print("select * from sources * where " + " or ".join(query_terms) + ";")
    return json.loads(urllib.request.urlopen(url).read())


def main():
    view_max = 1
    with open(queries_file, encoding="utf8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            query = row[0].strip()
            print("Query: " + query)

            tokens = tokenizer.encode_plus(query, add_special_tokens=False, max_length=sequence_length, pad_to_max_length=True)["input_ids"]
            result = vespa_search(query, tokens)

            print(json.dumps(result, indent=2))

            view_max -= 1
            if view_max == 0:
                break



if __name__ == "__main__":
    main()
