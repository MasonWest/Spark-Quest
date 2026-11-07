import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import "./index.css";
import AppShell from "./components/AppShell";
import DelayedCheckPage from "./pages/DelayedCheckPage";
import Home from "./pages/Home";
import LessonPage from "./pages/LessonPage";
import MapPage from "./pages/MapPage";
import QuizPage from "./pages/QuizPage";
import ReviewPage from "./pages/ReviewPage";
import BadgesPage from "./pages/BadgesPage";
import WeakQuestionsPage from "./pages/WeakQuestionsPage";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell />}>
        <Route path="/" element={<Home />} />
        <Route path="/map" element={<MapPage />} />
        {/* Phase 6b: 间隔复习 */}
        {/* Phase 9.2: 徽章墙 */}
        <Route path="/badges" element={<BadgesPage />} />
        {/* Phase 10.1: 薄弱题 */}
        <Route path="/wrong-questions" element={<WeakQuestionsPage />} />
        </Route>
        <Route path="/lesson/:id" element={<LessonPage />} />
        <Route path="/lesson/:id/quiz" element={<QuizPage />} />
        <Route path="/delayed-check" element={<DelayedCheckPage />} />
        <Route path="/review/:id" element={<ReviewPage />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>
);

if (import.meta.env.PROD && 'serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(error => console.warn('PWA registration failed', error));
  });
}
