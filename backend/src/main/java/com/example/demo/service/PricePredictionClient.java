package com.example.demo.service;

import com.example.demo.dto.PricePredictionRequest;
import com.example.demo.dto.PricePredictionResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

@Service
public class PricePredictionClient {

    private final RestClient restClient;

    public PricePredictionClient(@Value("${ai.api.base-url:http://localhost:8000}") String baseUrl) {
        this.restClient = RestClient.builder()
                .baseUrl(baseUrl)
                .build();
    }

    public PricePredictionResponse predict(PricePredictionRequest request) {
        return restClient.post()
                .uri("/predict")
                .body(request)
                .retrieve()
                .body(PricePredictionResponse.class);
    }
}
