import networkx as nx
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator


def create_bar_chart(dictionary, path, x_label, y_label, name):
    plt.clf()
    ax = plt.figure(figsize=(15, 5)).gca()
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    keys = list(dictionary.keys())
    values = list(dictionary.values())

    container = plt.bar(keys, values, align='edge', width=0.45)
    plt.bar_label(container, label_type='center')
    plt.xlim([0, len(keys)])
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(name)
    plt.savefig(path)


def construct_default_graph(path):
    graph = nx.DiGraph()
    graph.add_node('Hypernym')
    graph.add_node('Hyponym')
    graph.add_edge('Hypernym', 'Hyponym')
    plt.figure(figsize=(8, 8))
    pos = nx.circular_layout(graph)
    nx.draw(graph,
            pos,
            with_labels=True,
            node_color='gray',
            node_size=2500,
            font_size=11,
            font_weight='bold',
            edge_color='gray',
            arrows=True)
    plt.savefig(path)


def construct_relation_graph(data, dictionary, definition, path):
    graph = nx.DiGraph()
    for parent, children in data.items():
        if definition == parent or definition in children:
            graph.add_node(parent)
            graph.add_nodes_from(children)
            for child in children:
                graph.add_edge(parent, child)
    plt.figure(figsize=(6, 6))
    pos = nx.circular_layout(graph)

    colors = []
    for node in list(graph.nodes):
        if node == definition:
            colors.append('red')
        elif node in dictionary:
            colors.append('pink')
        else:
            colors.append('lightblue')

    sizes = [
        2000 if node_name == definition else 1500
        for node_name in list(graph.nodes)
    ]
    nx.draw(graph,
            pos,
            with_labels=True,
            node_color=colors,
            node_size=sizes,
            font_size=9,
            font_weight='bold',
            edge_color='gray',
            arrows=True)
    plt.margins(0.2, tight=False)
    plt.title('Ontology Graph')
    plt.savefig(path)
