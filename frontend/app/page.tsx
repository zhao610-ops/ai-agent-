"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

type Report = {week:string; title:string; summary:string; generation_mode:string};
type Trend = {keyword:string; frequency:number; trend_score:number};
type Repo = {full_name:string; stars:number; stars_growth_7d:number; url:string};

export default function Dashboard() {
  const [report, setReport] = useState<Report|null>(null); const [trends,setTrends]=useState<Trend[]>([]); const [repos,setRepos]=useState<Repo[]>([]); const [message,setMessage]=useState("");
  async function load(){ const reports=await api<Report[]>("/api/reports"); setReport(reports[0]||null); setTrends(await api<Trend[]>("/api/keywords/trends")); setRepos(await api<Repo[]>("/api/github/hot")); }
  useEffect(()=>{load().catch(e=>setMessage(e.message));},[]);
  async function run(){setMessage("任务提交中…"); await api("/api/agents/run-weekly",{method:"POST"}); setMessage("任务已提交，请稍后刷新。");}
  return <div className="space-y-6"><div className="flex items-center justify-between"><div><h1 className="text-2xl font-bold">Dashboard</h1><p className="text-slate-500">AI Agent 行业每周情报概览</p></div><button className="btn" onClick={run}>手动生成周报</button></div>{message&&<p className="text-sm text-blue-700">{message}</p>}
    <section className="card"><div className="mb-2 flex justify-between"><h2 className="font-semibold">本周核心结论</h2>{report&&<span className="text-xs text-slate-500">{report.generation_mode === "llm" ? "大模型生成" : "模板生成"}</span>}</div><p className="text-slate-700">{report?.summary||"暂无周报，请先运行任务。"}</p>{report&&<Link className="mt-3 inline-block text-sm text-blue-600" href={`/reports/${report.week}`}>查看完整周报 →</Link>}</section>
    <div className="grid gap-6 lg:grid-cols-2"><section className="card"><h2 className="mb-4 font-semibold">本周热词 TOP10</h2><div className="flex flex-wrap gap-2">{trends.slice(0,10).map(x=><span key={x.keyword} className="rounded-full bg-blue-50 px-3 py-1 text-sm text-blue-700">{x.keyword} · {x.frequency}</span>)}</div></section><section className="card"><h2 className="mb-4 font-semibold">GitHub 增长 TOP10</h2><ol className="space-y-2">{repos.slice(0,10).map((x,i)=><li key={x.full_name} className="flex justify-between text-sm"><a href={x.url} target="_blank" className="text-blue-700">{i+1}. {x.full_name}</a><span>+{x.stars_growth_7d}</span></li>)}</ol></section></div>
  </div>;
}
