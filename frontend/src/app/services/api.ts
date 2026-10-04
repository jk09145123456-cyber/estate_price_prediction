const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8080/api";

export interface AnalysisRequest {
  address: string;
  buildingType: string;
  area: string;
  landArea: string;
  deposit: string;
  mortgage: string;
  priorTenants: string;
  buildingAge: string;
}

export interface AnalysisResult {
  riskLevel: string;
  recoveryRate: number;
  depositAmount: number;
  recoverableAmount: number;
  expectedAuctionPrice: number;
  mortgageAmount: number;
  priorTenantsAmount: number;
  auctionCost: number;
  smallTenantApplied: boolean;
  priorityRepaymentApplied: boolean;
  recoveryRuleMessage: string;
}

export interface RegionData {
  region: string;
  avgPrice: number;
  change: number;
  riskScore: number;
  transactions: number;
}

export interface TradeTrendPoint {
  year: string;
  averagePrice: number;
  transactionCount: number;
}

export interface TradeData {
  gu: string;
  dong: string;
  houseType: string;
  dealYear: number;
  price: number;
  monthlyRent: number;
  landArea: number;
  totalArea: number;
}

export interface AreaBandStat {
  band: string;
  avgDeposit: number;
  transactionCount: number;
}

export interface RegionalMonthlyTrendPoint {
  month: string;
  avgDeposit: number;
  transactionCount: number;
}

export interface RegionalAnalysisStat {
  region: string;
  parentRegion?: string;
  avgDeposit: number;
  avgMonthlyRent: number;
  transactions: number;
  jeonseCount: number;
  monthlyRentCount: number;
  areaBands: AreaBandStat[];
  monthlyTrend: RegionalMonthlyTrendPoint[];
}

export async function analyzeRisk(data: AnalysisRequest): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error("분석 요청에 실패했습니다.");
  }

  return await response.json();
}

export async function getTrades(): Promise<TradeData[]> {
  const response = await fetch(`${API_BASE_URL}/trades`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error("거래 데이터 조회에 실패했습니다.");
  }

  return await response.json();
}

export async function getRegionalAnalysis(): Promise<RegionalAnalysisStat[]> {
  const response = await fetch(`${API_BASE_URL}/trades/regional-analysis`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error("지역 분석 데이터 조회에 실패했습니다.");
  }

  return await response.json();
}

export async function getRegionData(): Promise<RegionData[]> {
  const response = await fetch(`${API_BASE_URL}/trades/summary`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error("지역 데이터 조회에 실패했습니다.");
  }

  const result = await response.json();

  return result.map((item: any) => ({
    region: item.gu,
    avgPrice: Math.round(item.averagePrice / 100000000),
    change: 0,
    riskScore: 75,
    transactions: item.count,
  }));
}

export async function getTradeTrend(): Promise<TradeTrendPoint[]> {
  const response = await fetch(`${API_BASE_URL}/trades/trend`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error("실거래 추이 조회에 실패했습니다.");
  }

  return await response.json();
}
