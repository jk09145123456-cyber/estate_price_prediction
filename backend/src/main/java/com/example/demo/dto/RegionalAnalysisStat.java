package com.example.demo.dto;

import java.util.List;

public class RegionalAnalysisStat {

    private String region;
    private String parentRegion;
    private long avgDeposit;
    private long avgMonthlyRent;
    private long transactions;
    private long jeonseCount;
    private long monthlyRentCount;
    private List<AreaBandStat> areaBands;
    private List<MonthlyTrendPoint> monthlyTrend;

    public RegionalAnalysisStat(
            String region,
            String parentRegion,
            long avgDeposit,
            long avgMonthlyRent,
            long transactions,
            long jeonseCount,
            long monthlyRentCount,
            List<AreaBandStat> areaBands,
            List<MonthlyTrendPoint> monthlyTrend
    ) {
        this.region = region;
        this.parentRegion = parentRegion;
        this.avgDeposit = avgDeposit;
        this.avgMonthlyRent = avgMonthlyRent;
        this.transactions = transactions;
        this.jeonseCount = jeonseCount;
        this.monthlyRentCount = monthlyRentCount;
        this.areaBands = areaBands;
        this.monthlyTrend = monthlyTrend;
    }

    public String getRegion() {
        return region;
    }

    public String getParentRegion() {
        return parentRegion;
    }

    public long getAvgDeposit() {
        return avgDeposit;
    }

    public long getAvgMonthlyRent() {
        return avgMonthlyRent;
    }

    public long getTransactions() {
        return transactions;
    }

    public long getJeonseCount() {
        return jeonseCount;
    }

    public long getMonthlyRentCount() {
        return monthlyRentCount;
    }

    public List<AreaBandStat> getAreaBands() {
        return areaBands;
    }

    public List<MonthlyTrendPoint> getMonthlyTrend() {
        return monthlyTrend;
    }
}
