"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getStatus } from "@/lib/api";
import type { AgentStatus } from "@/lib/types";

export default function StatusPage() {
  const [status, setStatus] = useState<AgentStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getStatus()
      .then(setStatus)
      .catch(() => setError("Cannot connect to agent. Is the backend running on port 8000?"));
  }, []);

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle className="text-destructive">Connection Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">{error}</p>
            <p className="text-sm mt-2">
              Start the backend: <code className="bg-muted px-1 rounded">open_intern start</code>
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!status) {
    return <p className="text-muted-foreground">Loading...</p>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Dashboard</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">Agent</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{status.name}</p>
            <p className="text-sm text-muted-foreground">{status.role}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">LLM</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{status.llm_model}</p>
            <Badge variant="secondary">{status.llm_provider}</Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">Platform</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold capitalize">{status.platform}</p>
            <Badge variant="outline" className="text-green-600 border-green-600">Online</Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">Memories</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{status.memory_stats.total}</p>
            <p className="text-xs text-muted-foreground">
              {status.memory_stats.shared} shared / {status.memory_stats.channel} channel / {status.memory_stats.personal} personal
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
