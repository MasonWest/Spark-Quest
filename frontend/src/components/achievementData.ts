import type { Badge } from '../types';
import { journeyIndex, loadJourney } from '../content/journeys';
import { loadProgress, progressKey } from './journeyProgress';
import { loadDelayed, day } from './delayedProgress';
import bank from '../content/delayedChecks.json';

export const localDefinitions = [
  ['LOCAL_ANGLE','换个角度','原题答错后，通过补救，再答对原题',1,'bridge'],
  ['LOCAL_DAY','隔天还会','通过一次符合24小时规则的隔天验证',1,'echo'],
  ['LOCAL_FIVE','越记越牢','5个不同知识目标通过隔天验证',5,'orbit'],
  ['LOCAL_BOTH','两种表达','分别完成DataFrame与SQL的条件筛选练习',2,'pages'],
] as const;

export async function localAchievements(storage: Storage, now=Date.now()): Promise<Badge[]> {
  let angle=0;const goals=new Set<string>();const paired=new Set<string>();
  const events=loadDelayed(storage);
  for (const meta of Object.values(journeyIndex)) {
    if (!storage.getItem(progressKey(meta))) continue;
    const lesson=await loadJourney(meta.slug);if (!lesson) continue;
    const p=loadProgress(lesson,storage);
    for (const task of lesson.tasks) {
      const attempts=p.attempts.filter(a=>a.taskId===task.id && Number.isFinite(Date.parse(a.at)) && Date.parse(a.at)<=now);
      const right=(a:typeof attempts[number])=>!a.activity && task.fields.every(f=>a.answers[f.id]===f.correctOptionId && a.correctOptions[f.id]===f.correctOptionId);
      let wrong=false;let remedy=false;
      for (const a of attempts.filter(a=>a.runId===p.runId)) {
        if (!a.activity && !right(a)) wrong=true;
        if (wrong && a.activity==='remediation' && task.remediation && a.remediationId===task.remediation.id && a.answers[task.remediation.field.id]===task.remediation.field.correctOptionId && a.correctOptions[task.remediation.field.id]===task.remediation.field.correctOptionId) remedy=true;
        if (remedy && right(a)) angle=1;
      }
      if (rightEvidence(attempts,right) && ((meta.slug==='l2-select-filter' && task.id==='step-a4e9ad8ec5') || (meta.slug==='l3-where-order-limit' && task.id==='l3-where-order-limit/conditions'))) paired.add(meta.slug);
      for (const item of bank.items.filter(i=>i.slug===meta.slug && i.taskId===task.id)) {
        for (const e of events.filter(e=>e.itemId===item.id && e.correct && e.answer===item.correctOptionId && e.correctOptionId===item.correctOptionId && Date.parse(e.at)<=now && Date.parse(e.at)-Date.parse(e.sourceAt)>=day)) {
          const prior=events.slice(0,events.indexOf(e)).filter(v=>v.itemId===item.id && Date.parse(v.at)>=Date.parse(e.sourceAt) && Date.parse(v.at)<=Date.parse(e.at));
          if (prior.some(v=>v.correct) || Date.parse(e.at)-Math.max(Date.parse(e.sourceAt),...prior.map(v=>Date.parse(v.at)))<day) continue;
          const exposed=attempts.filter(a=>Date.parse(a.at)<=Date.parse(e.at));
          const latest=exposed.reduce((v,a)=>Math.max(v,Date.parse(a.at)),0);
          if (p.completedIds.includes(task.id) && latest===Date.parse(e.sourceAt) && exposed.some(right)) goals.add(item.knowledgeId);
        }
      }
    }
  }
  const counts=[angle,Math.min(1,goals.size),goals.size,paired.size];
  let receipts:Record<string,string>={};
  const raw=storage.getItem('spark-quest:local-achievements:v1');
  if (raw) {
    const parsed=JSON.parse(raw);
    if (!parsed || typeof parsed!=='object' || Array.isArray(parsed)) throw Error('Invalid local achievement record');
    for (const [code] of localDefinitions) if (code in parsed && (typeof parsed[code]!=='string' || !Number.isFinite(Date.parse(parsed[code])) || Date.parse(parsed[code])>now)) throw Error('Invalid achievement date');
    receipts=parsed;
  }
  let changed=false;
  const result=localDefinitions.map(([code,name,description,goal,icon],i)=>{
    if (counts[i]>=goal && !Number.isFinite(Date.parse(receipts[code]))) {receipts[code]=new Date(now).toISOString();changed=true;}
    const unlocked=typeof receipts[code]==='string' && Number.isFinite(Date.parse(receipts[code])) && Date.parse(receipts[code])<=now;
    return {code,name,description,goal,progress:unlocked?goal:Math.min(goal,counts[i]),image:`/badges/learning-${icon}.svg`,tier:'special' as const,sort_order:300+i,is_secret:false,unlocked,unlocked_at:unlocked?receipts[code]:null,group:'本机练习',action:code==='LOCAL_ANGLE'?'/map':code==='LOCAL_BOTH'?'/map':'/delayed-check',scope:'local' as const};
  });
  if (changed) storage.setItem('spark-quest:local-achievements:v1',JSON.stringify(receipts));
  return result;
}
function rightEvidence<T>(attempts:T[],right:(a:T)=>boolean) {return attempts.some(right);}

export function nextAchievement(badges:Badge[]) {
  return badges.filter(b=>!b.unlocked && !b.is_secret && b.goal && b.action && b.group && ['起步','复习与修复','坚持'].includes(b.group) && b.code!=='WELCOME_BACK' && b.scope!=='local')
    .sort((a,b)=>(b.progress??0)/b.goal!-(a.progress??0)/a.goal! || a.sort_order-b.sort_order)[0];
}
