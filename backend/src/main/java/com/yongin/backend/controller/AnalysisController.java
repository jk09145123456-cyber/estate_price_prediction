package com.yongin.backend.controller;

import com.yongin.backend.dto.analysis.AnalysisRequest;
import com.yongin.backend.dto.analysis.AnalysisResponse;
import com.yongin.backend.service.AnalysisService;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class AnalysisController {

    private final AnalysisService analysisService;

    public AnalysisController(AnalysisService analysisService) {
        this.analysisService = analysisService;
    }

    @PostMapping("/analyze")
    public AnalysisResponse analyze(@RequestBody AnalysisRequest request) {
        return analysisService.analyze(request);
    }
}
