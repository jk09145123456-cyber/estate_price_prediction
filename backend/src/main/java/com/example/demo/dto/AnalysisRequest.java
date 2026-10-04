package com.example.demo.dto;

public class AnalysisRequest {

    private String address;
    private String buildingType;
    private String area;
    private String landArea;
    private String deposit;
    private String mortgage;
    private String priorTenants;
    private String buildingAge;

    public String getAddress() {
        return address;
    }

    public String getBuildingType() {
        return buildingType;
    }

    public String getArea() {
        return area;
    }

    public String getLandArea() {
        return landArea;
    }

    public String getDeposit() {
        return deposit;
    }

    public String getMortgage() {
        return mortgage;
    }

    public String getPriorTenants() {
        return priorTenants;
    }

    public String getBuildingAge() {
        return buildingAge;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public void setBuildingType(String buildingType) {
        this.buildingType = buildingType;
    }

    public void setArea(String area) {
        this.area = area;
    }

    public void setLandArea(String landArea) {
        this.landArea = landArea;
    }

    public void setDeposit(String deposit) {
        this.deposit = deposit;
    }

    public void setMortgage(String mortgage) {
        this.mortgage = mortgage;
    }

    public void setPriorTenants(String priorTenants) {
        this.priorTenants = priorTenants;
    }

    public void setBuildingAge(String buildingAge) {
        this.buildingAge = buildingAge;
    }
}
