import { apiFetch, jsonBody } from "./client";

export const AuthApi = {
  me: () => apiFetch("/auth/me", { skipRefresh: true }),
  login: (data) => apiFetch("/auth/login", { method: "POST", body: jsonBody(data), skipRefresh: true }),
  register: (data) => apiFetch("/auth/register", { method: "POST", body: jsonBody(data), skipRefresh: true }),
  logout: () => apiFetch("/auth/logout", { method: "POST", skipRefresh: true })
};

export const PostsApi = {
  list: () => apiFetch("/posts"),
  get: (id) => apiFetch(`/posts/${id}`),
  create: (formData) => apiFetch("/posts", { method: "POST", body: formData }),
  like: (id) => apiFetch(`/posts/${id}/likes`, { method: "POST" }),
  comment: (id, body) => apiFetch(`/posts/${id}/comments`, { method: "POST", body: jsonBody({ body }) }),
  delete: (id) => apiFetch(`/posts/${id}`, { method: "DELETE" })
};

export const ProfilesApi = {
  get: (username) => apiFetch(`/users/${username}`),
  update: (id, data) => apiFetch(`/users/${id}/profile`, { method: "PATCH", body: jsonBody(data) }),
  follow: (id) => apiFetch("/follows", { method: "POST", body: jsonBody({ followingId: id }) }),
  unfollow: (id) => apiFetch(`/follows/${id}`, { method: "DELETE" })
};

export const SearchApi = {
  run: (q) => apiFetch(`/search?q=${encodeURIComponent(q)}`)
};

export const AdminApi = {
  users: () => apiFetch("/admin/users"),
  posts: () => apiFetch("/admin/posts"),
  deletePost: (id) => apiFetch(`/admin/posts/${id}`, { method: "DELETE" })
};
