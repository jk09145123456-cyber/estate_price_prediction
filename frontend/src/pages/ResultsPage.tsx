import {
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import {
  AlertTriangle,
  CheckCircle,
  AlertCircle,
  TrendingDown,
  Home,
  DollarSign,
  Shield,
  Download,
  Share2,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router";
import {
  AnalysisResult,
  getTradeTrend,
  TradeTrendPoint,
} from "../services/api";

type RiskFactor = {
  title: string;
  description: string;
  tone: "danger" | "warning" | "info" | "success";
};

const FALLBACK_TRADE_TREND: TradeTrendPoint[] = [
  { year: "2021", averagePrice: 465000000, transactionCount: 18 },
  { year: "2022", averagePrice: 492000000, transactionCount: 22 },
  { year: "2023", averagePrice: 521000000, transactionCount: 26 },
  { year: "2024", averagePrice: 548000000, transactionCount: 24 },
  { year: "2025", averagePrice: 563000000, transactionCount: 19 },
  { year: "2026", averagePrice: 571000000, transactionCount: 15 },
];

function formatMoney(value: number): string {
  const amount = Number.isFinite(value) ? Math.abs(value) : 0;
  const sign = value < 0 ? "-" : "";

  if (amount >= 100_000_000) {
    const eok = Math.floor(amount / 100_000_000);
    const remainderManwon = Math.round((amount % 100_000_000) / 10_000);
    return `${sign}${eok}억${remainderManwon > 0 ? ` ${remainderManwon.toLocaleString("ko-KR")}만원` : ""}`;
  }

  return `${sign}${Math.round(amount / 10_000).toLocaleString("ko-KR")}만원`;
}

function formatMoneyDetail(value: number): string {
  return `${formatMoney(value)} (${Math.round(value).toLocaleString("ko-KR")}원)`;
}

export function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();

  const analysisResult = location.state?.analysisResult as AnalysisResult | undefined;
  const formData = location.state?.formData;

  const [tradeTrend, setTradeTrend] = useState<TradeTrendPoint[]>([]);

  useEffect(() => {
    if (!analysisResult) {
      alert("분석 결과가 없습니다. 먼저 분석을 진행해주세요.");
      navigate("/analyze");
    }
  }, [analysisResult, navigate]);

  useEffect(() => {
    let active = true;

    async function loadTrend() {
      try {
        const result = await getTradeTrend();
        if (active) {
          setTradeTrend(result.length > 0 ? result : FALLBACK_TRADE_TREND);
        }
      } catch (error) {
        console.error("실거래 추이 로딩 실패:", error);
        if (active) {
          setTradeTrend(FALLBACK_TRADE_TREND);
        }
      }
    }

    loadTrend();

    return () => {
      active = false;
    };
  }, []);

  const riskLevel = analysisResult?.riskLevel ?? "주의";
  const recoveryRate = analysisResult?.recoveryRate ?? 60;
  const depositAmount = analysisResult?.depositAmount ?? 0;
  const recoverableAmount = analysisResult?.recoverableAmount ?? 0;
  const expectedAuctionPrice = analysisResult?.expectedAuctionPrice ?? 0;
  const mortgageAmount = analysisResult?.mortgageAmount ?? 0;
  const priorTenantsAmount = analysisResult?.priorTenantsAmount ?? 0;
  const auctionCost = analysisResult?.auctionCost ?? 0;
  const smallTenantApplied =
    analysisResult?.smallTenantApplied ?? (depositAmount > 0 && depositAmount <= 140_000_000);
  const priorityRepaymentApplied =
    analysisResult?.priorityRepaymentApplied ?? (depositAmount > 0 && depositAmount <= 48_000_000);
  const recoveryRuleMessage =
    analysisResult?.recoveryRuleMessage ??
    (priorityRepaymentApplied
      ? "소액임차인 최우선변제 대상입니다. 우선변제 한도 범위에서 회수 금액을 계산합니다."
      : smallTenantApplied
        ? "소액임차인 적용 구간입니다. 우선변제 대상 여부와 경매 잔여금을 함께 반영해 회수 금액을 계산합니다."
        : "일반 임차인 기준으로 경매 잔여금과 선순위 채권을 반영해 회수 금액을 계산합니다.");

  const remainingAfterAuction = Math.max(
    expectedAuctionPrice - mortgageAmount - priorTenantsAmount - auctionCost,
    0
  );
  const unrecoverableAmount = Math.max(depositAmount - recoverableAmount, 0);

  const priceHistory = useMemo(
    () =>
      (tradeTrend.length > 0 ? tradeTrend : FALLBACK_TRADE_TREND).map((item) => ({
        period: item.year,
        price: item.averagePrice,
      })),
    [tradeTrend]
  );

  const pieData = useMemo(
    () => [
      {
        name: "회수 가능",
        value: recoverableAmount,
        color: "#22c55e",
      },
      {
        name: "회수 불가능",
        value: unrecoverableAmount,
        color: "#ef4444",
      },
    ],
    [recoverableAmount, unrecoverableAmount]
  );

  const riskFactors: RiskFactor[] = useMemo(() => {
    const factors: RiskFactor[] = [];

    if (recoveryRate >= 90) {
      factors.push({
        title: "회수율 양호",
        description: `예상 회수율이 ${recoveryRate}%로 높습니다.`,
        tone: "success",
      });
    } else {
      factors.push({
        title: "회수율 주의",
        description: `예상 회수율이 ${recoveryRate}%로 보증금 전액 회수가 어렵습니다.`,
        tone: "warning",
      });
    }

    if (mortgageAmount > 0) {
      factors.push({
        title: "근저당 존재",
        description: `근저당 ${formatMoney(mortgageAmount)}가 선순위로 반영됩니다.`,
        tone: "danger",
      });
    }

    if (priorTenantsAmount > 0) {
      factors.push({
        title: "선순위 임차인",
        description: `선순위 임차보증금 ${formatMoney(priorTenantsAmount)}이 먼저 빠집니다.`,
        tone: "warning",
      });
    }

    if (smallTenantApplied) {
      factors.push({
        title: "소액임차인 보호",
        description: priorityRepaymentApplied
          ? "소액임차인 최우선변제 대상이라 우선변제 한도 기준으로 회수 금액을 계산합니다."
          : "소액임차인 적용 구간으로 분류되어 우선변제 규정이 반영됩니다.",
        tone: "info",
      });
    }

    if (remainingAfterAuction <= 0) {
      factors.push({
        title: "잔여 재원 부족",
        description: "경매가에서 선순위 채권과 비용을 제외하면 회수 재원이 부족합니다.",
        tone: "danger",
      });
    }

    if (recoverableAmount < depositAmount) {
      factors.push({
        title: "부분 회수",
        description: `보증금 ${formatMoney(depositAmount)} 중 ${formatMoney(recoverableAmount)}만 회수 가능합니다.`,
        tone: "warning",
      });
    }

    return factors.slice(0, 4);
  }, [
    depositAmount,
    mortgageAmount,
    priorTenantsAmount,
    recoveryRate,
    recoverableAmount,
    remainingAfterAuction,
    smallTenantApplied,
    priorityRepaymentApplied,
  ]);

  const getRiskColor = () => {
    if (riskLevel === "안전") return "text-green-600 bg-green-50 border-green-200";
    if (riskLevel === "주의") return "text-amber-600 bg-amber-50 border-amber-200";
    return "text-red-600 bg-red-50 border-red-200";
  };

  const getRiskIcon = () => {
    if (riskLevel === "안전") return <CheckCircle className="w-6 h-6" />;
    if (riskLevel === "주의") return <AlertCircle className="w-6 h-6" />;
    return <AlertTriangle className="w-6 h-6" />;
  };

  const toneClasses = {
    danger: "bg-red-50 border-red-200 text-red-700",
    warning: "bg-amber-50 border-amber-200 text-amber-700",
    info: "bg-blue-50 border-blue-200 text-blue-700",
    success: "bg-green-50 border-green-200 text-green-700",
  } as const;

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 mb-2">AI 위험 분석 결과</h1>
              <p className="text-slate-600">
                {formData?.address || "경기도 용인시 수지구 동천동 1234"} ·{" "}
                {formData?.buildingType || "아파트"} · {formData?.area ? `${formData.area}㎡` : "84㎡"}
              </p>
            </div>
            <div className="flex gap-2">
            </div>
          </div>
        </div>

        <div className={`rounded-2xl border p-8 mb-8 ${getRiskColor()}`}>
          <div className="flex items-start gap-4">
            {getRiskIcon()}
            <div className="flex-1">
              <h2 className="text-2xl font-bold mb-2">위험도: {riskLevel}</h2>
              <p className="text-lg mb-4">
                경매 시 보증금의 약 <strong>{recoveryRate}%</strong> 회수 가능할 것으로 예상됩니다.
              </p>
              <div className="flex flex-wrap gap-2 mb-4">
                {smallTenantApplied && (
                  <span className="inline-flex items-center rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700">
                    소액임차인 적용
                  </span>
                )}
                {priorityRepaymentApplied && (
                  <span className="inline-flex items-center rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-sm font-medium text-amber-700">
                    최우선변제 대상
                  </span>
                )}
              </div>
              <div className="bg-white/50 rounded-xl p-4 border border-current">
                <p className="text-sm">
                  {recoveryRuleMessage}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
                <Home className="w-5 h-5 text-blue-600" />
              </div>
              <h3 className="font-medium text-slate-900">예상 경매가</h3>
            </div>
            <div className="text-3xl font-bold text-slate-900 mb-1">
              {formatMoney(expectedAuctionPrice)}
            </div>
            <p className="text-sm text-slate-500">AI 예측 결과</p>
          </div>

            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center">
                  <DollarSign className="w-5 h-5 text-green-600" />
                </div>
                <h3 className="font-medium text-slate-900">회수 가능 금액</h3>
              </div>
              <div className="text-3xl font-bold text-green-600 mb-1">
                {formatMoney(recoverableAmount)}
              </div>
              <p className="text-sm text-slate-500">
              {smallTenantApplied
                ? priorityRepaymentApplied
                  ? "소액임차인 최우선변제 대상입니다."
                  : "소액임차인 적용 구간입니다."
                : `보증금 ${formatMoney(depositAmount)} 중`}
              </p>
            </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-purple-100 rounded-xl flex items-center justify-center">
                <Shield className="w-5 h-5 text-purple-600" />
              </div>
              <h3 className="font-medium text-slate-900">회수 가능 비율</h3>
            </div>
            <div className="text-3xl font-bold text-slate-900 mb-1">{recoveryRate}%</div>
            <p className="text-sm text-slate-500">분석 결과</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
            <h3 className="font-semibold text-slate-900 mb-6">보증금 회수 분석</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name} ${formatMoney(Number(value))}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => formatMoney(Number(value))} />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="text-sm text-slate-700">회수 가능</span>
                <span className="font-semibold text-green-600">{formatMoney(recoverableAmount)}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                <span className="text-sm text-slate-700">회수 불가능</span>
                <span className="font-semibold text-red-600">{formatMoney(unrecoverableAmount)}</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
            <h3 className="font-semibold text-slate-900 mb-6">실거래가 추이(연도별 평균)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={priceHistory}>
                <defs>
                  <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="period" tick={{ fontSize: 12 }} stroke="#94a3b8" />
                <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" tickFormatter={(value) => formatMoney(Number(value))} />
                <Tooltip
                  contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }}
                  formatter={(value) => [formatMoney(Number(value)), "실거래가"]}
                />
                <Area
                  type="monotone"
                  dataKey="price"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorPrice)"
                />
              </AreaChart>
            </ResponsiveContainer>
            <div className="mt-4 flex items-center gap-2 text-sm text-slate-600">
              <TrendingDown className="w-4 h-4 text-red-500" />
              JSON 데이터 기준 연도별 평균 실거래가를 반영합니다.
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm mb-8">
          <h3 className="font-semibold text-slate-900 mb-6 text-xl">상세 분석</h3>

          <div className="space-y-6">
            <div className="rounded-xl border border-blue-200 bg-blue-50 p-4 text-blue-800">
              <h4 className="font-medium mb-1">회수 규칙 판정</h4>
              <p className="text-sm">
                {recoveryRuleMessage}
              </p>
            </div>

            <div>
              <h4 className="font-medium text-slate-900 mb-3">회수 계산 내역</h4>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                  <span className="text-slate-700">예상 경매가</span>
                  <span className="font-semibold text-slate-900">{formatMoney(expectedAuctionPrice)}</span>
                </div>
                <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                  <span className="text-slate-700">근저당 채권</span>
                  <span className="font-semibold text-red-600">-{formatMoney(mortgageAmount)}</span>
                </div>
                <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                  <span className="text-slate-700">선순위 임차보증금</span>
                  <span className="font-semibold text-red-600">-{formatMoney(priorTenantsAmount)}</span>
                </div>
                <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                  <span className="text-slate-700">경매 비용</span>
                  <span className="font-semibold text-red-600">-{formatMoney(auctionCost)}</span>
                </div>
                <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                  <span className="text-slate-700">경매 후 잔여금</span>
                  <span className="font-semibold text-slate-900">{formatMoney(remainingAfterAuction)}</span>
                </div>
                <div className="border-t-2 border-slate-300 pt-3">
                  <div className="flex items-center justify-between p-4 bg-blue-50 rounded-xl">
                    <span className="font-semibold text-slate-900">최종 회수 가능 금액</span>
                    <span className="text-2xl font-bold text-blue-600">{formatMoney(recoverableAmount)}</span>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <h4 className="font-medium text-slate-900 mb-3">위험 요인</h4>
              <div className="space-y-2">
                {riskFactors.map((factor) => (
                  <div
                    key={factor.title}
                    className={`flex items-start gap-3 p-4 border rounded-xl ${toneClasses[factor.tone]}`}
                  >
                    <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                    <div>
                      <h5 className="font-medium mb-1">{factor.title}</h5>
                      <p className="text-sm">{factor.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-medium text-slate-900 mb-3">안전 조치 권장사항</h4>
              <div className="space-y-2">
                <div className="flex items-start gap-3 p-4 bg-blue-50 border border-blue-200 rounded-xl">
                  <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h5 className="font-medium text-blue-900 mb-1">전세보증보험 검토</h5>
                    <p className="text-sm text-blue-700">보증보험 가입 가능 여부를 먼저 확인하는 것이 좋습니다.</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-4 bg-blue-50 border border-blue-200 rounded-xl">
                  <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h5 className="font-medium text-blue-900 mb-1">보증금 조정</h5>
                    <p className="text-sm text-blue-700">가능하면 보증금을 낮추거나 추가 담보 조건을 확인하세요.</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-4 bg-blue-50 border border-blue-200 rounded-xl">
                  <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h5 className="font-medium text-blue-900 mb-1">등기부 재확인</h5>
                    <p className="text-sm text-blue-700">최종 계약 전 등기부와 권리관계를 다시 확인하세요.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-slate-50 border border-slate-200 rounded-xl p-6 text-sm text-slate-600">
          <h4 className="font-medium text-slate-900 mb-2">분석 결과 안내</h4>
          <ul className="space-y-1 list-disc list-inside">
            <li>분석 결과는 AI 모델 예측값과 경매 회수 규칙을 조합해 산출합니다.</li>
            <li>실제 경매 결과는 시세, 권리관계, 유찰 여부에 따라 달라질 수 있습니다.</li>
            <li>최종 계약 전에는 반드시 등기부등본과 현장 정보를 확인하세요.</li>
            <li>법적 책임이 필요한 의사결정에는 참고 자료로만 사용하세요.</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
