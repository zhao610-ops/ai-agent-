import Link from "next/link";

const links = [["/", "Dashboard"], ["/reports", "周报"], ["/agents", "Agents"], ["/github", "GitHub"], ["/settings", "设置"]];

export function Nav() {
  return <header className="border-b bg-white"><div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4"><Link href="/" className="font-bold">AI Agent 微信周报助手</Link><nav className="flex gap-5 text-sm">{links.map(([href, label]) => <Link key={href} href={href} className="text-slate-600 hover:text-blue-600">{label}</Link>)}</nav></div></header>;
}
