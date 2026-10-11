import { Link } from "react-router";
import { Shield, TrendingUp, Database, Brain, ArrowRight, AlertTriangle } from "lucide-react";

export function LandingPage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/5 to-indigo-600/5"></div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 relative">
          <div className="text-center max-w-3xl mx-auto">
            <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 px-4 py-2 rounded-full mb-6">
              <Brain className="w-4 h-4" />
              <span className="text-sm font-medium">AI 기반 리스크 분석</span>
            </div>

            <h1 className="text-5xl font-bold text-slate-900 mb-6">
              원룸 보증금,<br />안전하게 지키세요
            </h1>

            <p className="text-xl text-slate-600 mb-8">
              실거래가와 근저당 정보를 AI로 분석하여<br />
              경매 시 보증금 회수 가능성을 미리 확인하세요<br />
              월세, 반전세를 모두 포함합니다.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/analyze"
                className="inline-flex items-center justify-center gap-2 bg-blue-600 text-white px-8 py-4 rounded-xl hover:bg-blue-700 transition-colors shadow-lg shadow-blue-600/20"
              >
                <Shield className="w-5 h-5" />
               위험도 분석하기
                <ArrowRight className="w-5 h-5" />
              </Link>
              <a
                href="#how-it-works"
                className="inline-flex items-center justify-center gap-2 bg-white text-slate-700 px-8 py-4 rounded-xl hover:bg-slate-50 transition-colors border border-slate-200"
              >
                서비스 소개 보기
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">
              이런 고민 있으신가요?
            </h2>
            <p className="text-lg text-slate-600">
              전세 계약 전, 보증금 안전성을 확인하기 어려우셨죠?
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            <div className="bg-red-50 rounded-2xl p-6 border border-red-100">
              <AlertTriangle className="w-8 h-8 text-red-600 mb-4" />
              <h3 className="font-semibold text-slate-900 mb-2">근저당이 너무 많아요</h3>
              <p className="text-sm text-slate-600">
                집주인 대출이 많으면 경매 시 보증금을 못 받을 수 있습니다
              </p>
            </div>
            <div className="bg-red-50 rounded-2xl p-6 border border-red-100">
              <AlertTriangle className="w-8 h-8 text-red-600 mb-4" />
              <h3 className="font-semibold text-slate-900 mb-2">집값이 떨어지고 있어요</h3>
              <p className="text-sm text-slate-600">
                시세 하락 시 경매가도 낮아져 보증금 회수가 어려워집니다
              </p>
            </div>
            <div className="bg-red-50 rounded-2xl p-6 border border-red-100">
              <AlertTriangle className="w-8 h-8 text-red-600 mb-4" />
              <h3 className="font-semibold text-slate-900 mb-2">복잡해서 모르겠어요</h3>
              <p className="text-sm text-slate-600">
                등기부등본을 봐도 위험한지 안전한지 판단이 어렵습니다
              </p>
            </div>
            <div className="bg-red-50 rounded-2xl p-6 border border-red-100">
              <AlertTriangle className="w-8 h-8 text-red-600 mb-4" />
              <h3 className="font-semibold text-slate-900 mb-2">전문가 상담은 비싸요</h3>
              <p className="text-sm text-slate-600">
                변호사나 법무사 상담 비용 부담이 큽니다
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">
              AI가 3단계로 분석합니다
            </h2>
            <p className="text-lg text-slate-600">
              복잡한 권리분석을 쉽고 빠르게
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="relative">
              <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm h-full">
                <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-6">
                  <Database className="w-6 h-6 text-blue-600" />
                </div>
                <div className="absolute -top-3 -left-3 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                  1
                </div>
                <h3 className="font-semibold text-slate-900 mb-3">실거래가 분석</h3>
                <p className="text-sm text-slate-600">
                  최근 실거래 데이터를 분석하여 예상 경매가를 산정합니다
                </p>
              </div>
            </div>

            <div className="relative">
              <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm h-full">
                <div className="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center mb-6">
                  <TrendingUp className="w-6 h-6 text-indigo-600" />
                </div>
                <div className="absolute -top-3 -left-3 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                  2
                </div>
                <h3 className="font-semibold text-slate-900 mb-3">권리관계 검토</h3>
                <p className="text-sm text-slate-600">
                  근저당, 선순위 세입자 등 모든 권리관계를 종합 분석합니다
                </p>
              </div>
            </div>

            <div className="relative">
              <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm h-full">
                <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-6">
                  <Brain className="w-6 h-6 text-purple-600" />
                </div>
                <div className="absolute -top-3 -left-3 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                  3
                </div>
                <h3 className="font-semibold text-slate-900 mb-3">AI 위험도 예측</h3>
                <p className="text-sm text-slate-600">
                  AI로 보증금 회수 가능 금액과 위험도를 계산합니다
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-blue-600 to-indigo-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            지금 바로 분석해보세요
          </h2>
          <p className="text-lg text-blue-100 mb-8">
           
          </p>
          <Link
            to="/analyze"
            className="inline-flex items-center gap-2 bg-white text-blue-600 px-8 py-4 rounded-xl hover:bg-blue-50 transition-colors shadow-xl font-semibold"
          >
            <Shield className="w-5 h-5" />
            위험도 분석 시작하기
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>
    </div>
  );
}
