"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { useEffect, useState } from "react";
import { SearchApi } from "@/api/endpoints";
import { EmptyState, ErrorMessage } from "@/components/Status";

export default function SearchPage() {
  return (
    <Suspense fallback={<main className="mx-auto max-w-3xl text-muted">Loading search...</main>}>
      <SearchBody />
    </Suspense>
  );
}

function SearchBody() {
  const params = useSearchParams();
  const q = params.get("q") || "";
  const [query, setQuery] = useState(q);
  const [results, setResults] = useState({ users: [], posts: [] });
  const [error, setError] = useState("");

  useEffect(() => {
    setQuery(q);
    if (!q) return;
    SearchApi.run(q).then((data) => setResults(data.results)).catch((err) => setError(err.message));
  }, [q]);

  return (
    <main className="mx-auto max-w-3xl space-y-6">
      <form className="rounded-panel border border-border bg-surface p-4 shadow-soft">
        <label className="block text-sm font-semibold">Search users and captions<input name="q" className="mt-2 w-full rounded-ui border-border" value={query} onChange={(e) => setQuery(e.target.value)} /></label>
      </form>
      {q && (
        <h1 className="text-2xl font-black">
          Results for {/* LAB-VULN: V-02B - approved reflected XSS sink; see docs/VULNERABILITIES.md. */}
          <span dangerouslySetInnerHTML={{ __html: q }} />
        </h1>
      )}
      <ErrorMessage>{error}</ErrorMessage>
      {!q ? <EmptyState title="Search the lab">Find seeded users or words in synthetic captions.</EmptyState> : (
        <div className="grid gap-5 md:grid-cols-2">
          <section className="rounded-panel border border-border bg-surface p-4">
            <h2 className="font-bold">Users</h2>
            <div className="mt-3 space-y-2">
              {results.users.length ? results.users.map((user) => <Link className="block rounded-ui bg-elevated px-3 py-2 hover:text-primary" key={user.id} href={`/profile/${user.username}`}>@{user.username} <span className="text-muted">{user.displayName}</span></Link>) : <p className="text-sm text-muted">No users found.</p>}
            </div>
          </section>
          <section className="rounded-panel border border-border bg-surface p-4">
            <h2 className="font-bold">Posts</h2>
            <div className="mt-3 space-y-2">
              {results.posts.length ? results.posts.map((post) => <Link className="block rounded-ui bg-elevated px-3 py-2 hover:text-primary" key={post.id} href={`/posts/${post.id}`}>{post.caption || "Untitled post"} <span className="text-muted">by @{post.author.username}</span></Link>) : <p className="text-sm text-muted">No posts found.</p>}
            </div>
          </section>
        </div>
      )}
    </main>
  );
}
