"use client";

import Link from "next/link";
import { Heart, MessageCircle, Trash2 } from "lucide-react";
import { useState } from "react";
import { PostsApi } from "@/api/endpoints";
import { mediaUrl } from "@/lib/config";
import { Button } from "@/components/Button";

export function PostCard({ post, currentUser, onChanged, detail = false }) {
  const [busy, setBusy] = useState(false);
  const [draft, setDraft] = useState("");
  const [error, setError] = useState("");

  async function like() {
    setBusy(true);
    setError("");
    try {
      const data = await PostsApi.like(post.id);
      onChanged?.(data.post);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function comment() {
    if (!draft.trim()) return;
    setBusy(true);
    setError("");
    try {
      const data = await PostsApi.comment(post.id, draft);
      setDraft("");
      onChanged?.(data.post);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function remove() {
    if (!confirm("Delete this post?")) return;
    await PostsApi.delete(post.id);
    onChanged?.(null);
  }

  return (
    <article className="overflow-hidden rounded-panel border border-border bg-surface shadow-soft">
      <div className="flex items-center justify-between px-4 py-3">
        <Link href={`/profile/${post.author.username}`} className="font-semibold hover:text-primary">{post.author.displayName}</Link>
        <span className="text-xs text-muted">{new Date(post.createdAt).toLocaleString()}</span>
      </div>
      <Link href={`/posts/${post.id}`} className="block bg-elevated">
        <img className="aspect-square w-full object-cover" src={mediaUrl(post.imageUrl)} alt={`Post by ${post.author.displayName}`} />
      </Link>
      <div className="space-y-3 p-4">
        <div className="flex items-center gap-3">
          <button disabled={busy || !currentUser} onClick={like} className={`inline-flex min-h-11 items-center gap-2 rounded-ui px-3 font-semibold transition hover:bg-elevated disabled:opacity-50 ${post.likedByMe ? "text-danger" : ""}`}>
            <Heart size={20} fill={post.likedByMe ? "currentColor" : "none"} /> {post.likeCount}
          </button>
          <Link href={`/posts/${post.id}`} className="inline-flex min-h-11 items-center gap-2 rounded-ui px-3 text-sm font-semibold hover:bg-elevated">
            <MessageCircle size={20} /> {post.commentCount}
          </Link>
          {currentUser?.id === post.author.id && <button onClick={remove} className="ml-auto rounded-ui p-2 text-danger hover:bg-danger/10" aria-label="Delete post"><Trash2 size={18} /></button>}
        </div>
        {post.caption && <p><Link className="font-semibold" href={`/profile/${post.author.username}`}>@{post.author.username}</Link> {post.caption}</p>}
        {error && <p className="text-sm text-danger">{error}</p>}
        {detail && (
          <section className="space-y-3 border-t border-border pt-3">
            <h2 className="text-sm font-semibold">Comments</h2>
            {post.comments?.length ? post.comments.map((comment) => (
              <div key={comment.id} className="rounded-ui bg-elevated px-3 py-2 text-sm">
                <span className="font-semibold">@{comment.author.username} </span>
                <span>{comment.body}</span>
              </div>
            )) : <p className="text-sm text-muted">No comments yet.</p>}
            {currentUser && (
              <div className="flex gap-2">
                <input className="min-w-0 flex-1 rounded-ui border-border" value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Add a comment" />
                <Button disabled={busy || !draft.trim()} onClick={comment}>Post</Button>
              </div>
            )}
          </section>
        )}
      </div>
    </article>
  );
}
