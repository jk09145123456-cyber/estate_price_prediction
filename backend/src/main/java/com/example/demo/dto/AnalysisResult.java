package com.example.demo.dto;

public class AnalysisResult {

    private String riskLevel;
    private int recoveryRate;
    private long depositAmount;
    private long recoverableAmount;
    private long expectedAuctionPrice;
    private long mortgageAmount;
    private long priorTenantsAmount;
    private long auctionCost;
    private boolean smallTenantApplied;
    private boolean priorityRepaymentApplied;
    private String recoveryRuleMessage;

    public AnalysisResult(String riskLevel, int recoveryRate, long depositAmount,
                          long recoverableAmount, long expectedAuctionPrice,
                          long mortgageAmount, long priorTenantsAmount, long auctionCost,
                          boolean smallTenantApplied, boolean priorityRepaymentApplied,
                          String recoveryRuleMessage) {

        this.riskLevel = riskLevel;
        this.recoveryRate = recoveryRate;
        this.depositAmount = depositAmount;
        this.recoverableAmount = recoverableAmount;
        this.expectedAuctionPrice = expectedAuctionPrice;
        this.mortgageAmount = mortgageAmount;
        this.priorTenantsAmount = priorTenantsAmount;
        this.auctionCost = auctionCost;
        this.smallTenantApplied = smallTenantApplied;
        this.priorityRepaymentApplied = priorityRepaymentApplied;
        this.recoveryRuleMessage = recoveryRuleMessage;
    }

    public String getRiskLevel() {
        return riskLevel;
    }

    public int getRecoveryRate() {
        return recoveryRate;
    }

    public long getDepositAmount() {
        return depositAmount;
    }

    public long getRecoverableAmount() {
        return recoverableAmount;
    }

    public long getExpectedAuctionPrice() {
        return expectedAuctionPrice;
    }

    public long getMortgageAmount() {
        return mortgageAmount;
    }

    public long getPriorTenantsAmount() {
        return priorTenantsAmount;
    }

    public long getAuctionCost() {
        return auctionCost;
    }

    public boolean isSmallTenantApplied() {
        return smallTenantApplied;
    }

    public boolean isPriorityRepaymentApplied() {
        return priorityRepaymentApplied;
    }

    public String getRecoveryRuleMessage() {
        return recoveryRuleMessage;
    }
}
