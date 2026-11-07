import { NavLink, Outlet } from "react-router-dom";
import "./AppShell.css";

const links = [
  { to: "/", mark: "⌂", label: "今日学习" },
  { to: "/map", mark: "⚑", label: "学习路线" },
  { to: "/wrong-questions", mark: "↻", label: "强化练习" },
  { to: "/badges", mark: "☆", label: "成就徽章" },
];

export default function AppShell() {
  return <div className="shell-layout">
    <aside className="shell-sidebar">
      <NavLink to="/" className="shell-brand"><img src="/icons/spark.svg" alt="" />spark<span>quest</span></NavLink>
      <p className="shell-caption">每天一点，点亮大数据世界</p>
      <nav className="shell-nav" aria-label="主导航">{links.map(link =>
        <NavLink key={link.to} to={link.to} end={link.to === "/"} className={({ isActive }) => `shell-nav-link${isActive ? " shell-active" : ""}`}>
          <span aria-hidden="true">{link.mark}</span><strong>{link.label}</strong>
        </NavLink>)}</nav>
      <div className="shell-note"><span>小小进步，也很了不起。</span><p>让每一次练习，都成为下一次突破的火花。</p></div>
    </aside>
    <div className="shell-content"><Outlet /></div>
  </div>;
}
