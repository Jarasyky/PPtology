#!/usr/bin/env python3
import argparse
from pathlib import Path

import pandas as pd

from convert import xml_to_json_graph


def build_nodes_dataframe(nodes):
    # find maximum number of data values across all nodes
    max_data_len = max((len(n.get("data", [])) for n in nodes), default=0)

    rows = []
    for n in nodes:
        row = {
            "id": n.get("id"),
            "type": n.get("type"),
        }
        data_vals = n.get("data", [])
        for i in range(max_data_len):
            col_name = f"data_{i + 1}"
            row[col_name] = data_vals[i] if i < len(data_vals) else None
        rows.append(row)

    return pd.DataFrame(rows)


def build_edges_dataframe(edges):
    rows = []
    for e in edges:
        f = e.get("from", {})
        t = e.get("to", {})

        row = {
            "from_node": f.get("node"),
            "from_port": f.get("port"),
            "to_node": t.get("node"),
            "to_port": t.get("port"),
            "pressure": e.get("pressure"),
            "enthalpy": e.get("enthalpy"),
            "flow": e.get("flow"),
            "temperature": e.get("temperature"),
        }
        rows.append(row)

    return pd.DataFrame(rows)


def xml_to_excel(xml_path: str | Path, xlsx_path: str | Path):
    graph = xml_to_json_graph(xml_path)
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    df_nodes = build_nodes_dataframe(nodes)
    df_edges = build_edges_dataframe(edges)

    xlsx_path = Path(xlsx_path)
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        df_nodes.to_excel(writer, sheet_name="nodes", index=False)
        df_edges.to_excel(writer, sheet_name="edges", index=False)


def main():
    parser = argparse.ArgumentParser(
        description="Export turbine XML nodes and edges to Excel"
    )
    parser.add_argument("input_xml", help="Path to the XML file")
    parser.add_argument("output_xlsx", help="Path to the Excel file to create")
    args = parser.parse_args()

    xml_to_excel(args.input_xml, args.output_xlsx)


if __name__ == "__main__":
    main()