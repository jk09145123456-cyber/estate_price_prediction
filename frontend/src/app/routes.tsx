import { createBrowserRouter } from "react-router";
import { LandingPage } from "./pages/LandingPage";
import { AnalysisInputPage } from "./pages/AnalysisInputPage";
import { ResultsPage } from "./pages/ResultsPage";
import { RegionalDataPage } from "./pages/RegionalDataPage";
import { RootLayout } from "./components/RootLayout";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: RootLayout,
    children: [
      { index: true, Component: LandingPage },
      { path: "analyze", Component: AnalysisInputPage },
      { path: "results", Component: ResultsPage },
      { path: "data", Component: RegionalDataPage },
    ],
  },
]);
