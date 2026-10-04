package com.example.demo.dto;

public class MonthlyTrendPoint {

    private String month;
    private long avgDeposit;
    private long transactionCount;

    public MonthlyTrendPoint(String month, long avgDeposit, long transactionCount) {
        this.month = month;
        this.avgDeposit = avgDeposit;
        this.transactionCount = transactionCount;
    }

    public String getMonth() {
        return month;
    }

    public long getAvgDeposit() {
        return avgDeposit;
    }

    public long getTransactionCount() {
        return transactionCount;
    }
}
