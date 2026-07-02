import type { Metadata } from "next";
import "./globals.css";
import { Nav } from "@/components/Nav";

export const metadata: Metadata = { title: "AI Agent 微信周报助手", description: "AI Agent 行业周报与趋势监测" };
export default function RootLayout({ children }: Readonly<{children: React.ReactNode}>) {
  return <html lang="zh-CN"><body><Nav/><main className="mx-auto max-w-7xl px-6 py-8">{children}</main></body></html>;
}
