interface TencentCaptchaResult {
  ret: number;
  ticket: string;
  randstr: string;
}

interface Window {
  TencentCaptcha?: new (
    appId: string,
    callback: (result: TencentCaptchaResult) => void,
  ) => { show: () => void };
}
