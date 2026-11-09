import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import type { Badge } from "../types";
import { localAchievements, nextAchievement } from "../components/achievementData";
import AchievementGoal from "../components/AchievementGoal";
import "./BadgesPage.css";

export default function BadgesPage() {
 const [badges,setBadges]=useState<Badge[]>([]);const [local,setLocal]=useState<Badge[]>([]);
 const [loaded,setLoaded]=useState(false);const [error,setError]=useState(false);const [localError,setLocalError]=useState(false);
 const [localNotice,setLocalNotice]=useState('');
 const [filter,setFilter]=useState('全部');const [retry,setRetry]=useState(0);
 useEffect(()=>{let active=true;
  fetch('/api/badges').then(r=>{if(!r.ok)throw Error();return r.json();}).then(b=>{if(active){setBadges(b);setLoaded(true);setError(false);}}).catch(()=>{if(active)setError(true);});
  const refresh=()=>{let old='';try{old=localStorage.getItem('spark-quest:local-achievements:v1')||'';}catch{}return localAchievements(localStorage).then(b=>{if(active){setLocal(b);setLocalError(false);const fresh=b.filter(v=>v.unlocked&&!old.includes(v.code));if(fresh.length)setLocalNotice('本机新成就已收录：'+fresh.map(v=>v.name).join('、'));}}).catch(()=>{if(active)setLocalError(true);});};
  refresh();window.addEventListener('focus',refresh);window.addEventListener('storage',refresh);
  return ()=>{active=false;window.removeEventListener('focus',refresh);window.removeEventListener('storage',refresh);};
 },[retry]);
 const all=[...badges,...local];const groups=['起步','复习与修复','坚持','本机练习','章节旅程','特别收藏'];
 const group=(b:Badge)=>b.group||(b.tier==='journey'?'章节旅程':'特别收藏');
 const target=nextAchievement(badges);
 return <div className="container badges-page">
  <header className="badges-header"><Link to="/" className="back-link">← 返回首页</Link><p className="aw-eyebrow">每一次重新理解，都算数</p><h1 className="badges-title">把进步收集起来</h1><p className="badges-sub">{loaded?`永久成就 ${badges.filter(b=>b.unlocked).length} / ${badges.length}`:'正在读取成就…'} · 本机练习 {local.filter(b=>b.unlocked).length} / {local.length||4}</p></header>
  {error&&<div role="alert" className="card">暂时无法读取永久成就。<button onClick={()=>setRetry(v=>v+1)}>重新加载</button></div>}
  {localError&&<p role="status">本机记录暂时无法读取或保存，永久成就不受影响。恢复浏览器存储后可重新读取。</p>}
  {localNotice&&<p role="status" className="aw-local-notice">{localNotice}</p>}
  {target&&<AchievementGoal badge={target}/>}
  <nav className="aw-filters" aria-label="成就筛选">{['全部','已获得','待点亮'].map(f=><button key={f} aria-pressed={filter===f} onClick={()=>setFilter(f)}>{f}</button>)}</nav>
  {groups.map(g=>{const list=all.filter(b=>group(b)===g&&(filter==='全部'||(filter==='已获得'?b.unlocked:!b.unlocked))).sort((a,b)=>Number(b.unlocked)-Number(a.unlocked));return list.length>0&&<section key={g} className="badge-group"><h2 className="badge-group-title">{g}</h2><p className="badge-group-hint">{g==='本机练习'?'记录在当前浏览器；不代表正式掌握，清除本机数据会丢失。':'已获得的成就会保留。日期为成就收录日期，历史记录可能在升级时补发。'}</p><div className="badge-grid">{list.map(b=><BadgeCard key={b.code} badge={b}/>)}</div></section>})}
  {loaded&&all.filter(b=>filter==='已获得'?b.unlocked:filter==='待点亮'?!b.unlocked:true).length===0&&<p className="card">这一栏还没有成就。先完成一小步，再回来看看。</p>}
 </div>;
}
function BadgeCard({badge:b}:{badge:Badge}) {
 const secret=b.is_secret&&!b.unlocked;
 return <article className={`badge-card ${b.unlocked?'unlocked':'locked'} ${secret?'secret':''}`}>
  <div className="badge-card-img">{!secret&&b.image?<img src={b.image} alt="" loading="lazy"/>:<span className="badge-card-q">?</span>}</div>
  <div className="badge-card-name">{secret?'神秘徽章':b.name}</div><p className="badge-card-desc">{secret?'留一点惊喜，遇见时再揭晓':b.description}</p>
  {!secret&&b.goal!=null&&<div className="aw-progress"><progress max={b.goal} value={b.progress??0}/><span>{b.progress??0} / {b.goal}</span></div>}
  <div className="badge-card-status">{b.unlocked?`已收录${b.unlocked_at?' · '+b.unlocked_at.slice(0,10):''}`:'等待下一次进步'}{b.scope==='local'?' · 本机':''}</div>
  {!secret&&!b.unlocked&&b.action&&<Link className="aw-action" to={b.action}>去练习 →</Link>}
 </article>;
}
