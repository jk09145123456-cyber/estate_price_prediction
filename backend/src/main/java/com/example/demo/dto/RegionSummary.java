package com.example.demo.dto;

public class RegionSummary {

    private String gu;
    private long count;
    private long averagePrice;
    private long minPrice;
    private long maxPrice;

    public RegionSummary(String gu, long count, long averagePrice, long minPrice, long maxPrice) {
        this.gu = gu;
        this.count = count;
        this.averagePrice = averagePrice;
        this.minPrice = minPrice;
        this.maxPrice = maxPrice;
    }

    public String getGu() {
        return gu;
    }

    public long getCount() {
        return count;
    }

    public long getAveragePrice() {
        return averagePrice;
    }

    public long getMinPrice() {
        return minPrice;
    }

    public long getMaxPrice() {
        return maxPrice;
    }
}