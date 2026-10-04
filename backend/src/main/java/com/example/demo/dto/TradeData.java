package com.example.demo.dto;

public class TradeData {

    private String gu;
    private String dong;
    private String houseType;
    private String rentType;
    private String dealYearMonth;
    private int dealYear;
    private long price;
    private long monthlyRent;
    private double landArea;
    private double totalArea;

    public String getGu() {
        return gu;
    }

    public void setGu(String gu) {
        this.gu = gu;
    }

    public String getDong() {
        return dong;
    }

    public void setDong(String dong) {
        this.dong = dong;
    }

    public String getHouseType() {
        return houseType;
    }

    public void setHouseType(String houseType) {
        this.houseType = houseType;
    }

    public String getRentType() {
        return rentType;
    }

    public void setRentType(String rentType) {
        this.rentType = rentType;
    }

    public String getDealYearMonth() {
        return dealYearMonth;
    }

    public void setDealYearMonth(String dealYearMonth) {
        this.dealYearMonth = dealYearMonth;
    }

    public int getDealYear() {
        return dealYear;
    }

    public void setDealYear(int dealYear) {
        this.dealYear = dealYear;
    }

    public long getPrice() {
        return price;
    }

    public void setPrice(long price) {
        this.price = price;
    }

    public long getMonthlyRent() {
        return monthlyRent;
    }

    public void setMonthlyRent(long monthlyRent) {
        this.monthlyRent = monthlyRent;
    }

    public double getLandArea() {
        return landArea;
    }

    public void setLandArea(double landArea) {
        this.landArea = landArea;
    }

    public double getTotalArea() {
        return totalArea;
    }

    public void setTotalArea(double totalArea) {
        this.totalArea = totalArea;
    }
}
