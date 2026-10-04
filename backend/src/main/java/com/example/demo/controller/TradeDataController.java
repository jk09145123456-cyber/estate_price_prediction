package com.example.demo.controller;

import com.example.demo.dto.RegionSummary;
import com.example.demo.dto.PriceTrendPoint;
import com.example.demo.dto.RegionalAnalysisStat;
import com.example.demo.dto.TradeData;
import com.example.demo.service.TradeDataService;
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
