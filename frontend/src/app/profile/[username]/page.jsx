"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ProfilesApi } from "@/api/endpoints";
import { Button } from "@/components/Button";
import { EmptyState, ErrorMessage } from "@/components/Status";
import { mediaUrl } from "@/lib/config";
import { useAuth } from "@/context/AuthContext";

export default function ProfilePage() {
  const { username } = useParams();
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState("");

  async function load() {
    try {
      const data = await ProfilesApi.get(username);
      setProfile(data.profile);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => { load(); }, [username]);

  async function toggleFollow() {
    if (!profile) return;
    if (profile.isFollowing) await ProfilesApi.unfollow(profile.id);
    else await ProfilesApi.follow(profile.id);
    load();
  }

  if (error) return <main className="mx-auto max-w-4xl"><ErrorMessage>{error}</ErrorMessage></main>;
  if (!profile) return <main className="mx-auto max-w-4xl text-muted">Loading profile...</main>;

  return (
    <main className="mx-auto max-w-4xl space-y-6">
      <section className="rounded-panel border border-border bg-surface p-5 shadow-soft">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
          <div className="grid h-20 w-20 place-items-center rounded-full bg-elevated text-2xl font-black text-primary">{profile.displayName[0]}</div>
          <div className="min-w-0 flex-1">
            <h1 className="text-2xl font-black">{profile.displayName}</h1>
            <p className="text-muted">@{profile.username}</p>
            <p className="mt-2">{profile.bio}</p>
          </div>
          {user?.id === profile.id ? <Link className="font-semibold text-primary" href="/settings">Edit profile</Link> : user ? <Button onClick={toggleFollow}>{profile.isFollowing ? "Unfollow" : "Follow"}</Button> : null}
        </div>
        <dl className="mt-5 grid grid-cols-3 gap-3 text-center">
          <div><dt className="text-sm text-muted">Posts</dt><dd className="font-black">{profile.postCount}</dd></div>
          <div><dt className="text-sm text-muted">Followers</dt><dd className="font-black">{profile.followers}</dd></div>
          <div><dt className="text-sm text-muted">Following</dt><dd className="font-black">{profile.following}</dd></div>
        </dl>
      </section>
      {profile.posts.length ? (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {profile.posts.map((post) => <Link key={post.id} href={`/posts/${post.id}`}><img className="aspect-square w-full rounded-ui object-cover" src={mediaUrl(post.imageUrl)} alt={post.caption || `Post by ${profile.displayName}`} /></Link>)}
        </div>
      ) : <EmptyState title="No posts yet">This profile has not published any posts.</EmptyState>}
    </main>
  );
}
