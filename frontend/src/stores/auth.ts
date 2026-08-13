import { computed, ref } from "vue";

import {
  login,
  logout,
  requestCaptcha,
  type CaptchaChallenge,
  type LoginSession,
} from "../api/auth";

const storageKey = "hotel-ops-session";
const session = ref<LoginSession | null>(readSession());
const challenge = ref<CaptchaChallenge | null>(null);
const authError = ref("");
const authenticating = ref(false);

function readSession(): LoginSession | null {
  const raw = sessionStorage.getItem(storageKey);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as LoginSession;
  } catch {
    sessionStorage.removeItem(storageKey);
    return null;
  }
}

export function getAccessToken() {
  return session.value?.access_token ?? "";
}

export function useAuth() {
  const isAuthenticated = computed(() => session.value !== null);

  async function refreshCaptcha() {
    authError.value = "";
    challenge.value = await requestCaptcha();
  }

  async function signIn(username: string, password: string, sliderPosition: number) {
    if (!challenge.value) await refreshCaptcha();
    authenticating.value = true;
    authError.value = "";
    try {
      const activeChallenge = challenge.value;
      if (!activeChallenge) throw new Error("滑块验证初始化失败");
      session.value = await login({
        username,
        password,
        captcha_id: activeChallenge.captcha_id,
        slider_position: sliderPosition,
      });
      sessionStorage.setItem(storageKey, JSON.stringify(session.value));
      challenge.value = null;
    } catch (error) {
      authError.value = error instanceof Error ? error.message : "登录失败";
      await refreshCaptcha();
      throw error;
    } finally {
      authenticating.value = false;
    }
  }

  async function signOut() {
    const token = getAccessToken();
    session.value = null;
    sessionStorage.removeItem(storageKey);
    if (token) await logout(token).catch(() => undefined);
  }

  return {
    session,
    challenge,
    authError,
    authenticating,
    isAuthenticated,
    refreshCaptcha,
    signIn,
    signOut,
  };
}
