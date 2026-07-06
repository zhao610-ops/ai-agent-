"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type PublicSettings = { demo_mode:boolean; public_demo:boolean; allow_real_push:boolean; allow_real_llm:boolean };

export function DemoBanner() {
  const [visible, setVisible] = useState(false);
  // 横幅接口失败时静默隐藏，不影响其他页面正常加载。
  useEffect(() => { api<PublicSettings>("/api/settings").then(data => setVisible(data.public_demo)).catch(() => undefined); }, []);
  if (!visible) return null;
  return <div className="border-b border-amber-200 bg-amber-50 px-4 py-2 text-center text-xs text-amber-800">当前为在线演示环境，已关闭真实模型调用和微信推送。</div>;
}
