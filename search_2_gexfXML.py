# -*- coding: utf-8 -*-
"""Download data from Elasticsearch and convert it to Gexf/XML format."""
# Usage
# python search_2_gexfXML.py edward snowden
# python search_2_gexfXML.py juha nurmi
# python search_2_gexfXML.py ahmia

import networkx as nx  # Network modeling library
from elasticsearch import Elasticsearch # Elasticsearch connection
from urlparse import urlparse
import argparse  # To command line arguments


def query(graph, es, term, DOC_TYPE_READ ="tor"):
    """Make query and create a graph."""
    # Status of doc_type in the READ onion index
    index = "crawl"
    term = '"' + term + '"'
    print "Searching %s..." % term
    res = es.search(index=index, doc_type=DOC_TYPE_READ, q=term)
    size = res['hits']['total']
    print "READ Index onions/%s size is %d" % (DOC_TYPE_READ, size)
    start = 0
    limit = 100
    color = {'r': 0, 'g': 0, 'b': 240, 'a': 0.8} # blue
    while start < size:
        try:
            res = es.search(index=index, doc_type=DOC_TYPE_READ, from_=start, size=limit, q=term)
        except Exception as e:
            print e
            continue
        print "range=%d-%d, hits %d" % (start, start+limit, len(res['hits']['hits']))
        for hit in res['hits']['hits']:
            item = hit["_source"]
            onion_url = item["url"]
            if item["domain"][-6:] != ".onion":
                continue
            source_added = False
            for link in item["links"]:
                if not source_added and not onion_url in graph:
                    graph.add_node(onion_url)
                    c = {'r': 240, 'g': 0, 'b': 0, 'a': 0.8} # red
                    graph.node[onion_url]['viz'] = {'color': c}
                    source_added = True
                link = link["link"].encode('ascii', 'ignore')
                # If it is a link to onion domain
                if link[0:7] == "http://" and link[23:30] == ".onion/":
                    if not link in graph:
                        graph.add_node(link)
                        graph.node[link]['viz'] = {'color': color}
                    graph.add_edge(onion_url, link)
                else: # It is a link to non-onion domain
                    graph.add_edge(onion_url, "PUBLIC_WWW")

        start = start + limit

def use_data(es, term):
    """Use Elasticsearch data."""
    graph = nx.Graph()
    # Public WWW is one node
    graph.add_node("PUBLIC_WWW")
    graph.node["PUBLIC_WWW"]['viz'] = {'color': {'r': 0, 'g': 240, 'b': 0, 'a': 0.8}}

    # Add onion site linking
    # Address is a node
    query(graph, es, term)

    print "The number of nodes %d" % len(graph.nodes())
    print "The number of edges %d" % len(graph.edges())
    gexf = term.replace(" ", "_") + ".gexf"
    nx.write_gexf(graph, gexf, encoding='utf-8', prettyprint=True, version='1.2draft')

def get_command_args(parser):
    """Reads command line arguments."""
    parser.add_argument('term', nargs='*')
    args = parser.parse_args()
    term = args.term
    if term:
        term = ' '.join(term)
        print "Search patterns according to search term = %s" % term
    else:
        print "You need to give search term(s)."
        raise SystemExit
    return term

def main():
    """Main function."""
    desc = "Search patterns according to search term."
    parser = argparse.ArgumentParser(description=desc)
    term = get_command_args(parser)
    es = Elasticsearch(timeout=60,port=9200)
    use_data(es, term)

if __name__ == '__main__':
    main()
