"use client";

import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

type JobItem = {
  name?: string;
  description?: string;
  status?: string;
  schedule?: string;
};

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobItem[]>([]);

  useEffect(() => {
    api.getJobs().then((data) => setJobs(data.items || []));
  }, []);

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-semibold">Background Jobs</h1>
          <p className="text-muted-foreground">Scheduled maintenance and update jobs</p>
        </div>
        <div className="grid gap-4">
          {jobs.map((job, i) => (
            <Card key={i}>
              <CardHeader>
                <CardTitle className="text-base">{job.name ?? "Unnamed job"}</CardTitle>
              </CardHeader>
              <CardContent className="text-sm space-y-1">
                <p className="text-muted-foreground">{job.description ?? "No description"}</p>
                <p>Status: <span className="font-medium">{job.status ?? "unknown"}</span></p>
                <p>Schedule: {job.schedule ?? "Not scheduled"}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
}
