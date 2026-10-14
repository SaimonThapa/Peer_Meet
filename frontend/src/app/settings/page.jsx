"use client";

import { useState } from "react";
import { ProfilesApi } from "@/api/endpoints";
import { Button } from "@/components/Button";
import { ErrorMessage } from "@/components/Status";
import { useAuth } from "@/context/AuthContext";

export default function SettingsPage() {
  const { user, refreshCurrentUser, logout } = useAuth();
  const [form, setForm] = useState({ displayName: user?.displayName || "", bio: user?.bio || "" });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      await ProfilesApi.update(user.id, form);
      await refreshCurrentUser();
      setMessage("Profile updated.");
    } catch (err) {
      setError(err.message);
    }
  }

  if (!user) return <main className="mx-auto max-w-lg"><ErrorMessage>Please sign in to edit settings.</ErrorMessage></main>;

  return (
    <main className="mx-auto max-w-lg rounded-panel border border-border bg-surface p-6 shadow-soft">
      <h1 className="text-2xl font-black">Profile settings</h1>
      <form onSubmit={submit} className="mt-6 space-y-4">
        <label className="block text-sm font-semibold">Display name<input className="mt-1 w-full rounded-ui border-border" value={form.displayName} onChange={(e) => setForm({ ...form, displayName: e.target.value })} /></label>
        <label className="block text-sm font-semibold">Bio<textarea className="mt-1 w-full rounded-ui border-border" rows={4} value={form.bio} onChange={(e) => setForm({ ...form, bio: e.target.value })} /></label>
        <ErrorMessage>{error}</ErrorMessage>
        {message && <p className="text-sm font-semibold text-primary">{message}</p>}
        <div className="flex gap-3"><Button>Save</Button><Button type="button" variant="ghost" className="border border-border" onClick={logout}>Log out</Button></div>
      </form>
    </main>
  );
}
