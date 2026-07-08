"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

type CompanyDetail = {
  id?: string;
  name?: string;
  industry?: string;
  website?: string;
  description?: string;
};

export default function CompanyDetailPage() {
  const params = useParams();
  const id = typeof params.id === "string" ? params.id : "";
  const [company, setCompany] = useState<CompanyDetail | null>(null);

  useEffect(() => {
    if (id) api.getCompany(id).then(setCompany);
  }, [id]);

  if (!company) {
    return (
      <DashboardLayout>
        <div className="p-6">Loading...</div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div>
          <Link href="/company" className="text-sm text-muted-foreground hover:text-primary">
            ← Back to Companies
          </Link>
          <h1 className="text-2xl font-semibold mt-2">{company.name ?? "Unnamed company"}</h1>
        </div>
        <Card>
          <CardHeader>
            <CardTitle>Company Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            {company.industry && <p><span className="font-medium">Industry:</span> {company.industry}</p>}
            {company.website && (
              <p>
                <span className="font-medium">Website:</span>{" "}
                <a href={company.website} className="text-primary hover:underline" target="_blank" rel="noopener">
                  {company.website}
                </a>
              </p>
            )}
            {company.description && <p className="text-muted-foreground">{company.description}</p>}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
