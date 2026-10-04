import { Outlet, Link, useLocation } from "react-router";
import { BarChart3, Home, FileText, Map } from "lucide-react";

export function RootLayout() {
  const location = useLocation();

  const isActive = (path: string) => {
    if (path === "/" && location.pathname === "/") return true;
    if (path !== "/" && location.pathname.startsWith(path)) return true;
    return false;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <nav className="bg-white border-b border-slate-200 sticky top-0 z-50 backdrop-blur-sm bg-white/90">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="font-semibold text-slate-900">용인 원룸 보증금분석</h1>
                <p className="text-xs text-slate-500">AI 보증금 위험도 분석</p>
              </div>
            </Link>

            <div className="flex gap-1">
              <Link
                to="/"
                className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
                  isActive("/") && location.pathname === "/"
                    ? "bg-blue-50 text-blue-600"
                    : "text-slate-600 hover:bg-slate-50"
                }`}
              >
                <Home className="w-4 h-4" />
                <span className="hidden sm:inline">홈</span>
              </Link>
              <Link
                to="/analyze"
                className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
                  isActive("/analyze")
                    ? "bg-blue-50 text-blue-600"
                    : "text-slate-600 hover:bg-slate-50"
                }`}
              >
                <FileText className="w-4 h-4" />
                <span className="hidden sm:inline">분석하기</span>
              </Link>
              <Link
                to="/data"
                className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
                  isActive("/data")
                    ? "bg-blue-50 text-blue-600"
                    : "text-slate-600 hover:bg-slate-50"
                }`}
              >
                <Map className="w-4 h-4" />
                <span className="hidden sm:inline">지역 데이터</span>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main>
        <Outlet />
      </main>
    </div>
  );
}
