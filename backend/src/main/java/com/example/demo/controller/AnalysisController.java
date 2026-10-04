package com.example.demo.controller;

import com.example.demo.dto.AnalysisRequest;
import com.example.demo.dto.AnalysisResult;
import com.example.demo.dto.PricePredictionRequest;
import com.example.demo.dto.PricePredictionResponse;
import com.example.demo.service.PricePredictionClient;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;

@RestController
@RequestMapping("/api")
public class AnalysisController {

    private static final long FALLBACK_EXPECTED_AUCTION_PRICE = 650_000_000L;
    private static final long AUCTION_COST = 13_000_000L;
    private static final long SMALL_DEPOSIT_LIMIT = 140_000_000L;
    private static final long PRIORITY_REPAYMENT = 48_000_000L;
    private static final double LIQUIDATION_RATE = 0.85;

    private final PricePredictionClient pricePredictionClient;

    public AnalysisController(PricePredictionClient pricePredictionClient) {
        this.pricePredictionClient = pricePredictionClient;
    }

    @PostMapping("/analyze")
    public AnalysisResult analyze(@RequestBody AnalysisRequest request) {
        long deposit = parseMoney(request.getDeposit());
        long mortgage = parseMoney(request.getMortgage());
        long priorTenants = parseMoney(request.getPriorTenants());

        long expectedAuctionPrice = predictExpectedAuctionPrice(request);

        long remainingAfterAuction =
                expectedAuctionPrice
                        - mortgage
                        - priorTenants
                        - AUCTION_COST;

        long recoverableAmount = calculateRecoverableAmount(deposit, remainingAfterAuction);
        int recoveryRate = deposit > 0 ? (int) (recoverableAmount * 100L / deposit) : 0;
        String riskLevel = classifyRisk(recoveryRate);
        boolean smallTenantApplied = deposit > 0 && deposit <= SMALL_DEPOSIT_LIMIT;
        boolean priorityRepaymentApplied = deposit > 0 && deposit <= PRIORITY_REPAYMENT;
        String recoveryRuleMessage = buildRecoveryRuleMessage(smallTenantApplied, priorityRepaymentApplied);

        return new AnalysisResult(
                riskLevel,
                recoveryRate,
                deposit,
                recoverableAmount,
                expectedAuctionPrice,
                mortgage,
                priorTenants,
                AUCTION_COST,
                smallTenantApplied,
                priorityRepaymentApplied,
                recoveryRuleMessage
        );
    }

    private long predictExpectedAuctionPrice(AnalysisRequest request) {
        try {
            int buildingAgeInput = parseInt(request.getBuildingAge(), 0);
            int currentYear = LocalDate.now().getYear();
            // 프론트엔드는 건축년도(예: 2020)를 전송 — 나이(연수)가 아님
            int buildYear = (buildingAgeInput >= 1800 && buildingAgeInput <= currentYear)
                    ? buildingAgeInput
                    : currentYear;

            PricePredictionRequest predictionRequest = new PricePredictionRequest(
                    request.getAddress(),
                    request.getBuildingType(),
                    parseDouble(request.getArea(), 1.0),
                    parseDouble(request.getLandArea(), parseDouble(request.getArea(), 1.0)),
                    buildYear,
                    LocalDate.now().getYear(),
                    LocalDate.now().getMonthValue(),
                    LocalDate.now().getDayOfMonth(),
                    "기타"
            );

            PricePredictionResponse response = pricePredictionClient.predict(predictionRequest);

            if (response != null && response.getPredictedPriceManwon() > 0) {
                return (long)(response.getPredictedPriceManwon() * 10_000L * LIQUIDATION_RATE);
            }
        } catch (Exception e) {
            System.out.println("AI price prediction failed. Using fallback auction price.");
        }

        return FALLBACK_EXPECTED_AUCTION_PRICE;
    }

    private long calculateRecoverableAmount(long deposit, long remainingAfterAuction) {
        long recoverableAmount;

        if (deposit >= SMALL_DEPOSIT_LIMIT) {
            recoverableAmount = remainingAfterAuction;
        } else if (deposit <= PRIORITY_REPAYMENT) {
            recoverableAmount = deposit;
        } else {
            long excessDeposit = deposit - PRIORITY_REPAYMENT;
            long excessRecoverable = Math.min(remainingAfterAuction, excessDeposit);
            recoverableAmount = PRIORITY_REPAYMENT + excessRecoverable;
        }

        recoverableAmount = Math.min(recoverableAmount, deposit);
        recoverableAmount = Math.max(recoverableAmount, 0);

        return recoverableAmount;
    }

    private String classifyRisk(int recoveryRate) {
        if (recoveryRate >= 90) {
            return "안전";
        }

        if (recoveryRate >= 60) {
            return "주의";
        }

        return "위험";
    }

    private String buildRecoveryRuleMessage(boolean smallTenantApplied, boolean priorityRepaymentApplied) {
        if (priorityRepaymentApplied) {
            return "소액임차인 최우선변제 대상입니다. 우선변제 한도 범위에서 회수 금액을 계산합니다.";
        }

        if (smallTenantApplied) {
            return "소액임차인 적용 구간입니다. 우선변제 대상 여부와 경매 잔여금을 함께 반영해 회수 금액을 계산합니다.";
        }

        return "일반 임차인 기준으로 경매 잔여금과 선순위 채권을 반영해 회수 금액을 계산합니다.";
    }

    private long parseMoney(String value) {
        if (value == null || value.isBlank()) {
            return 0L;
        }

        return Long.parseLong(value.replace(",", "").trim());
    }

    private double parseDouble(String value, double defaultValue) {
        if (value == null || value.isBlank()) {
            return defaultValue;
        }

        return Double.parseDouble(value.replace(",", "").trim());
    }

    private int parseInt(String value, int defaultValue) {
        if (value == null || value.isBlank()) {
            return defaultValue;
        }

        return Integer.parseInt(value.replace(",", "").trim());
    }
}
