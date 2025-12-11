#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import json
from pathlib import Path


def _parse_number(s: str):
    try:
        n = float(s)
        return int(n) if n.is_integer() else n
    except ValueError:
        return s


def parse_node(node_el: ET.Element) -> dict:
    node_id = node_el.attrib["ID"]
    node_type = int(node_el.attrib["type"])

    values = []
    data_container = node_el.find("nodedata")
    if data_container is not None:
        for d in data_container.findall("data"):
            v = d.attrib.get("value")
            if v is not None:
                values.append(_parse_number(v))

    return {
        "id": node_id,
        "type": node_type,
        "data": values,
    }


def _parse_edge_end(value: str) -> dict:
    node_id, port_str = value.split(",", 1)
    return {"node": node_id, "port": int(port_str)}


def parse_edge(edge_el: ET.Element) -> dict:
    a = edge_el.attrib
    return {
        "from": _parse_edge_end(a["start"]),
        "to": _parse_edge_end(a["end"]),
        "pressure": float(a["pressure"]),
        "enthalpy": float(a["enthalpy"]),
        "flow": float(a["flow"]),
        "temperature": float(a["temperature"]),
    }


def xml_to_json_graph(xml_path: str | Path) -> dict:
    xml_path = Path(xml_path)
    tree = ET.parse(xml_path)
    root = tree.getroot()

    nodes_el = root.find("nodes")
    edges_el = root.find("edges")

    if nodes_el is None or edges_el is None:
        raise RuntimeError("XML does not contain <nodes> and <edges> sections")

    # NOW nodes is an array
    nodes = [parse_node(node_el) for node_el in nodes_el.findall("node")]

    # edges stay as an array
    edges = [parse_edge(e) for e in edges_el.findall("edge")]

    return {"nodes": nodes, "edges": edges}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert turbine XML to JSON graph")
    parser.add_argument("input_xml", help="Path to the XML file")
    parser.add_argument("output_json", help="Path to write JSON output")
    args = parser.parse_args()

    graph = xml_to_json_graph(args.input_xml)
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
