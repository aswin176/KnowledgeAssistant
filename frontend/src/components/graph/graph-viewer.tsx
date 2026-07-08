"use client";

import { useEffect, useRef } from "react";
import { Network } from "vis-network";
import type { GraphNode, GraphRelationship } from "@/lib/api";

interface GraphViewerProps {
  nodes: GraphNode[];
  relationships: GraphRelationship[];
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

    const visNodes = nodes.map((n) => {
      const label = n._labels?.[0] ?? "default";
      const color = LABEL_COLORS[label] ?? LABEL_COLORS.default;
      return {
        id: n.id,
        label: n.name ?? n.id.slice(0, 8),
        color: {
          background: color,
          border: centerId === n.id ? "#ffffff" : color,
        },
        borderWidth: centerId === n.id ? 3 : 1,
        font: { color: "#e5e7eb", size: 14 },
        shape: label === "Company" ? ("box" as const) : ("dot" as const),
        size: centerId === n.id ? 25 : 18,
      };
    });

    const visEdges = relationships.map((r, i) => ({
      id: `${r.type}-${i}`,
      from: r.start,
      to: r.end,
      label: r.type,
      arrows: "to" as const,
      color: { color: "#4b5563", highlight: "#9ca3af" },
      font: { color: "#9ca3af", size: 10, align: "middle" as const },
      smooth: { type: "curvedCW" as const, roundness: 0.2 },
    }));

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
