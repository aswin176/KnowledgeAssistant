"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

export default function CompanyDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [company, setCompany] = useState<Record<string, unknown> | null>(null);

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
          <h1 className="text-2xl font-semibold mt-2">{company.name as string}</h1>
        </div>
        <Card>
          <CardHeader>
            <CardTitle>Company Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            {company.industry && <p><span className="font-medium">Industry:</span> {company.industry as string}</p>}
            {company.website && (
              <p>
                <span className="font-medium">Website:</span>{" "}
                <a href={company.website as string} className="text-primary hover:underline" target="_blank" rel="noopener">
                  {company.website as string}
                </a>
              </p>
            )}
            {company.description && <p className="text-muted-foreground">{company.description as string}</p>}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
