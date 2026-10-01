import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, NavLink, Navigate, Route, Routes } from "react-router-dom";
import { AutomotiveDemoPage } from "../pages/AutomotiveDemoPage";
import { EnterpriseDemoPage } from "../pages/EnterpriseDemoPage";
import { EvaluationPage } from "../pages/EvaluationPage";
import { HomePage } from "../pages/HomePage";
import { KnowledgePage } from "../pages/KnowledgePage";
import { BenchmarksPage } from "../pages/BenchmarksPage";

const queryClient = new QueryClient();

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="shell">
          <header className="header">
            <strong>agent-lab</strong>
            <nav>
              <NavLink to="/">Home</NavLink>
              <NavLink to="/ontology">Ontology Agent</NavLink>
              <NavLink to="/embedded">Embedded / ADAS AI</NavLink>
              <NavLink to="/evaluations">Evaluation</NavLink>
              <NavLink to="/benchmarks">Benchmarks</NavLink>
            </nav>
          </header>
          <main className="main">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/ontology" element={<KnowledgePage />} />
              <Route path="/embedded" element={<AutomotiveDemoPage />} />
              <Route path="/evaluations" element={<EvaluationPage />} />
              <Route path="/benchmarks" element={<BenchmarksPage />} />
              {/* Compat redirects from earlier routes */}
              <Route path="/enterprise" element={<Navigate to="/ontology" replace />} />
              <Route path="/knowledge" element={<Navigate to="/ontology" replace />} />
              <Route path="/automotive" element={<Navigate to="/embedded" replace />} />
              <Route path="/legacy-enterprise" element={<EnterpriseDemoPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
