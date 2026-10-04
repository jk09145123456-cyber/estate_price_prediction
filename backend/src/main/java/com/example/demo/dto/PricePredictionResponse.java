package com.example.demo.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public class PricePredictionResponse {

    @JsonProperty("predicted_price_manwon")
    private double predictedPriceManwon;

    @JsonProperty("predicted_price_text")
    private String predictedPriceText;

    public double getPredictedPriceManwon() {
        return predictedPriceManwon;
    }

    public void setPredictedPriceManwon(double predictedPriceManwon) {
        this.predictedPriceManwon = predictedPriceManwon;
    }

    public String getPredictedPriceText() {
        return predictedPriceText;
    }

    public void setPredictedPriceText(String predictedPriceText) {
        this.predictedPriceText = predictedPriceText;
    }
}
