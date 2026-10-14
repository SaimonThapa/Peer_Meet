"use client";

import { useEffect, useState } from "react";
import { PostsApi } from "@/api/endpoints";
import { EmptyState, ErrorMessage, SkeletonCard } from "@/components/Status";
import { PostCard } from "./PostCard";
import { useAuth } from "@/context/AuthContext";

export function Feed() {
  const [posts, setPosts] = useState([]);
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState("");
  const { user } = useAuth();

  async function load() {
    setStatus("loading");
    setError("");
    try {
      const data = await PostsApi.list();
      setPosts(data.posts);
      setStatus("success");
    } catch (err) {
      setError(err.message);
      setStatus("error");
    }
  }

  useEffect(() => { load(); }, []);

  if (status === "loading") return <div className="mx-auto max-w-[var(--feed-max)] space-y-5"><SkeletonCard /><SkeletonCard /></div>;
  if (status === "error") return <div className="mx-auto max-w-[var(--feed-max)]"><ErrorMessage>{error}</ErrorMessage></div>;
  if (!posts.length) return <div className="mx-auto max-w-[var(--feed-max)]"><EmptyState title="No posts yet">Publish the first synthetic image post for the lab.</EmptyState></div>;

  return (
    <div className="mx-auto max-w-[var(--feed-max)] space-y-5">
      {posts.map((post) => <PostCard key={post.id} post={post} currentUser={user} onChanged={(updated) => setPosts((items) => updated ? items.map((item) => item.id === updated.id ? updated : item) : items.filter((item) => item.id !== post.id))} />)}
    </div>
  );
}
