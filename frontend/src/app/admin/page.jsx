"use client";

import { useEffect, useState } from "react";
import { AdminApi } from "@/api/endpoints";
import { Button } from "@/components/Button";
import { ErrorMessage } from "@/components/Status";

export default function AdminPage() {
  const [users, setUsers] = useState([]);
  const [posts, setPosts] = useState([]);
  const [error, setError] = useState("");

  async function load() {
    try {
      const [userData, postData] = await Promise.all([AdminApi.users(), AdminApi.posts()]);
      setUsers(userData.users);
      setPosts(postData.posts);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => { load(); }, []);

  async function remove(id) {
    if (!confirm("Remove this demo post?")) return;
    await AdminApi.deletePost(id);
    load();
  }

  return (
    <main className="mx-auto max-w-5xl space-y-6">
      <h1 className="text-2xl font-black">Admin dashboard</h1>
      <ErrorMessage>{error}</ErrorMessage>
      <section className="rounded-panel border border-border bg-surface p-4">
        <h2 className="font-bold">Users</h2>
        <div className="mt-3 overflow-x-auto">
          <table className="w-full text-left text-sm"><tbody>{users.map((u) => <tr key={u.id} className="border-t border-border"><td className="py-2">@{u.username}</td><td>{u.display_name}</td><td>{u.role}</td></tr>)}</tbody></table>
        </div>
      </section>
      <section className="rounded-panel border border-border bg-surface p-4">
        <h2 className="font-bold">Posts</h2>
        <div className="mt-3 space-y-2">{posts.map((post) => <div key={post.id} className="flex items-center justify-between gap-3 rounded-ui bg-elevated p-3"><span className="text-sm">@{post.username}: {post.caption || "Untitled"}</span><Button variant="danger" onClick={() => remove(post.id)}>Delete</Button></div>)}</div>
      </section>
    </main>
  );
}
