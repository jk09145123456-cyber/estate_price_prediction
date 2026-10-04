package com.example.demo.dto;

public class PriceTrendPoint {

    private String year;
    private long averagePrice;
    private long transactionCount;

    public PriceTrendPoint(String year, long averagePrice, long transactionCount) {
        this.year = year;
        this.averagePrice = averagePrice;
        this.transactionCount = transactionCount;
    }

    public String getYear() {
        return year;
    }

    public long getAveragePrice() {
        return averagePrice;
    }

    public long getTransactionCount() {
        return transactionCount;
    }
}
