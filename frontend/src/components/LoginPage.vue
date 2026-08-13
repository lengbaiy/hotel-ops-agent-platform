<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { useAuth } from "../stores/auth";

const { challenge, authError, authenticating, refreshCaptcha, signIn } = useAuth();
const username = ref("ops-admin");
const password = ref("HotelOps@2026");
const sliderPosition = ref(0);
const isCaptchaReady = computed(() => Boolean(challenge.value));

onMounted(refreshCaptcha);

async function submit() {
  await signIn(username.value, password.value, sliderPosition.value).catch(() => undefined);
}
</script>

<template>
  <main class="login-page">
    <section class="login-hero">
      <div class="hero-brand"><span>H</span> Hotel Ops</div>
      <p class="eyebrow">SECURE OPERATIONS PLATFORM</p>
      <h1>酒店智能运营<br />Agent 平台</h1>
      <p class="hero-copy">
        统一管理经营任务、策略审批与受控执行。每一次决策均可追踪、可校验、可回读。
      </p>
      <div class="security-points">
        <span>✓ 身份认证</span><span>✓ 权限校验</span><span>✓ 审批留痕</span>
      </div>
    </section>

    <section class="login-panel">
      <form class="login-card" @submit.prevent="submit">
        <p class="eyebrow">WELCOME BACK</p>
        <h2>登录运营平台</h2>
        <p class="hint">请输入已分配的账号信息完成身份验证。</p>
        <label
          >账号<input
            v-model.trim="username"
            autocomplete="username"
            placeholder="请输入账号"
            required
        /></label>
        <label
          >密码<input
            v-model="password"
            type="password"
            autocomplete="current-password"
            placeholder="请输入密码"
            required
        /></label>
        <div class="captcha-block">
          <div class="captcha-title">
            <b>安全验证</b><button type="button" @click="refreshCaptcha">刷新</button>
          </div>
          <p>拖动滑块至缺口处，完成登录校验</p>
          <div class="captcha-scene" :class="{ ready: isCaptchaReady }">
            <span class="captcha-pattern"></span
            ><i :style="{ left: `${challenge?.target_position ?? 0}%` }"></i>
          </div>
          <input
            v-model.number="sliderPosition"
            class="slider"
            type="range"
            min="0"
            max="100"
            :disabled="!isCaptchaReady || authenticating"
            aria-label="登录滑块验证"
          />
          <div class="slider-label">
            {{ sliderPosition ? `当前验证位置：${sliderPosition}%` : "请拖动滑块完成验证" }}
          </div>
        </div>
        <p v-if="authError" class="login-error">{{ authError }}</p>
        <button class="login-button" :disabled="!isCaptchaReady || authenticating">
          {{ authenticating ? "身份校验中…" : "安全登录" }}
        </button>
        <p class="demo-note">本地演示账号：`ops-admin` / `HotelOps@2026`</p>
      </form>
    </section>
  </main>
</template>

<style scoped>
.login-page {
  display: grid;
  min-height: 100vh;
  grid-template-columns: 1.05fr 0.95fr;
  background: #f6f8fc;
  color: #172744;
}
.login-hero {
  display: flex;
  min-height: 100vh;
  flex-direction: column;
  justify-content: center;
  padding: 10vw;
  color: #fff;
  background: radial-gradient(circle at 76% 18%, #3e87ec 0, #173c83 34%, #0d1f43 76%);
}
.hero-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 92px;
  font-size: 23px;
  font-weight: 800;
}
.hero-brand span {
  display: grid;
  width: 35px;
  height: 35px;
  color: #123464;
  background: #50d4c5;
  border-radius: 10px;
  place-items: center;
}
.eyebrow {
  margin: 0 0 10px;
  color: #3987ef;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 1.8px;
}
.login-hero .eyebrow {
  color: #7ac6ff;
}
.login-hero h1 {
  margin: 0;
  font-size: 42px;
  line-height: 1.23;
}
.hero-copy {
  max-width: 485px;
  margin: 22px 0 28px;
  color: #bdcff1;
  font-size: 15px;
  line-height: 1.8;
}
.security-points {
  display: flex;
  gap: 20px;
  color: #7ce1d7;
  font-size: 13px;
  font-weight: 700;
}
.login-panel {
  display: grid;
  padding: 32px;
  place-items: center;
}
.login-card {
  width: min(390px, 100%);
}
.login-card h2 {
  margin: 0;
  font-size: 29px;
}
.hint {
  margin: 10px 0 28px;
  color: #76849a;
  font-size: 13px;
}
.login-card label {
  display: grid;
  gap: 8px;
  margin: 15px 0;
  color: #42516a;
  font-size: 13px;
  font-weight: 700;
}
.login-card input {
  box-sizing: border-box;
  width: 100%;
  padding: 12px;
  color: #1c2d49;
  background: #fff;
  border: 1px solid #dce4ef;
  border-radius: 8px;
  outline: none;
}
.login-card input:focus {
  border-color: #3177e8;
  box-shadow: 0 0 0 3px #3177e819;
}
.captcha-block {
  padding: 14px;
  margin: 20px 0;
  background: #f7f9fd;
  border: 1px solid #e5ebf4;
  border-radius: 10px;
}
.captcha-title {
  display: flex;
  justify-content: space-between;
  color: #35445e;
  font-size: 13px;
}
.captcha-title button {
  padding: 0;
  color: #2871e5;
  background: transparent;
  border: 0;
}
.captcha-block p,
.slider-label {
  margin: 7px 0;
  color: #8491a5;
  font-size: 11px;
}
.captcha-scene {
  position: relative;
  height: 60px;
  overflow: hidden;
  background: linear-gradient(135deg, #dde9fa, #eff5ff);
  border-radius: 7px;
}
.captcha-pattern {
  position: absolute;
  inset: 0;
  opacity: 0.55;
  background: repeating-linear-gradient(45deg, transparent 0 10px, #bfd3f4 10px 12px);
}
.captcha-scene i {
  position: absolute;
  top: 16px;
  width: 26px;
  height: 26px;
  border: 2px dashed #286fe2;
  border-radius: 6px;
  transform: translateX(-50%);
}
.slider {
  accent-color: #2e74e7;
}
.login-error {
  padding: 10px;
  color: #b73947;
  background: #fff0f1;
  border-radius: 7px;
  font-size: 12px;
}
.login-button {
  width: 100%;
  padding: 13px;
  color: #fff;
  background: #286fe2;
  border: 0;
  border-radius: 8px;
  font-weight: 800;
}
.login-button:disabled {
  opacity: 0.55;
}
.demo-note {
  margin: 16px 0 0;
  color: #8995a8;
  font-size: 11px;
  text-align: center;
}
@media (max-width: 800px) {
  .login-page {
    grid-template-columns: 1fr;
  }
  .login-hero {
    min-height: auto;
    padding: 45px 32px;
  }
  .hero-brand {
    margin-bottom: 45px;
  }
  .login-hero h1 {
    font-size: 31px;
  }
  .login-panel {
    min-height: 620px;
  }
}
</style>
