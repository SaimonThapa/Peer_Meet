"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/Button";
import { ErrorMessage } from "@/components/Status";
import { useAuth } from "@/context/AuthContext";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({ username: "", displayName: "", email: "", password: "" });
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault();
    setStatus("loading");
    setError("");
    try {
      await register(form);
      router.push("/");
    } catch (err) {
      setError(err.message);
      setStatus("error");
    }
  }

  return (
    <main className="mx-auto max-w-md rounded-panel border border-border bg-surface p-6 shadow-soft">
      <h1 className="text-2xl font-black">Create account</h1>
      <form onSubmit={submit} className="mt-6 space-y-4">
        <label className="block text-sm font-semibold">Username<input required className="mt-1 w-full rounded-ui border-border" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} /></label>
        <label className="block text-sm font-semibold">Display name<input className="mt-1 w-full rounded-ui border-border" value={form.displayName} onChange={(e) => setForm({ ...form, displayName: e.target.value })} /></label>
        <label className="block text-sm font-semibold">Email<input className="mt-1 w-full rounded-ui border-border" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>
        <label className="block text-sm font-semibold">Password<input required minLength={8} className="mt-1 w-full rounded-ui border-border" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>
        <ErrorMessage>{error}</ErrorMessage>
        <Button disabled={status === "loading"} className="w-full">{status === "loading" ? "Creating..." : "Create account"}</Button>
      </form>
    </main>
  );
}
