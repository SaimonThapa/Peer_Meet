"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/Button";
import { ErrorMessage } from "@/components/Status";
import { PostsApi } from "@/api/endpoints";
import { useAuth } from "@/context/AuthContext";

export default function UploadPage() {
  const { status } = useAuth();
  const router = useRouter();
  const [file, setFile] = useState(null);
  const [caption, setCaption] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event) {
    event.preventDefault();
    const form = new FormData();
    form.append("image", file);
    form.append("caption", caption);
    setBusy(true);
    setError("");
    try {
      await PostsApi.create(form);
      router.push("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  if (status === "unauthenticated") return <main className="mx-auto max-w-lg"><ErrorMessage>Please sign in before publishing a post.</ErrorMessage></main>;

  return (
    <main className="mx-auto max-w-xl rounded-panel border border-border bg-surface p-6 shadow-soft">
      <h1 className="text-2xl font-black">New post</h1>
      <form onSubmit={submit} className="mt-6 space-y-4">
        <label className="block text-sm font-semibold">Image file<input required className="mt-1 w-full rounded-ui border border-border p-3" type="file" onChange={(e) => setFile(e.target.files?.[0])} /></label>
        <label className="block text-sm font-semibold">Caption<textarea className="mt-1 w-full rounded-ui border-border" rows={4} value={caption} onChange={(e) => setCaption(e.target.value)} /></label>
        <ErrorMessage>{error}</ErrorMessage>
        <Button disabled={busy || !file}>{busy ? "Publishing..." : "Publish"}</Button>
      </form>
    </main>
  );
}
