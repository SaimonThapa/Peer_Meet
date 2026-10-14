"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/Button";
import { ErrorMessage } from "@/components/Status";
import { useAuth } from "@/context/AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({ username: "alice", password: "Password123!" });
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault();
    setStatus("loading");
    setError("");
    try {
      await login(form);
      router.push("/");
    } catch (err) {
      setError(err.message);
      setStatus("error");
    }
  }

  return (
    <main className="mx-auto max-w-md rounded-panel border border-border bg-surface p-6 shadow-soft">
      <h1 className="text-2xl font-black">Sign in</h1>
      <p className="mt-2 text-sm text-muted">Use seeded accounts like alice, bob, casey, or admin.</p>
      <form onSubmit={submit} className="mt-6 space-y-4">
        <label className="block text-sm font-semibold">Username<input className="mt-1 w-full rounded-ui border-border" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} /></label>
        <label className="block text-sm font-semibold">Password<input className="mt-1 w-full rounded-ui border-border" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>
        <ErrorMessage>{error}</ErrorMessage>
        <Button disabled={status === "loading"} className="w-full">{status === "loading" ? "Signing in..." : "Sign in"}</Button>
      </form>
      <p className="mt-4 text-sm text-muted">New here? <Link className="font-semibold text-primary" href="/register">Create an account</Link></p>
    </main>
  );
}
