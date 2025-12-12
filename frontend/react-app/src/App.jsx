import { BrowserRouter, Routes, Route } from "react-router-dom";
import PageLayout from "./layouts/PageLayout";
import LoginRegisterLayout from "./layouts/LoginRegisterLayout";

import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import CompareResults from "./pages/CompareResults";
import RunExperiments from "./pages/RunExperiment";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<PageLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/run_experiment" element={<RunExperiments />} />
          <Route path="/compare" element={<CompareResults />} />
        </Route>
		<Route element={<LoginRegisterLayout />}>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}