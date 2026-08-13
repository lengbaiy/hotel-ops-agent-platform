export type CaptchaChallenge = {
  provider: "local_puzzle" | "tencent";
  captcha_id: string;
  track_length?: number;
  canvas_width?: number;
  canvas_height?: number;
  puzzle_offset?: number;
  app_id?: string;
  expires_in: number;
};

export type UserProfile = {
  username: string;
  display_name: string;
  tenant_id: string;
  property_ids: string[];
  roles: string[];
};

export type LoginSession = {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  user: UserProfile;
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`/api/v2/auth${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(payload?.detail ?? `认证请求失败：${response.status}`);
  }
  return response.status === 204 ? (undefined as T) : ((await response.json()) as T);
}

export function requestCaptcha() {
  return request<CaptchaChallenge>("/captcha", { method: "POST" });
}

export function login(payload: {
  username: string;
  password: string;
  captcha_id: string;
  slider_position?: number;
  captcha_ticket?: string;
  captcha_randstr?: string;
}) {
  return request<LoginSession>("/login", { method: "POST", body: JSON.stringify(payload) });
}

export function logout(token: string) {
  return request<void>("/logout", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
  });
}
