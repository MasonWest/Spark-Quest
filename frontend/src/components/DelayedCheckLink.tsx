import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import bank from "../content/delayedChecks.json";
import { journeyIndex } from "../content/journeys";
import { delayedQueue } from "./delayedProgress";
export default function DelayedCheckLink() {
  const [count, setCount] = useState(0);
  useEffect(() => {
    const refresh = () => { try { setCount(delayedQueue(bank.items, journeyIndex, localStorage).length); } catch { setCount(0); } };
    refresh(); const timer = window.setInterval(refresh, 60000);
    window.addEventListener("focus", refresh); window.addEventListener("storage", refresh);
    return () => { clearInterval(timer); window.removeEventListener("focus", refresh); window.removeEventListener("storage", refresh); };
  }, []);
  return count > 0 ? <section className="card"><h2>隔了一天，还记得吗？</h2><p>{count} 个知识点可以换个情境再判断，先试一题也可以。</p><Link className="btn-primary" to="/delayed-check">开始隔天验证 →</Link><p>本机练习 · 不改变正式成绩</p></section> : null;
}
