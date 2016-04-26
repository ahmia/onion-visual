# -*- coding: utf-8 -*-
"""Download data from Elasticsearch and convert it to Gexf/XML format."""

import networkx as nx  # Network modeling library
from elasticsearch import Elasticsearch # Elasticsearch connection
from urlparse import urlparse


def query(graph, es, color, DOC_TYPE_READ ="tor"):
    """Make query and create a graph."""
    # Status of doc_type in the READ onion index
    index = "crawl"
    res = es.search(index=index, doc_type=DOC_TYPE_READ) #, q=title:ahmia)
    size = res['hits']['total']
    print "READ Index onions/%s size is %d" % (DOC_TYPE_READ, size)
    start = 0
    limit = 100
    while start < size:
        try:
            res = es.search(index=index, doc_type=DOC_TYPE_READ, from_=start, size=limit) #, q=title:ahmia)
        except Exception as e:
            print e
            continue
        print "range=%d-%d, hits %d" % (start, start+limit, len(res['hits']['hits']))
        for hit in res['hits']['hits']:
            item = hit["_source"]
            onion = item["domain"]
            if onion[-6:] != ".onion":
                continue
            source_added = False
            for link in item["links"]:
                link = link["link"].encode('ascii', 'ignore')
                if not source_added and not onion in graph:
                    graph.add_node(onion)
                    graph.node[onion]['viz'] = {'color': color}
                    source_added = True
                # If it is a link to onion domain
                if link[0:7] == "http://" and link[23:30] == ".onion/":
                    parsed_uri = urlparse(link)
                    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
                    domain = domain[7:29]
                    if not domain in graph:
                        graph.add_node(domain)
                        graph.node[domain]['viz'] = {'color': color}
                    graph.add_edge(onion, domain)
                else: # It is a link to non-onion domain
                    graph.add_edge(onion, "PUBLIC_WWW")

        start = start + limit

def use_data(es):
    """Use Elasticsearch data."""
    graph = nx.Graph()
    # Public WWW is one node
    graph.add_node("PUBLIC_WWW")
    graph.node["PUBLIC_WWW"]['viz'] = {'color': {'r': 0, 'g': 240, 'b': 0, 'a': 0.8}}

    color = {'r': 200, 'g': 0, 'b': 255, 'a': 0.8} # redblue
    # Add onion site linking
    # A node is an onion domain
    query(graph, es, color)

    print "The number of nodes %d" % len(graph.nodes())
    print "The number of edges %d" % len(graph.edges())
    nx.write_gexf(graph, "onionlinks_no_directories.gexf", encoding='utf-8', prettyprint=True, version='1.2draft')

def main():
    """Main function."""
    es = Elasticsearch(timeout=60,port=9200)
    use_data(es)

if __name__ == '__main__':
    main()
