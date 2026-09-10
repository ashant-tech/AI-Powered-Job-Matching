import type { AuthResponse, User } from "@/types/User";
import { request, setToken } from "./apiClient";

export async function register(data: { email: string; full_name: string; password: string; phone?: string }) {
  const res = await request<AuthResponse>("/api/auth/register", { method: "POST", body: JSON.stringify(data) });
  setToken(res.access_token);
  return res;
}

export async function login(email: string, password: string) {
  const res = await request<AuthResponse>("/api/auth/login/json", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setToken(res.access_token);
  return res;
}

export function logout() {
  setToken(null);
}

export function getMe() {
  return request<User>("/api/users/me");
}

export function updateMe(data: { full_name?: string; phone?: string }) {
  return request<User>("/api/users/me", { method: "PATCH", body: JSON.stringify(data) });
}
