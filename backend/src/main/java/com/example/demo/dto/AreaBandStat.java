package com.example.demo.dto;

public class AreaBandStat {

    private String band;
    private long avgDeposit;
    private long transactionCount;

    public AreaBandStat(String band, long avgDeposit, long transactionCount) {
        this.band = band;
        this.avgDeposit = avgDeposit;
        this.transactionCount = transactionCount;
    }

    public String getBand() {
        return band;
    }

    public long getAvgDeposit() {
        return avgDeposit;
    }

    public long getTransactionCount() {
        return transactionCount;
    }
}
