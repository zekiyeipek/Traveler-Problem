from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx
from graph import Graph
from query import Query
import sys

def read_transportation_network(file_path):
    graph = Graph()

    with open(file_path) as file:
        transport_type = None
        cities = None

        for line in file:
            line = line.strip()

            if line in {"Highway", "Airway", "Railway"}:
                transport_type = line
                cities = file.readline().strip().split()[1:]
                matrix_size = len(cities)

                matrix = [[0] * matrix_size for _ in range(matrix_size)]

                for i in range(matrix_size):
                    data = file.readline().strip().split()[1:]
                    for j, value in enumerate(data):
                        matrix[i][j] = value

                for i, city in enumerate(cities):
                    for j, neighbor in enumerate(cities):
                        if matrix[i][j] == '1':
                            graph.add_edge(city, neighbor, transport_type)

    return graph

def read_queries(file_path):
    queries = []
    with open(file_path) as file:
        for line in file:
            print(f"Debug: Reading query - {line}")
            data = line.strip().split()
            query_type = data[0]

            if query_type == 'Q1':
                transport_types = [data[i] for i in range(4, len(data), 2)] if len(data) > 3 else []
                queries.append(Query(query_type, data[1], data[2], transport_types=transport_types))
            elif query_type == 'Q2':
                if len(data) == 4 and data[3] == 'N':
                    queries.append(Query(query_type, data[1], data[2], n=-1))
                elif len(data) == 4:
                    n = int(data[3])
                    queries.append(Query(query_type, data[1], data[2], n=n))
                else:
                    print(f"Not enough values for Q2 query. Skipping.")
            elif query_type == 'Q3':
                transport_type = data[3] if len(data) > 3 else None
                queries.append(Query(query_type, data[1], data[2], transport_types=[transport_type]))
            elif query_type == 'ADD':
                if data[1] == 'City':
                    city = data[2]
                    queries.append(Query(query_type, city, destination=""))
                elif data[1] == 'Path':
                    if len(data) == 6:
                        city = data[2]
                        neighbor = data[5]
                        transport_type = data[4]
                        # Ensure transport_type is added to the list
                        queries.append(Query(query_type, city, neighbor, transport_types=[transport_type]))
                    else:
                        print(f"Error: Invalid ADD Path query format. Skipping.")
                else:
                    print(f"Error: Invalid ADD query format - {line}. Skipping.")
    return queries


def find_paths(graph, source, destination, transport_types):
    return dfs(source, [], set(transport_types), destination, graph.graph)



def dfs(current_node, path, remaining_types, destination, graph):
    if current_node not in graph:
        return []

    if current_node == destination:
        return [path]

    paths = []
    for neighbor, transport_type in graph[current_node].items():
        type_value = transport_type if isinstance(transport_type, str) else transport_type.get('type', None)

        if type_value is not None and type_value in remaining_types:
            new_path = path + [(neighbor, transport_type)]
            new_types = remaining_types - {type_value}
            paths.extend(dfs(neighbor, new_path, new_types, destination, graph))

    return paths

def dfs_bonus(current_node, path, remaining_types, destination, graph):
    if current_node not in graph:
        return []

    if current_node == destination:
        return [path]

    paths = []
    for neighbor, transport_type in graph[current_node].items():
        type_value = transport_type if isinstance(transport_type, str) else transport_type.get('type', None)

        if type_value is not None and any(char.isdigit() for char in type_value):
            new_path = path + [(neighbor, transport_type)]
            new_types = remaining_types - {type_value}
            paths.extend(dfs_bonus(neighbor, new_path, new_types, destination, graph))

    return paths

def add_city(graph, city):
    if city not in graph.graph:
        graph.add_node(city)

def add_path(graph, source, dest, transport_type):
    if dest not in graph[source] or 'type' not in graph[source][dest]:
        graph.add_edge(source, dest, type=transport_type)
    else:
        print(f"Error: Path from {source} to {dest} with {transport_type} already exists.")
                
        
        

def parse_add_query(graph, query):
    params = query.type.split()

    if len(params) < 2:
        print("Error: Invalid ADD query format. Skipping.", file=sys.stdout)
        return

    if params[1] == 'City':
        parse_add_city_query(graph, query)
    elif params[1] == 'Path':
        parse_add_path_query(graph, query)
    else:
        print(f"Error: Unknown ADD query type {params[1]}. Skipping.", file=sys.stdout)
        
        

def parse_add_city_query(graph, query):
    _, city_name = query.type.split()
    add_city(graph, city_name)

def parse_add_path_query(graph, query):
    params = query.type.split()
    print(f"Debug: Parsed ADD Path query - {params}")

    if len(params) != 6:
        print(f"Error: Invalid ADD Path query format - {query.type}. Skipping.", file=sys.stdout)
        return

    _, source_city, _, transport_type, _, target_city = params

    print(f"Debug: Parsed ADD Path query - Source: {source_city}, Target: {target_city}, Transport Type: {transport_type}", file=sys.stdout)

    add_city(graph, source_city)
    add_city(graph, target_city)

    try:
        # Extract transport_type from data[3] and ensure it's numeric before converting to string
        transport_type = ''.join([c for c in transport_type if c.isnumeric()])

        if target_city not in graph[source_city] or transport_type not in graph[source_city][target_city].values():
            add_path(graph, source_city, target_city, transport_type)
            print(f"Path added from {source_city} to {target_city} with {transport_type}.", file=sys.stdout)
        else:
            print(f"Error: Path from {source_city} to {target_city} with {transport_type} already exists.", file=sys.stdout)
    except KeyError as e:
        print(f"Error: Invalid ADD Path query format - {query.type}. Skipping. (Error details: {e})", file=sys.stdout)
        
    
        

def find_common_nodes(graph, source1, source2):
    neighbors1 = set(graph.graph.neighbors(source1))
    neighbors2 = set(graph.graph.neighbors(source2))
    common_nodes = neighbors1.intersection(neighbors2)
    return list(common_nodes)

def find_shortest_path(graph, source, destination, transport_type):
    paths = find_paths(graph, source, destination, [transport_type])
    if paths:
        min_distance_path = min(paths, key=lambda path: sum(edge[1] == transport_type for edge in path))
        return min_distance_path
    return None

def process_queries(graph, queries):
    for query in queries:
        if query.type == 'Q1':
            if query.transport_types is not None and len(query.transport_types) > 0:
                paths = find_paths(graph, query.source, query.destination, query.transport_types)
                if paths:
                    print(f"Q1: Paths from {query.source} to {query.destination} with {query.transport_types[0]}:")
                    for path in paths:
                        formatted_path = [f"{node} {transport_type}" for node, transport_type in path]
                        formatted_path.append(query.destination)  # Add the destination city
                        print(" ".join(formatted_path))
                else:
                    print(f"No paths found from {query.source} to {query.destination} with {query.transport_types[0]}.")
            else:
                print(f"Not enough values for Q1 query. Skipping.")
        elif query.type == 'Q2':
            if query.n == -1:
                print(f"Q2: Common nodes between {query.source} and {query.destination}: {find_common_nodes(graph, query.source, query.destination)}")
            elif len(query.transport_types) == 1:
                print(f"Not enough values for Q2 query. Skipping.")
        elif query.type == 'Q3':
            min_distance_path = find_shortest_path(graph, query.source, query.destination, query.transport_types[0])
            if min_distance_path:
                formatted_path = [f"{node} {transport_type}" for node, transport_type in min_distance_path]
                formatted_path.append(query.destination)  # Add the destination city
                print(f"Q3: Shortest path from {query.source} to {query.destination} with {query.transport_types[0]}: {' '.join(formatted_path)}")
            else:
                print(f"No path found from {query.source} to {query.destination} with {query.transport_types[0]}.")
        elif query.type == 'ADD':
            parse_add_query(graph, query)
        elif query.type.startswith('ADD City'):
            parse_add_city_query(graph, query)
        elif query.type.startswith('ADD Path'):
            parse_add_path_query(graph, query)
        else:
            print(f"Unknown query type: {query.type}", file=sys.stdout)
            
            
def visualize_graph(graph):
    if graph.graph.edges():
        pos = nx.spring_layout(graph.graph)

        # Draw nodes
        nx.draw_networkx_nodes(graph.graph, pos, node_color='lightblue', edgecolors='black', node_size=700)

        # Create a color map for edge types
        edge_color_map = {'Highway': 'red', 'Airway': 'blue', 'Railway': 'green'}

        # Draw edges with different colors based on transportation type
        edge_colors = []
        for edge in graph.graph.edges():
            edge_data = graph.graph[edge[0]][edge[1]]
            edge_type = edge_data.get('type', None)
            if edge_type in edge_color_map:
                edge_colors.append(edge_color_map[edge_type])
            else:
                edge_colors.append('black')  # Default color if type is not found

        # Draw edges with different colors based on transportation type
        nx.draw_networkx_edges(graph.graph, pos, edge_color=edge_colors, width=2)

        # Draw labels
        nx.draw_networkx_labels(graph.graph, pos, font_weight='bold')

        # Create a legend
        legend_entries = []
        for transport_type, color in edge_color_map.items():
            legend_entries.append(Line2D([0], [0], marker='o', color='w', label=transport_type,
                                          markerfacecolor=color, markersize=10))
        plt.legend(handles=legend_entries)

        plt.show()
    else:
        print("No edges to visualize.")

def main():
    graph = read_transportation_network("transportation_network.inp")
    queries = read_queries("query.inp")

    # Redirect stdout to a file
    sys.stdout = open("output_results.txt", "w")

    # Add debug prints
    print("Cities in the graph:", list(graph.graph.nodes()))
    print("Edges in the graph:", list(graph.graph.edges()))

    process_queries(graph, queries)

    # Visualize the graph after processing queries
    visualize_graph(graph)

    # Close the redirected stdout
    sys.stdout.close()
    
if __name__ == "__main__":
    main()