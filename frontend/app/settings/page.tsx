"use client";
import {useEffect,useState} from "react"; import {api} from "@/lib/api";

type LLMConfig={enabled:boolean;provider:string;base_url:string;model:string;api_key_configured:boolean;api_key?:string};
type ServerConfig={enabled:boolean;sendkey_configured:boolean;api_base:string};
const providers=[
  {value:"deepseek",label:"DeepSeek",base_url:"https://api.deepseek.com",model:"deepseek-chat"},
  {value:"qwen",label:"Qwen / 通义千问",base_url:"https://dashscope.aliyuncs.com/compatible-mode/v1",model:"qwen-plus"},
  {value:"kimi",label:"Kimi / Moonshot",base_url:"https://api.moonshot.ai/v1",model:"kimi-latest"},
  {value:"siliconflow",label:"SiliconFlow",base_url:"https://api.siliconflow.cn/v1",model:"deepseek-ai/DeepSeek-V3"},
  {value:"custom",label:"Custom OpenAI Compatible",base_url:"",model:""},
];

export default function Settings(){
  const [form,setForm]=useState<LLMConfig>({enabled:false,provider:"deepseek",base_url:"",model:"",api_key_configured:false,api_key:""}); const [server,setServer]=useState<ServerConfig|null>(null); const [message,setMessage]=useState(""); const [busy,setBusy]=useState(false);
  useEffect(()=>{api<LLMConfig>("/api/settings/llm").then(x=>setForm({...x,api_key:""})); api<ServerConfig>("/api/settings/serverchan").then(setServer)},[]);
  function providerChanged(value:string){const item=providers.find(x=>x.value===value)!; setForm({...form,provider:value,base_url:item.base_url,model:item.model});}
  async function save(){setBusy(true);setMessage("");try{const saved=await api<LLMConfig>("/api/settings/llm",{method:"POST",body:JSON.stringify({enabled:form.enabled,provider:form.provider,base_url:form.base_url,model:form.model,api_key:form.api_key||null})});setForm({...saved,api_key:""});setMessage("模型配置已保存。");}catch(e){setMessage((e as Error).message)}finally{setBusy(false)}}
  async function testLLM(){setBusy(true);setMessage("正在测试模型…");try{const result=await api<{success:boolean;error:string;output:string}>("/api/settings/test-llm",{method:"POST"});setMessage(result.success?`测试成功：${result.output}`:`测试失败：${result.error}`)}catch(e){setMessage((e as Error).message)}finally{setBusy(false)}}
  async function testPush(){setBusy(true);setMessage("正在测试推送…");try{await api("/api/settings/test-push",{method:"POST"});setMessage("测试推送成功。")}catch(e){setMessage((e as Error).message)}finally{setBusy(false)}}
  return <div className="space-y-6"><h1 className="text-2xl font-bold">设置</h1>{message&&<div className="rounded-lg bg-blue-50 p-3 text-sm text-blue-800">{message}</div>}
    <section className="card space-y-4"><div><h2 className="font-semibold">模型调用设置</h2><p className="text-sm text-slate-500">关闭或调用失败时，周报自动使用模板生成。</p></div>
      <label className="flex items-center gap-3"><input type="checkbox" checked={form.enabled} onChange={e=>setForm({...form,enabled:e.target.checked})}/><span className="text-sm">启用大模型</span></label>
      <div><label className="label">模型提供商</label><select className="input" value={form.provider} onChange={e=>providerChanged(e.target.value)}>{providers.map(p=><option value={p.value} key={p.value}>{p.label}</option>)}</select></div>
      <div><label className="label">API Base URL</label><input className="input" value={form.base_url} onChange={e=>setForm({...form,base_url:e.target.value})}/></div>
      <div><label className="label">Model</label><input className="input" value={form.model} onChange={e=>setForm({...form,model:e.target.value})}/></div>
      <div><label className="label">API Key</label><input type="password" className="input" value={form.api_key} placeholder={form.api_key_configured?"已配置；留空则保留原 Key":"请输入 API Key"} onChange={e=>setForm({...form,api_key:e.target.value})}/></div>
      <div className="flex gap-3"><button disabled={busy} className="btn" onClick={save}>保存配置</button><button disabled={busy} className="btn bg-slate-700 hover:bg-slate-800" onClick={testLLM}>测试模型</button></div>
    </section>
    <section className="card"><h2 className="font-semibold">Server 酱</h2><div className="my-3 space-y-1 text-sm text-slate-600"><p>状态：{server?.enabled?"已启用":"未启用"}</p><p>SendKey：{server?.sendkey_configured?"已配置":"未配置"}</p><p>API：{server?.api_base||"-"}</p></div><button disabled={busy||!server?.sendkey_configured} className="btn" onClick={testPush}>测试微信推送</button></section>
    <section className="card"><h2 className="font-semibold">定时任务</h2><p className="mt-2 text-sm text-slate-600">默认每周一 08:30（Asia/Shanghai）执行。</p></section>
  </div>
}
