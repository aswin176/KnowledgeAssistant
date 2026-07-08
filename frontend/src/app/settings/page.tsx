"use client";

import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

type SettingsData = {
  llm_model?: string;
  ollama_model?: string;
  supported_import_formats?: string[];
};

type HealthData = {
  status?: string;
  neo4j?: boolean;
  llm?: boolean;
  version?: string;
};

export default function SettingsPage() {
  const [settings, setSettings] = useState<SettingsData | null>(null);
  const [health, setHealth] = useState<HealthData | null>(null);

  useEffect(() => {
    api.getSettings().then(setSettings);
    api.health().then(setHealth);
  }, []);

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-semibold">Settings</h1>
          <p className="text-muted-foreground">System configuration and status</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>System Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Overall</span>
                <span className={health?.status === "healthy" ? "text-green-500" : "text-yellow-500"}>
                  {health?.status ?? "Unknown"}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Neo4j</span>
                <span>{health?.neo4j ? "Connected" : "Disconnected"}</span>
              </div>
              <div className="flex justify-between">
                <span>LLM (Ollama)</span>
                <span>{health?.llm ? "Available" : "Unavailable"}</span>
              </div>
              <div className="flex justify-between">
                <span>Version</span>
                <span>{health?.version ?? "Unknown"}</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>LLM Model</span>
                <span>{settings?.ollama_model ?? settings?.llm_model ?? "Unknown"}</span>
              </div>
              <div className="flex justify-between">
                <span>Import Formats</span>
                <span>{settings?.supported_import_formats?.join(", ") ?? "None"}</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
