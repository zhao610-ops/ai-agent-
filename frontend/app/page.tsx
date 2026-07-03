"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

type Report = {week:string; title:string; summary:string; generation_mode:string; pushed_at:string|null};
type Trend = {keyword:string; frequency:number; trend_score:number};
type Repo = {full_name:string; stars:number; stars_growth_7d:number; url:string};

export default function Dashboard() {
  const [report, setReport] = useState<Report|null>(null); const [reports,setReports]=useState<Report[]>([]); const [selectedWeek,setSelectedWeek]=useState(""); const [trends,setTrends]=useState<Trend[]>([]); const [repos,setRepos]=useState<Repo[]>([]); const [message,setMessage]=useState(""); const [pushing,setPushing]=useState(false);
  async function load(){ const reportRows=await api<Report[]>("/api/reports"); setReports(reportRows); setReport(reportRows[0]||null); setSelectedWeek(current=>current||reportRows[0]?.week||""); setTrends(await api<Trend[]>("/api/keywords/trends")); setRepos(await api<Repo[]>("/api/github/hot")); }
  useEffect(()=>{load().catch(e=>setMessage(e.message));},[]);
  async function run(){setMessage("任务提交中…"); await api("/api/agents/run-weekly",{method:"POST"}); setMessage("任务已提交，请稍后刷新。");}
  async function pushReport(){
    // 前端先提示已推送状态，后端仍会再次校验，防止绕过页面重复发送。
    const selected=reports.find(item=>item.week===selectedWeek);
    if(selected?.pushed_at){window.alert("该周报已经推送过，不能重复推送");return;}
    setPushing(true);
    try{const result=await api<{message:string}>(`/api/reports/${selectedWeek}/push`,{method:"POST"});window.alert(result.message);await load();}
    catch(error){window.alert(error instanceof Error?error.message:"微信推送失败");}
    finally{setPushing(false);}
  }
  return <div className="space-y-6"><div className="flex flex-wrap items-center justify-between gap-4"><div><h1 className="text-2xl font-bold">Dashboard</h1><p className="text-slate-500">AI Agent 行业每周情报概览</p></div><div className="flex flex-wrap items-center gap-2"><button className="btn" onClick={run}>手动生成周报</button><select className="input w-auto min-w-36" value={selectedWeek} onChange={event=>setSelectedWeek(event.target.value)} disabled={!reports.length||pushing} aria-label="选择要推送的周报"><option value="" disabled>选择周报</option>{reports.map(item=><option key={item.week} value={item.week}>{item.week}{item.pushed_at?"（已推送）":""}</option>)}</select><button className="btn" onClick={pushReport} disabled={!selectedWeek||pushing}>{pushing?"推送中…":"推送到微信"}</button></div></div>{message&&<p className="text-sm text-blue-700">{message}</p>}
    <section className="card"><div className="mb-2 flex justify-between"><h2 className="font-semibold">本周核心结论</h2>{report&&<span className="text-xs text-slate-500">{report.generation_mode === "llm" ? "大模型生成" : "模板生成"}</span>}</div><p className="text-slate-700">{report?.summary||"暂无周报，请先运行任务。"}</p>{report&&<Link className="mt-3 inline-block text-sm text-blue-600" href={`/reports/${report.week}`}>查看完整周报 →</Link>}</section>
    <div className="grid gap-6 lg:grid-cols-2"><section className="card"><h2 className="mb-4 font-semibold">本周热词 TOP10</h2><div className="flex flex-wrap gap-2">{trends.slice(0,10).map(x=><span key={x.keyword} className="rounded-full bg-blue-50 px-3 py-1 text-sm text-blue-700">{x.keyword} · {x.frequency}</span>)}</div></section><section className="card"><h2 className="mb-4 font-semibold">GitHub 增长 TOP10</h2><ol className="space-y-2">{repos.slice(0,10).map((x,i)=><li key={x.full_name} className="flex justify-between text-sm"><a href={x.url} target="_blank" className="text-blue-700">{i+1}. {x.full_name}</a><span>+{x.stars_growth_7d}</span></li>)}</ol></section></div>
  </div>;
}
