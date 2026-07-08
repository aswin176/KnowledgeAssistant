"use client";

import { useEffect, useRef } from "react";
import { Network } from "vis-network";
import { DataSet } from "vis-data";

interface GraphNode {
  id: string;
  name?: string;
  _labels?: string[];
}

interface GraphEdge {
  type: string;
  start?: string;
  end?: string;
}

interface GraphViewerProps {
  nodes: GraphNode[];
  relationships: GraphEdge[];
  centerId?: string;
  onNodeClick?: (nodeId: string) => void;
}

const LABEL_COLORS: Record<string, string> = {
  Person: "#3b82f6",
  Student: "#8b5cf6",
  Company: "#10b981",
  Skill: "#f59e0b",
  City: "#ef4444",
  Event: "#ec4899",
  Certification: "#06b6d4",
  default: "#6b7280",
};

export function GraphViewer({ nodes, relationships, centerId, onNodeClick }: GraphViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const networkRef = useRef<Network | null>(null);

  useEffect(() => {
    if (!containerRef.current || nodes.length === 0) return;

    const visNodes = new DataSet(
      nodes.map((n) => {
        const label = n._labels?.[0] || "default";
        return {
          id: n.id,
          label: n.name || n.id.slice(0, 8),
          color: {
            background: LABEL_COLORS[label] || LABEL_COLORS.default,
            border: centerId === n.id ? "#ffffff" : LABEL_COLORS[label] || LABEL_COLORS.default,
          },
          borderWidth: centerId === n.id ? 3 : 1,
          font: { color: "#e5e7eb", size: 14 },
          shape: label === "Company" ? "box" : "dot",
          size: centerId === n.id ? 25 : 18,
        };
      })
    );

    const visEdges = new DataSet(
      relationships.map((r, i) => ({
        id: i,
        from: r.start,
        to: r.end,
        label: r.type,
        arrows: "to",
        color: { color: "#4b5563", highlight: "#9ca3af" },
        font: { color: "#9ca3af", size: 10, align: "middle" },
        smooth: { type: "curvedCW", roundness: 0.2 },
      }))
    );

    const network = new Network(
      containerRef.current,
      { nodes: visNodes, edges: visEdges },
      {
        physics: {
          enabled: true,
          barnesHut: { gravitationalConstant: -3000, springLength: 150 },
        },
        interaction: { hover: true, tooltipDelay: 200, zoomView: true },
        layout: { improvedLayout: true },
      }
    );

    if (onNodeClick) {
      network.on("click", (params) => {
        if (params.nodes.length > 0) {
          onNodeClick(String(params.nodes[0]));
        }
      });
    }

    networkRef.current = network;
    return () => {
      network.destroy();
    };
  }, [nodes, relationships, centerId, onNodeClick]);

  return (
    <div
      ref={containerRef}
      className="h-full w-full rounded-lg border border-border bg-background"
    />
  );
}
