package com.example.demo.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public class PricePredictionRequest {

    private String address;
    @JsonProperty("building_type")
    private String buildingType;

    @JsonProperty("total_area")
    private double totalArea;

    @JsonProperty("land_area")
    private double landArea;

    @JsonProperty("build_year")
    private int buildYear;

    @JsonProperty("contract_year")
    private int contractYear;

    @JsonProperty("contract_month")
    private int contractMonth;

    @JsonProperty("contract_day")
    private int contractDay;

    @JsonProperty("road_condition")
    private String roadCondition;

    public PricePredictionRequest(String address, String buildingType, double totalArea,
                                  double landArea, int buildYear, int contractYear,
                                  int contractMonth, int contractDay,
                                  String roadCondition) {
        this.address = address;
        this.buildingType = buildingType;
        this.totalArea = totalArea;
        this.landArea = landArea;
        this.buildYear = buildYear;
        this.contractYear = contractYear;
        this.contractMonth = contractMonth;
        this.contractDay = contractDay;
        this.roadCondition = roadCondition;
    }

    public String getAddress() {
        return address;
    }

    public String getBuildingType() {
        return buildingType;
    }

    public double getTotalArea() {
        return totalArea;
    }

    public double getLandArea() {
        return landArea;
    }

    public int getBuildYear() {
        return buildYear;
    }

    public int getContractYear() {
        return contractYear;
    }

    public int getContractMonth() {
        return contractMonth;
    }

    public int getContractDay() {
        return contractDay;
    }

    public String getRoadCondition() {
        return roadCondition;
    }
}
