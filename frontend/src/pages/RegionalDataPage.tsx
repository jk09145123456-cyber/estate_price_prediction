import { type ReactNode, useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Building2, Clock, DollarSign, MapPin, Search, X } from "lucide-react";
import { getRegionalAnalysis, type RegionalAnalysisStat } from "../services/api";

const SEARCH_HISTORY_KEY = "regional-search-history";
const BAND_ORDER = ["60㎡ 이하", "60~85㎡", "85~102㎡", "102㎡ 초과"];

type AreaSummary = { band: string; avgDeposit: number; transactionCount: number };

const fallbackRegionalData: RegionalAnalysisStat[] = [
  {
    region: "수지구",
    avgDeposit: 520_000_000,
    avgMonthlyRent: 1_250_000,
    transactions: 189,
    jeonseCount: 138,
    monthlyRentCount: 51,
    areaBands: [
      { band: "60㎡ 이하", avgDeposit: 320_000_000, transactionCount: 24 },
      { band: "60~85㎡", avgDeposit: 410_000_000, transactionCount: 49 },
      { band: "85~102㎡", avgDeposit: 540_000_000, transactionCount: 62 },
      { band: "102㎡ 초과", avgDeposit: 690_000_000, transactionCount: 54 },
    ],
    monthlyTrend: [
      { month: "2025-01", avgDeposit: 505_000_000, transactionCount: 28 },
      { month: "2025-02", avgDeposit: 510_000_000, transactionCount: 31 },
      { month: "2025-03", avgDeposit: 515_000_000, transactionCount: 33 },
      { month: "2025-04", avgDeposit: 522_000_000, transactionCount: 31 },
      { month: "2025-05", avgDeposit: 528_000_000, transactionCount: 32 },
      { month: "2025-06", avgDeposit: 525_000_000, transactionCount: 34 },
    ],
  },
  {
    region: "기흥구",
    avgDeposit: 480_000_000,
    avgMonthlyRent: 1_150_000,
    transactions: 245,
    jeonseCount: 171,
    monthlyRentCount: 74,
    areaBands: [
      { band: "60㎡ 이하", avgDeposit: 300_000_000, transactionCount: 31 },
      { band: "60~85㎡", avgDeposit: 385_000_000, transactionCount: 61 },
      { band: "85~102㎡", avgDeposit: 495_000_000, transactionCount: 83 },
      { band: "102㎡ 초과", avgDeposit: 640_000_000, transactionCount: 70 },
    ],
    monthlyTrend: [
      { month: "2025-01", avgDeposit: 470_000_000, transactionCount: 35 },
      { month: "2025-02", avgDeposit: 475_000_000, transactionCount: 37 },
      { month: "2025-03", avgDeposit: 482_000_000, transactionCount: 40 },
      { month: "2025-04", avgDeposit: 486_000_000, transactionCount: 42 },
      { month: "2025-05", avgDeposit: 488_000_000, transactionCount: 45 },
      { month: "2025-06", avgDeposit: 484_000_000, transactionCount: 46 },
    ],
  },
  {
    region: "처인구",
    avgDeposit: 420_000_000,
    avgMonthlyRent: 980_000,
    transactions: 156,
    jeonseCount: 102,
    monthlyRentCount: 54,
    areaBands: [
      { band: "60㎡ 이하", avgDeposit: 250_000_000, transactionCount: 28 },
      { band: "60~85㎡", avgDeposit: 335_000_000, transactionCount: 44 },
      { band: "85~102㎡", avgDeposit: 440_000_000, transactionCount: 47 },
      { band: "102㎡ 초과", avgDeposit: 585_000_000, transactionCount: 37 },
    ],
    monthlyTrend: [
      { month: "2025-01", avgDeposit: 410_000_000, transactionCount: 22 },
      { month: "2025-02", avgDeposit: 414_000_000, transactionCount: 24 },
      { month: "2025-03", avgDeposit: 418_000_000, transactionCount: 26 },
      { month: "2025-04", avgDeposit: 421_000_000, transactionCount: 28 },
      { month: "2025-05", avgDeposit: 425_000_000, transactionCount: 27 },
      { month: "2025-06", avgDeposit: 423_000_000, transactionCount: 29 },
    ],
  },
];

function readSearchHistory() {
  try {
    const parsed = JSON.parse(localStorage.getItem(SEARCH_HISTORY_KEY) ?? "[]");
    return Array.isArray(parsed) ? parsed.slice(0, 5) : [];
  } catch {
    return [];
  }
}

function saveSearchHistory(history: string[]) {
  localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(history.slice(0, 5)));
}

function compareBandOrder(a: string, b: string) {
  const aIndex = BAND_ORDER.indexOf(a);
  const bIndex = BAND_ORDER.indexOf(b);
  return aIndex === -1 || bIndex === -1 ? a.localeCompare(b, "ko-KR") : aIndex - bIndex;
}

function formatMoney(value: number) {
  const amount = Number.isFinite(value) ? Math.abs(value) : 0;
  const sign = value < 0 ? "-" : "";
  if (amount >= 100_000_000) {
    const eok = Math.floor(amount / 100_000_000);
    const manwon = Math.round((amount % 100_000_000) / 10_000);
    return `${sign}${eok}억${manwon > 0 ? ` ${manwon.toLocaleString("ko-KR")}만원` : ""}`;
  }
  return `${sign}${Math.round(amount / 10_000).toLocaleString("ko-KR")}만원`;
}

function formatPriceChange(prevValue: number, nextValue: number) {
  if (!Number.isFinite(prevValue) || prevValue <= 0 || !Number.isFinite(nextValue)) return "-";
  const diff = nextValue - prevValue;
  const rate = (Math.abs(diff) / prevValue) * 100;
  return `${diff >= 0 ? "상승" : "하락"} ${rate.toFixed(1)}%`;
}

function matchesRegionQuery(item: RegionalAnalysisStat, query: string) {
  return [item.region, item.parentRegion]
    .filter(Boolean)
    .map((value) => String(value).toLowerCase())
    .some((value) => value.includes(query));
}

export function RegionalDataPage() {
  const [searchInput, setSearchInput] = useState("");
  const [activeQuery, setActiveQuery] = useState("");
  const [searchHistory, setSearchHistory] = useState<string[]>([]);
  const [regionalData, setRegionalData] = useState<RegionalAnalysisStat[]>(fallbackRegionalData);
  const [isLoadingData, setIsLoadingData] = useState(true);
  const [dataError, setDataError] = useState("");

  useEffect(() => setSearchHistory(readSearchHistory()), []);

  useEffect(() => {
    let ignore = false;
    async function loadData() {
      try {
        setIsLoadingData(true);
        setDataError("");
        const result = await getRegionalAnalysis();
        if (!ignore && result.length > 0) setRegionalData(result);
      } catch (error) {
        if (!ignore) setDataError(error instanceof Error ? error.message : "지역 분석 데이터 조회에 실패했습니다.");
      } finally {
        if (!ignore) setIsLoadingData(false);
      }
    }
    loadData();
    return () => { ignore = true; };
  }, []);

  const filteredData = useMemo(() => {
    const query = activeQuery.trim().toLowerCase();
    return query ? regionalData.filter((item) => matchesRegionQuery(item, query)) : regionalData;
  }, [activeQuery, regionalData]);

  const aggregates = useMemo(() => {
    const totalTransactions = filteredData.reduce((sum, item) => sum + item.transactions, 0);
    const totalDeposit = filteredData.reduce((sum, item) => sum + item.avgDeposit * item.transactions, 0);
    const totalMonthlyRent = filteredData.reduce((sum, item) => sum + item.avgMonthlyRent * item.monthlyRentCount, 0);
    const totalJeonse = filteredData.reduce((sum, item) => sum + item.jeonseCount, 0);
    const totalMonthlyRentCount = filteredData.reduce((sum, item) => sum + item.monthlyRentCount, 0);
    const bandMap = new Map<string, AreaSummary>();
    const monthMap = new Map<string, { month: string; avgDeposit: number; transactionCount: number }>();

    filteredData.forEach((item) => {
      item.areaBands.forEach((band) => {
        const current = bandMap.get(band.band) ?? { band: band.band, avgDeposit: 0, transactionCount: 0 };
        current.avgDeposit += band.avgDeposit * band.transactionCount;
        current.transactionCount += band.transactionCount;
        bandMap.set(band.band, current);
      });
      item.monthlyTrend.forEach((point) => {
        const current = monthMap.get(point.month) ?? { month: point.month, avgDeposit: 0, transactionCount: 0 };
        current.avgDeposit += point.avgDeposit * point.transactionCount;
        current.transactionCount += point.transactionCount;
        monthMap.set(point.month, current);
      });
    });

    const areaBands = Array.from(bandMap.values())
      .map((item) => ({ ...item, avgDeposit: item.transactionCount > 0 ? Math.round(item.avgDeposit / item.transactionCount) : 0 }))
      .sort((a, b) => compareBandOrder(a.band, b.band));
    const monthlyTrend = Array.from(monthMap.values())
      .map((item) => ({ ...item, avgDeposit: item.transactionCount > 0 ? Math.round(item.avgDeposit / item.transactionCount) : 0 }))
      .sort((a, b) => a.month.localeCompare(b.month));

    return {
      totalTransactions,
      averageDeposit: totalTransactions > 0 ? Math.round(totalDeposit / totalTransactions) : 0,
      averageMonthlyRent: totalMonthlyRentCount > 0 ? Math.round(totalMonthlyRent / totalMonthlyRentCount) : 0,
      totalJeonse,
      totalMonthlyRentCount,
      jeonseRatio: totalTransactions > 0 ? (totalJeonse / totalTransactions) * 100 : 0,
      monthlyRatio: totalTransactions > 0 ? (totalMonthlyRentCount / totalTransactions) * 100 : 0,
      topRegion: [...filteredData].sort((a, b) => b.transactions - a.transactions)[0],
      topAreaBand: [...areaBands].sort((a, b) => b.transactionCount - a.transactionCount)[0],
      areaBands,
      monthlyTrend,
    };
  }, [filteredData]);

  const ratioData = [
    { name: "전세", value: aggregates.totalJeonse, color: "#2563eb" },
    { name: "월세", value: aggregates.totalMonthlyRentCount, color: "#f97316" },
  ];

  const handleSearch = (query = searchInput) => {
    const normalized = query.trim();
    setActiveQuery(normalized);
    setSearchInput(normalized);
    if (!normalized) return;
    const nextHistory = [normalized, ...searchHistory.filter((item) => item !== normalized)].slice(0, 5);
    setSearchHistory(nextHistory);
    saveSearchHistory(nextHistory);
  };

  const handleClearSearch = () => { setSearchInput(""); setActiveQuery(""); };
  const handleClearHistory = () => { setSearchHistory([]); saveSearchHistory([]); };

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">지역 분석 데이터</h1>
          <p className="text-slate-600">DB 전월세 거래 데이터를 기준으로 지역별 보증금, 월세, 거래 비율, 면적대, 계약월 추이를 확인합니다.</p>
        </div>

        <div className="bg-white border border-slate-200 p-6 shadow-sm mb-8">
          <div className="flex flex-col gap-4">
            <div className="flex gap-3">
              <div className="flex-1 relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="text"
                  value={searchInput}
                  onChange={(event) => setSearchInput(event.target.value)}
                  onKeyDown={(event) => { if (event.key === "Enter") handleSearch(); }}
                  placeholder="지역명 검색: 수지구, 죽전동, 기흥구"
                  className="w-full pl-12 pr-12 py-3 border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                {searchInput && <button type="button" onClick={handleClearSearch} className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700" aria-label="검색어 지우기"><X className="w-5 h-5" /></button>}
              </div>
              <button type="button" onClick={() => handleSearch()} className="px-6 py-3 bg-blue-600 text-white hover:bg-blue-700 transition-colors">검색</button>
            </div>

            {searchHistory.length > 0 && (
              <div className="flex flex-wrap items-center gap-2">
                <div className="flex items-center gap-1 text-sm text-slate-500 mr-1"><Clock className="w-4 h-4" />최근 검색</div>
                {searchHistory.map((item) => <button key={item} type="button" onClick={() => handleSearch(item)} className="px-3 py-1.5 bg-slate-100 text-slate-700 text-sm hover:bg-slate-200">{item}</button>)}
                <button type="button" onClick={handleClearHistory} className="px-3 py-1.5 text-sm text-slate-500 hover:text-slate-900">기록 삭제</button>
              </div>
            )}

            <div className="text-sm text-slate-600">{activeQuery ? `"${activeQuery}" 검색 결과 ${filteredData.length.toLocaleString("ko-KR")}개 지역` : `전체 ${filteredData.length.toLocaleString("ko-KR")}개 지역`}</div>
            <div className="text-xs text-slate-500">{isLoadingData ? "DB 지역 분석 데이터를 불러오는 중입니다." : dataError ? `DB 연결 실패: ${dataError} 샘플 데이터를 표시합니다.` : "DB 지역 분석 데이터를 기준으로 표시합니다."}</div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <MetricCard icon={<Building2 className="w-5 h-5 text-blue-600" />} title="평균 보증금" value={formatMoney(aggregates.averageDeposit)} helper="검색 결과 기준 가중 평균" tone="bg-blue-100" />
          <MetricCard icon={<MapPin className="w-5 h-5 text-emerald-600" />} title="전세 비율" value={`${aggregates.jeonseRatio.toFixed(1)}%`} helper={`전세 ${aggregates.totalJeonse.toLocaleString("ko-KR")}건`} tone="bg-emerald-100" />
          <MetricCard icon={<DollarSign className="w-5 h-5 text-amber-600" />} title="월세 비율" value={`${aggregates.monthlyRatio.toFixed(1)}%`} helper={`평균 월세 ${formatMoney(aggregates.averageMonthlyRent)}`} tone="bg-amber-100" />
          <MetricCard icon={<Building2 className="w-5 h-5 text-purple-600" />} title="거래 최다 지역" value={aggregates.topRegion?.region || "-"} helper={`거래 ${aggregates.topRegion?.transactions.toLocaleString("ko-KR") ?? 0}건`} tone="bg-purple-100" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <ChartPanel title="계약년월별 거래 추이"><ResponsiveContainer width="100%" height={300}><LineChart data={aggregates.monthlyTrend}><CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" /><XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="#94a3b8" /><YAxis yAxisId="left" tick={{ fontSize: 12 }} stroke="#94a3b8" /><YAxis yAxisId="right" orientation="right" tick={{ fontSize: 12 }} stroke="#94a3b8" tickFormatter={(value) => formatMoney(Number(value))} /><Tooltip formatter={(value, name) => name === "평균 보증금" ? [formatMoney(Number(value)), name] : [Number(value).toLocaleString("ko-KR"), name]} /><Line yAxisId="left" type="monotone" dataKey="transactionCount" stroke="#2563eb" name="거래 건수" /><Line yAxisId="right" type="monotone" dataKey="avgDeposit" stroke="#7c3aed" name="평균 보증금" /></LineChart></ResponsiveContainer></ChartPanel>
          <ChartPanel title="전세 / 월세 비율"><ResponsiveContainer width="100%" height={300}><PieChart><Pie data={ratioData} cx="50%" cy="50%" labelLine={false} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`} outerRadius={90} dataKey="value">{ratioData.map((entry) => <Cell key={entry.name} fill={entry.color} />)}</Pie><Tooltip formatter={(value) => Number(value).toLocaleString("ko-KR")} /></PieChart></ResponsiveContainer></ChartPanel>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <ChartPanel title="면적대별 평균 보증금"><ResponsiveContainer width="100%" height={300}><BarChart data={aggregates.areaBands}><CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" /><XAxis dataKey="band" tick={{ fontSize: 12 }} stroke="#94a3b8" /><YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" tickFormatter={(value) => formatMoney(Number(value))} /><Tooltip formatter={(value) => [formatMoney(Number(value)), "평균 보증금"]} /><Bar dataKey="avgDeposit" fill="#0ea5e9" radius={[8, 8, 0, 0]} /></BarChart></ResponsiveContainer></ChartPanel>
          <ChartPanel title="면적대별 거래 요약"><SummaryTable areaBands={aggregates.areaBands} /></ChartPanel>
        </div>

        <div className="bg-white border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-slate-200"><h3 className="font-semibold text-slate-900">지역별 상세 정보</h3></div>
          <div className="overflow-x-auto"><table className="w-full"><thead className="bg-slate-50"><tr><th className="px-6 py-4 text-left text-sm font-medium text-slate-900">지역</th><th className="px-6 py-4 text-left text-sm font-medium text-slate-900">상위 구</th><th className="px-6 py-4 text-right text-sm font-medium text-slate-900">평균 보증금</th><th className="px-6 py-4 text-right text-sm font-medium text-slate-900">평균 월세</th><th className="px-6 py-4 text-right text-sm font-medium text-slate-900">전세/월세 비율</th><th className="px-6 py-4 text-right text-sm font-medium text-slate-900">가격 변화</th><th className="px-6 py-4 text-right text-sm font-medium text-slate-900">거래 건수</th><th className="px-6 py-4 text-right text-sm font-medium text-slate-900">주요 면적대</th></tr></thead><tbody className="divide-y divide-slate-200">{filteredData.map((item) => { const topBand = [...item.areaBands].sort((a, b) => b.transactionCount - a.transactionCount)[0]; const ratio = item.transactions > 0 ? (item.jeonseCount / item.transactions) * 100 : 0; const latestTrend = item.monthlyTrend[item.monthlyTrend.length - 1]; const previousTrend = item.monthlyTrend[item.monthlyTrend.length - 2]; return <tr key={`${item.parentRegion ?? "root"}-${item.region}`} className="hover:bg-slate-50 transition-colors"><td className="px-6 py-4"><div className="flex items-center gap-2"><MapPin className="w-4 h-4 text-slate-400" /><span className="font-medium text-slate-900">{item.region}</span></div></td><td className="px-6 py-4 text-slate-600">{item.parentRegion ?? "-"}</td><td className="px-6 py-4 text-right font-medium text-slate-900">{formatMoney(item.avgDeposit)}</td><td className="px-6 py-4 text-right text-slate-700">{formatMoney(item.avgMonthlyRent)}</td><td className="px-6 py-4 text-right"><span className="inline-flex px-3 py-1 text-sm font-medium bg-blue-50 text-blue-700">전세 {ratio.toFixed(1)}% / 월세 {(100 - ratio).toFixed(1)}%</span></td><td className="px-6 py-4 text-right text-slate-700">{formatPriceChange(previousTrend?.avgDeposit ?? 0, latestTrend?.avgDeposit ?? 0)}</td><td className="px-6 py-4 text-right text-slate-600">{item.transactions.toLocaleString("ko-KR")}건</td><td className="px-6 py-4 text-right text-slate-700">{topBand ? `${topBand.band} · ${formatMoney(topBand.avgDeposit)}` : "-"}</td></tr>; })}{filteredData.length === 0 && <tr><td className="px-6 py-10 text-center text-slate-500" colSpan={8}>검색 결과가 없습니다.</td></tr>}</tbody></table></div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ icon, title, value, helper, tone }: { icon: ReactNode; title: string; value: string; helper: string; tone: string }) {
  return <div className="bg-white border border-slate-200 p-6 shadow-sm"><div className="flex items-center gap-3 mb-3"><div className={`w-10 h-10 ${tone} flex items-center justify-center`}>{icon}</div><h3 className="font-medium text-slate-900">{title}</h3></div><div className="text-3xl font-bold text-slate-900 mb-1">{value}</div><p className="text-sm text-slate-500">{helper}</p></div>;
}

function ChartPanel({ title, children }: { title: string; children: ReactNode }) {
  return <div className="bg-white border border-slate-200 p-6 shadow-sm"><h3 className="font-semibold text-slate-900 mb-6">{title}</h3>{children}</div>;
}

function SummaryTable({ areaBands }: { areaBands: AreaSummary[] }) {
  return <div className="overflow-x-auto"><table className="w-full"><thead className="bg-slate-50"><tr><th className="px-4 py-3 text-left text-sm font-medium text-slate-900">면적대</th><th className="px-4 py-3 text-right text-sm font-medium text-slate-900">평균 보증금</th><th className="px-4 py-3 text-right text-sm font-medium text-slate-900">거래 건수</th></tr></thead><tbody className="divide-y divide-slate-200">{areaBands.map((item) => <tr key={item.band} className="hover:bg-slate-50 transition-colors"><td className="px-4 py-3 text-sm text-slate-900">{item.band}</td><td className="px-4 py-3 text-right text-sm font-medium text-slate-900">{formatMoney(item.avgDeposit)}</td><td className="px-4 py-3 text-right text-sm text-slate-600">{item.transactionCount.toLocaleString("ko-KR")}건</td></tr>)}</tbody></table></div>;
}
