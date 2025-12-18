import { BrowserRouter, Routes, Route } from "react-router-dom";
import PageLayout from "./layouts/PageLayout";
import LoginRegisterLayout from "./layouts/LoginRegisterLayout";

import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import CompareResults from "./pages/CompareResults";
import RunExperiments from "./pages/RunExperiment";
import History from "./pages/History";
import Demo from "./pages/Demo";
import { AuthProvider } from './context/AuthContext';
import PublicRoute from "./context/PublicRoute";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<PageLayout />}>
            <Route path="/" element={<Home />} />
            <Route path="/run_experiment" element={<RunExperiments />} />
            <Route path="/compare" element={<CompareResults />} />
            <Route path="/history" element={<History />} />
            <Route path="/demo" element={<Demo />} />
          </Route>
          <Route element={<LoginRegisterLayout />}>
            <Route 
              path="/login"
              element={
                <PublicRoute>
                  <Login /> 
                </PublicRoute>}
             />
            <Route 
              path="/register" 
              element={
                <PublicRoute>
                  <Register /> 
                </PublicRoute>
                } 
              />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}