"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { PostsApi } from "@/api/endpoints";
import { PostCard } from "@/features/posts/PostCard";
import { useAuth } from "@/context/AuthContext";
import { ErrorMessage, SkeletonCard } from "@/components/Status";

export default function PostDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const [post, setPost] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    PostsApi.get(id).then((data) => setPost(data.post)).catch((err) => setError(err.message));
  }, [id]);

  if (error) return <main className="mx-auto max-w-[var(--feed-max)]"><ErrorMessage>{error}</ErrorMessage></main>;
  if (!post) return <main className="mx-auto max-w-[var(--feed-max)]"><SkeletonCard /></main>;
  return <main className="mx-auto max-w-[var(--feed-max)]"><PostCard post={post} currentUser={user} detail onChanged={(updated) => setPost(updated || post)} /></main>;
}
