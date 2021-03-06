from graphviz import Graph
import argparse

def create_graph(in_filename, out_filename, engine):

    circuit = Graph('circuit', filename=out_filename, engine=engine)
    circuit.body.append('overlap=false')
    nmos = Graph('cluster_0')
    nmos.body.append('color=black')
    nmos.body.append('label="nmos"')
    pmos = Graph('cluster_1')
    pmos.body.append('color=black')
    pmos.body.append('label="pmos"')
    pos = Graph('cluster_2')
    pos.body.append('color=black')
    gnd = Graph('cluster_3')
    gnd.body.append('color=black')
    inp = Graph('cluster_4')
    inp.body.append('color=black')
    outp = Graph('cluster_5')
    outp.body.append('color=black')

    top_level_nodes = []
    node_hints = {}
    conn_ref = {}
    conn_edge_color = ['red','blue' ,'green' ,'black']

    with open(in_filename, "r") as spicef:
        for line in spicef:
            if line[0] not in ".*\n":
                t_name, c1, c2, c3, c4, fet_type, width, length, nfin = line.split(" ")

                if fet_type == "nfet":
                    target_graph = nmos
                    nmos.node(t_name,shape='diamond')
                    partial_id = "_n"
                elif fet_type == "pfet":
                    target_graph = pmos
                    pmos.node(t_name,shape='diamond')
                    partial_id = "_p"

                connections = [c1,c2,c3,c4]
                for i, conn in enumerate(connections):
                    if conn not in conn_ref:
                        conn_ref[conn] = []
                    if conn in top_level_nodes:
                        circuit.edge(t_name, conn, color=conn_edge_color[i])
                    else:
                        target_graph.edge(t_name, conn+partial_id, color=conn_edge_color[i])
                        if conn+partial_id not in conn_ref[conn]:
                            conn_ref[conn] += [conn+partial_id]

            elif ".SUBCKT" in line:
                top_level_nodes = line.strip().split(" ")[2:]
                #for node in top_level_nodes:
                #    circuit.node(node, shape='square')

            elif "*.PININFO" in line:
                node_info = line.strip().split(" ")[1:]
                for node_pair in node_info:
                    node, t = node_pair.split(":")
                    node_hints[t] = node_hints.get(t,[]) + [node]

                for node_t in node_hints:
                    nodes = node_hints[node_t]
                    if node_t == 'I':
                        target_graph = inp
                    elif node_t == 'O':
                        target_graph = outp
                    elif node_t == 'P':
                        target_graph = pos
                    elif node_t == 'G':
                        target_graph = gnd
                    else:
                        raise ValueError("Bad input")
                    for node in nodes:
                        target_graph.node(node, shape='square')


    for conn, parts in conn_ref.items():
        if len(parts) == 2:
            circuit.edge(conn, parts[0])
            circuit.edge(conn, parts[1])


    circuit.subgraph(nmos)
    circuit.subgraph(pmos)
    circuit.subgraph(inp)
    circuit.subgraph(outp)
    circuit.subgraph(pos)
    circuit.subgraph(gnd)
    return circuit

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create graphviz files from spice models')
    parser.add_argument('input_file', type=str, help='the input spice file')
    parser.add_argument('output_file', type=str, help='the target output graphviz file')
    parser.add_argument('--gv_engine', type=str, default="neato", help='graphviz display engine (default: neato): dot, neato, twopi, circo, fdp, sfdp, patchwork, osage')
    parser.add_argument('--skip_render', action='store_true', help='skip rendering output with graphviz')

    args = parser.parse_args()

    new_graph = create_graph(args.input_file, args.output_file, args.gv_engine)
    if args.skip_render:
        new_graph.save()
    else:
        new_graph.view()

