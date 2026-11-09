import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import type { Badge, Dashboard } from "../types";
import { ProgressRing } from "../components/ui";
import "./Home.css";
import DelayedCheckLink from "../components/DelayedCheckLink";

import AchievementGoal from "../components/AchievementGoal";
import { nextAchievement } from "../components/achievementData";

export default function Home() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [error, setError] = useState(false);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    setError(false);
    fetch("/api/dashboard", { signal: controller.signal }).then(res => {
      if (!res.ok) throw new Error(); return res.json();
    }).then(setData).catch(e => { if (e.name !== "AbortError") setError(true); });
    return () => controller.abort();
  }, [attempt]);
  const [achievement,setAchievement]=useState<Badge>();
  useEffect(()=>{let active=true;fetch("/api/badges").then(r=>r.ok?r.json():[]).then(b=>{if(active)setAchievement(nextAchievement(b));}).catch(()=>{});return ()=>{active=false;};},[]);
  const lesson = data?.today_lesson;
  const level = data?.current_level;
  return <div className="home-page">
    <header className="home-topbar"><Link to="/" className="home-wordmark">spark quest<span> / 每天进步一点点</span></Link><span className="home-streak">🔥 {data?.streak_days ?? "—"}<small> 连续天数</small></span></header>
    <section className="home-welcome"><div><p className="home-eyebrow">LET’S SPARK SOMETHING</p><h1>{data?.studied_today ? "今天的你，又进步了！" : "准备好，点亮新技能！"}</h1><p>从一个小知识点开始，让 Spark 一点点变简单。</p></div><img className="home-mascot" src="/icons/spark.svg" alt="微笑的 Spark 火苗伙伴" /></section>
    <DelayedCheckLink />
    {achievement&&<AchievementGoal badge={achievement}/>}
    {error ? <div className="home-panel" role="alert"><h2>暂时连不上学习服务</h2><p>请确认后端服务已启动，再试一次。</p><button className="btn-primary" onClick={() => setAttempt(x => x + 1)}>重新加载</button></div> : !data ? <div className="home-panel home-loading" role="status">正在准备你的学习旅程…</div> : <div className="home-grid">
      <div className="home-main">
        <section className="home-lesson-card">
          <div className="home-course-label"><span>✦ {lesson?.status === "needs_review" ? "继续挑战" : lesson ? "你的下一站" : "旅程里程碑"}</span><span>APACHE SPARK</span></div>
          <div className="home-lesson-body"><p className="home-eyebrow">{level?.title ?? "学习旅程"}</p><h2>{lesson?.title ?? "全部课程，成功通关！"}</h2><p>{lesson?.description ?? "每一步坚持都算数。回到学习路线，巩固已经掌握的知识吧。"}</p>
            {lesson && <div className="home-lesson-meta"><span>◷ 约 {lesson.estimated_minutes} 分钟</span><span>✎ 学习 · 练习 · 掌握</span></div>}
            <Link className="btn-primary home-start" to={lesson ? `/lesson/${lesson.id}` : "/map"}>{lesson?.status === "needs_review" ? "温习并再次挑战" : lesson ? "开始学习" : "回顾学习路线"}<span aria-hidden="true">→</span></Link>
          </div>
        </section>
        <div className="home-section-heading"><h2>练一练，记得更牢</h2><span>每次练习都有收获</span></div>
        <div className="home-practice-grid"><Link to={data.reviews_due.length ? `/review/${data.reviews_due[0].lesson_id}` : "/map"} className="home-practice home-purple"><span className="home-tile-icon" aria-hidden="true">↻</span><h3>温故知新</h3><p>{data.reviews_due.length ? `${data.reviews_due.length} 节课程等你复习` : "暂时没有到期复习，继续探索吧"}</p><strong>{data.reviews_due.length ? "开始复习" : "探索课程"} →</strong></Link><Link to="/wrong-questions" className="home-practice home-amber"><span className="home-tile-icon" aria-hidden="true">ϟ</span><h3>薄弱点突破</h3><p>把上次的难题，变成这次的拿手题</p><strong>强化练习 →</strong></Link></div>
        {data.reviews_due.length > 0 && <section className="home-panel"><h2>待复习课程</h2>{data.reviews_due.map(r => <Link className="home-review-row" to={`/review/${r.lesson_id}`} key={r.lesson_id}><span><strong>{r.title}</strong><small>{r.level_title} · {r.overdue_days > 0 ? `逾期 ${r.overdue_days} 天` : "今天到期"}</small></span><span aria-hidden="true">→</span></Link>)}</section>}
        <Link to="/map" className="home-route-link"><span>⚑</span><div><strong>你的 Spark 探索地图</strong><p>从初识 Spark，到性能调优，一步一步解锁。</p></div><b aria-hidden="true">→</b></Link>
      </div>
      <aside className="home-aside">
        <section className="home-panel"><div className="home-section-heading"><h2>学习足迹</h2><span>✦</span></div><div className="home-progress"><ProgressRing percentage={data.progress.percentage} size={92} showLabel /><div><strong>{data.progress.completed}<small> / {data.progress.total} 课</small></strong><p>已完成课程</p></div></div><div className="home-level-caption"><span>当前阶段</span><strong>{level?.percentage ?? 0}%</strong></div><progress className="home-level-progress" value={level?.percentage ?? 0} max={100} aria-label="当前阶段完成进度" /><p className="home-level-detail">{level ? `${level.title} · 已完成 ${level.completed_count} / ${level.total_count} 课` : "已完成全部阶段"}</p><div className="home-record"><span>最长连续学习</span><strong>{data.longest_streak} 天</strong></div><div className="home-record"><span>今日状态</span><strong>{data.studied_today ? "已学习 ✓" : "等你点亮"}</strong></div></section>
        <section className="home-panel home-achievements"><div className="home-section-heading"><h2>闪闪发光的成就</h2><span>☆</span></div>{data.recent_badges?.length ? <div className="home-badges">{data.recent_badges.slice(0, 3).map(b => <Link to="/badges" key={b.code}><img src={b.image} alt={b.name} /><span>{b.name}</span></Link>)}</div> : <><div className="home-empty-badge" aria-hidden="true">☆</div><p>每一份坚持，都值得一枚徽章。<br />你的第一枚成就正在路上。</p></>}<Link className="home-text-link" to="/badges">打开成就徽章墙 →</Link></section>
        <section className="home-install"><span aria-hidden="true">↗</span><div><strong>把学习装进口袋</strong><p>iPhone Safari 中点击「分享」→「添加到主屏幕」，随时开启学习。</p></div></section>
      </aside>
    </div>}
    <footer className="home-footer">A LITTLE SPARK. A BIG DIFFERENCE.</footer>
  </div>;
}
