import { Link } from 'react-router-dom';
import type { Badge } from '../types';
import './AchievementGoal.css';
export default function AchievementGoal({badge}:{badge:Badge}) {
 return <section className="ag-goal" aria-label="下一个成就"><img src={badge.image} alt=""/><div><small>再往前一点 · 下一个成就</small><h2>{badge.name}</h2><p>{badge.description}</p><progress value={badge.progress??0} max={badge.goal??1}/><span>{badge.progress??0} / {badge.goal}</span><Link to={badge.action||'/map'}>继续积累 →</Link></div></section>;
}
