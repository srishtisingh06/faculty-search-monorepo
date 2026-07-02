import { Routes, Route } from "react-router-dom";

import LandingPage from "./pages/LandingPage";
import FacultySearchPage from "./pages/FacultySearchPage";
import FacultyProfilePage from "./pages/FacultyProfilePage";
import DepartmentExplorerPage from "./pages/DepartmentExplorerPage";
import InstitutesDirectoryPage from "./pages/InstitutesDirectoryPage";
import InstituteDetailPage from "./pages/InstituteDetailPage";
import CoverageDashboardPage from "./pages/CoverageDashboardPage";
import AnalyticsDashboardPage from "./pages/AnalyticsDashboardPage";

import LoadingPage from "./pages/LoadingPage";
import NoResultsPage from "./pages/NoResultsPage";
import NotFoundPage from "./pages/NotFoundPage";

function App() {
  return (
    <Routes>

      <Route path="/" element={<LandingPage />} />

      <Route path="/faculty" element={<FacultySearchPage />} />

      <Route
        path="/faculty/:facultyId"
        element={<FacultyProfilePage />}
      />

      <Route
        path="/departments"
        element={<DepartmentExplorerPage />}
      />

      <Route
        path="/institutes"
        element={<InstitutesDirectoryPage />}
      />

      <Route
        path="/institute/:id"
        element={<InstituteDetailPage />}
      />

      <Route
        path="/coverage"
        element={<CoverageDashboardPage />}
      />

      <Route
        path="/analytics"
        element={<AnalyticsDashboardPage />}
      />

      <Route
        path="/loading"
        element={<LoadingPage />}
      />

      <Route
        path="/no-results"
        element={<NoResultsPage />}
      />

      <Route
        path="*"
        element={<NotFoundPage />}
      />

    </Routes>
  );
}

export default App;