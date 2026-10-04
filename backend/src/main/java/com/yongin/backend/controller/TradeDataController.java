package com.yongin.backend.controller;

import com.yongin.backend.dto.RegionSummary;
import com.yongin.backend.dto.PriceTrendPoint;
import com.yongin.backend.dto.RegionalAnalysisStat;
import com.yongin.backend.dto.TradeData;
import com.yongin.backend.service.TradeDataService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/trades")
public class TradeDataController {

    private final TradeDataService tradeDataService;

    public TradeDataController(TradeDataService tradeDataService) {
        this.tradeDataService = tradeDataService;
    }

    @GetMapping
    public List<TradeData> getAllTrades() {
        return tradeDataService.getAllTrades();
    }

    @GetMapping("/summary")
    public List<RegionSummary> getRegionSummary() {
        return tradeDataService.getRegionSummary();
    }

    @GetMapping("/trend")
    public List<PriceTrendPoint> getPriceTrend() {
        return tradeDataService.getYearlyTrend();
    }

    @GetMapping("/regional-analysis")
    public List<RegionalAnalysisStat> getRegionalAnalysis() {
        return tradeDataService.getRegionalAnalysis();
    }
}
