"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { getConfig, updateIdentity, updateLLM } from "@/lib/api";

export default function SettingsPage() {
  const [name, setName] = useState("");
  const [role, setRole] = useState("");
  const [personality, setPersonality] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");

  const [provider, setProvider] = useState("");
  const [model, setModel] = useState("");
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(4096);
  const [dailyBudget, setDailyBudget] = useState(10);

  const [identityMsg, setIdentityMsg] = useState("");
  const [llmMsg, setLlmMsg] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getConfig()
      .then((cfg) => {
        setName(cfg.identity.name);
        setRole(cfg.identity.role);
        setPersonality(cfg.identity.personality);
        setAvatarUrl(cfg.identity.avatar_url || "");
        setProvider(cfg.llm.provider);
        setModel(cfg.llm.model);
        setTemperature(cfg.llm.temperature);
        setMaxTokens(cfg.llm.max_tokens_per_action);
        setDailyBudget(cfg.llm.daily_cost_budget_usd);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  async function saveIdentity() {
    try {
      const res = await updateIdentity({ name, role, personality, avatar_url: avatarUrl });
      setIdentityMsg(res.message || "Saved!");
      setTimeout(() => setIdentityMsg(""), 3000);
    } catch {
      setIdentityMsg("Failed to save");
    }
  }

  async function saveLLM() {
    try {
      const res = await updateLLM({
        provider,
        model,
        temperature,
        max_tokens_per_action: maxTokens,
        daily_cost_budget_usd: dailyBudget,
      });
      setLlmMsg(res.message || "Saved!");
      setTimeout(() => setLlmMsg(""), 3000);
    } catch {
      setLlmMsg("Failed to save");
    }
  }

  if (loading) {
    return <p className="text-muted-foreground">Loading...</p>;
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <h2 className="text-2xl font-bold">Settings</h2>

      <Card>
        <CardHeader>
          <CardTitle>Identity</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input id="name" value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="role">Role</Label>
              <Input id="role" value={role} onChange={(e) => setRole(e.target.value)} />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="personality">Personality / System Prompt</Label>
            <Textarea
              id="personality"
              value={personality}
              onChange={(e) => setPersonality(e.target.value)}
              rows={8}
              placeholder="Define the agent's personality, company info, rules..."
            />
            <p className="text-xs text-muted-foreground">
              Put company info here so the agent always knows about your org.
            </p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="avatar">Avatar URL</Label>
            <Input id="avatar" value={avatarUrl} onChange={(e) => setAvatarUrl(e.target.value)} placeholder="https://..." />
          </div>
          <div className="flex items-center gap-2">
            <Button onClick={saveIdentity}>Save Identity</Button>
            {identityMsg && <Badge variant="secondary">{identityMsg}</Badge>}
          </div>
        </CardContent>
      </Card>

      <Separator />

      <Card>
        <CardHeader>
          <CardTitle>LLM Configuration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="provider">Provider</Label>
              <Input id="provider" value={provider} onChange={(e) => setProvider(e.target.value)} placeholder="minimax / claude / openai / ollama" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="model">Model</Label>
              <Input id="model" value={model} onChange={(e) => setModel(e.target.value)} />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="temp">Temperature</Label>
              <Input id="temp" type="number" step={0.1} min={0} max={2} value={temperature} onChange={(e) => setTemperature(Number(e.target.value))} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="tokens">Max Tokens</Label>
              <Input id="tokens" type="number" value={maxTokens} onChange={(e) => setMaxTokens(Number(e.target.value))} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="budget">Daily Budget ($)</Label>
              <Input id="budget" type="number" step={1} value={dailyBudget} onChange={(e) => setDailyBudget(Number(e.target.value))} />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button onClick={saveLLM}>Save LLM Config</Button>
            {llmMsg && <Badge variant="secondary">{llmMsg}</Badge>}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
