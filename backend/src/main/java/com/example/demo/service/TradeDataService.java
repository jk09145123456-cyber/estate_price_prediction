package com.example.demo.service;

import com.example.demo.dto.AreaBandStat;
import com.example.demo.dto.MonthlyTrendPoint;
import com.example.demo.dto.PriceTrendPoint;
import com.example.demo.dto.RegionalAnalysisStat;
import com.example.demo.dto.RegionSummary;
import com.example.demo.dto.TradeData;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class TradeDataService {

    private final JdbcTemplate jdbcTemplate;

    public TradeDataService(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public List<TradeData> getAllTrades() {
        String sql = """
                SELECT '처인구' AS gu,
                       `시군구` AS sigungu,
                       `주택유형` AS house_type,
                       `전월세구분` AS rent_type,
                       `계약년월` AS contract_year_month,
                       `보증금(만원)` AS deposit_manwon,
                       `월세금(만원)` AS monthly_rent_manwon,
                       `계약면적(㎡)` AS contract_area
                FROM cheoin_data

                UNION ALL

                SELECT '기흥구' AS gu,
                       `시군구` AS sigungu,
                       `주택유형` AS house_type,
                       `전월세구분` AS rent_type,
                       `계약년월` AS contract_year_month,
                       `보증금(만원)` AS deposit_manwon,
                       `월세금(만원)` AS monthly_rent_manwon,
                       `계약면적(㎡)` AS contract_area
                FROM giheung_data

                UNION ALL

                SELECT '수지구' AS gu,
                       `시군구` AS sigungu,
                       `주택유형` AS house_type,
                       `전월세구분` AS rent_type,
                       `계약년월` AS contract_year_month,
                       `보증금(만원)` AS deposit_manwon,
                       `월세금(만원)` AS monthly_rent_manwon,
                       `계약면적(㎡)` AS contract_area
                FROM suji_data
                """;

        return jdbcTemplate.query(sql, (rs, rowNum) -> {
            TradeData tradeData = new TradeData();
            String dealYearMonth = cleanText(rs.getString("contract_year_month"));

            tradeData.setGu(cleanText(rs.getString("gu")));
            tradeData.setDong(getDongFromAddress(rs.getString("sigungu")));
            tradeData.setHouseType(cleanText(rs.getString("house_type")));
            tradeData.setRentType(cleanText(rs.getString("rent_type")));
            tradeData.setDealYearMonth(dealYearMonth);
            tradeData.setDealYear(getYearFromDealYearMonth(dealYearMonth));
            tradeData.setPrice(parseManwonToWon(rs.getString("deposit_manwon")));
            tradeData.setMonthlyRent(parseManwonToWon(rs.getString("monthly_rent_manwon")));
            tradeData.setTotalArea(parseDouble(rs.getString("contract_area")));
            tradeData.setLandArea(0.0);

            return tradeData;
        });
    }

    public List<RegionSummary> getRegionSummary() {
        List<TradeData> trades = getAllTrades();
        List<RegionSummary> result = new ArrayList<>();

        result.add(makeSummary("수지구", trades));
        result.add(makeSummary("기흥구", trades));
        result.add(makeSummary("처인구", trades));

        return result;
    }

    public List<PriceTrendPoint> getYearlyTrend() {
        List<TradeData> trades = getAllTrades();

        return trades.stream()
                .collect(Collectors.groupingBy(
                        TradeData::getDealYear,
                        LinkedHashMap::new,
                        Collectors.toList()
                ))
                .entrySet()
                .stream()
                .filter(entry -> entry.getKey() > 0)
                .sorted(Map.Entry.comparingByKey())
                .map(entry -> {
                    List<TradeData> yearlyTrades = entry.getValue();
                    long totalDeposit = yearlyTrades.stream().mapToLong(TradeData::getPrice).sum();
                    long count = yearlyTrades.size();

                    return new PriceTrendPoint(
                            String.valueOf(entry.getKey()),
                            count > 0 ? totalDeposit / count : 0,
                            count
                    );
                })
                .collect(Collectors.toList());
    }

    public List<RegionalAnalysisStat> getRegionalAnalysis() {
        return getAllTrades().stream()
                .collect(Collectors.groupingBy(
                        trade -> trade.getGu() + "::" + trade.getDong(),
                        LinkedHashMap::new,
                        Collectors.toList()
                ))
                .values()
                .stream()
                .map(this::makeRegionalAnalysisStat)
                .sorted(Comparator
                        .comparing((RegionalAnalysisStat stat) ->
                                stat.getParentRegion() == null ? stat.getRegion() : stat.getParentRegion())
                        .thenComparing(RegionalAnalysisStat::getRegion))
                .collect(Collectors.toList());
    }

    private RegionSummary makeSummary(String gu, List<TradeData> trades) {
        List<TradeData> filtered = trades.stream()
                .filter(trade -> trade.getGu().equals(gu))
                .collect(Collectors.toList());

        long count = filtered.size();
        long totalPrice = filtered.stream().mapToLong(TradeData::getPrice).sum();
        long minPrice = filtered.stream().mapToLong(TradeData::getPrice).min().orElse(0L);
        long maxPrice = filtered.stream().mapToLong(TradeData::getPrice).max().orElse(0L);

        return new RegionSummary(
                gu,
                count,
                count > 0 ? totalPrice / count : 0,
                minPrice,
                maxPrice
        );
    }

    private RegionalAnalysisStat makeRegionalAnalysisStat(List<TradeData> trades) {
        TradeData first = trades.get(0);
        long totalDeposit = trades.stream().mapToLong(TradeData::getPrice).sum();
        long monthlyRentCount = trades.stream().filter(this::isMonthlyRentTrade).count();
        long jeonseCount = trades.size() - monthlyRentCount;
        long totalMonthlyRent = trades.stream()
                .filter(this::isMonthlyRentTrade)
                .mapToLong(TradeData::getMonthlyRent)
                .sum();

        long transactions = trades.size();

        return new RegionalAnalysisStat(
                first.getDong(),
                first.getDong().equals(first.getGu()) ? null : first.getGu(),
                transactions > 0 ? totalDeposit / transactions : 0,
                monthlyRentCount > 0 ? totalMonthlyRent / monthlyRentCount : 0,
                transactions,
                jeonseCount,
                monthlyRentCount,
                makeAreaBands(trades),
                makeMonthlyTrend(trades)
        );
    }

    private List<AreaBandStat> makeAreaBands(List<TradeData> trades) {
        return trades.stream()
                .collect(Collectors.groupingBy(
                        trade -> getAreaBand(trade.getTotalArea()),
                        LinkedHashMap::new,
                        Collectors.toList()
                ))
                .entrySet()
                .stream()
                .map(entry -> {
                    List<TradeData> bandTrades = entry.getValue();
                    long totalDeposit = bandTrades.stream().mapToLong(TradeData::getPrice).sum();
                    long count = bandTrades.size();

                    return new AreaBandStat(
                            entry.getKey(),
                            count > 0 ? totalDeposit / count : 0,
                            count
                    );
                })
                .sorted(Comparator.comparingInt(stat -> getAreaBandOrder(stat.getBand())))
                .collect(Collectors.toList());
    }

    private List<MonthlyTrendPoint> makeMonthlyTrend(List<TradeData> trades) {
        return trades.stream()
                .filter(trade -> trade.getDealYearMonth() != null && !trade.getDealYearMonth().isBlank())
                .collect(Collectors.groupingBy(
                        TradeData::getDealYearMonth,
                        LinkedHashMap::new,
                        Collectors.toList()
                ))
                .entrySet()
                .stream()
                .map(entry -> {
                    List<TradeData> monthlyTrades = entry.getValue();
                    long totalDeposit = monthlyTrades.stream().mapToLong(TradeData::getPrice).sum();
                    long count = monthlyTrades.size();

                    return new MonthlyTrendPoint(
                            entry.getKey(),
                            count > 0 ? totalDeposit / count : 0,
                            count
                    );
                })
                .sorted(Comparator.comparing(MonthlyTrendPoint::getMonth))
                .collect(Collectors.toList());
    }

    private boolean isMonthlyRentTrade(TradeData trade) {
        String rentType = trade.getRentType();

        if (rentType != null && rentType.contains("월세")) {
            return true;
        }

        return trade.getMonthlyRent() > 0;
    }

    private String getDongFromAddress(String address) {
        String cleanAddress = cleanText(address);

        if (cleanAddress.isBlank()) {
            return "";
        }

        String[] addressParts = cleanAddress.split("\\s+");
        return addressParts[addressParts.length - 1];
    }

    private int getYearFromDealYearMonth(String dealYearMonth) {
        if (dealYearMonth == null || dealYearMonth.length() < 4) {
            return 0;
        }

        return parseInt(dealYearMonth.substring(0, 4));
    }

    private long parseManwonToWon(String value) {
        String cleanValue = normalizeNumber(value);

        if (cleanValue.isBlank()) {
            return 0L;
        }

        return Long.parseLong(cleanValue) * 10_000L;
    }

    private double parseDouble(String value) {
        String cleanValue = normalizeNumber(value);

        if (cleanValue.isBlank()) {
            return 0.0;
        }

        return Double.parseDouble(cleanValue);
    }

    private int parseInt(String value) {
        String cleanValue = normalizeNumber(value);

        if (cleanValue.isBlank()) {
            return 0;
        }

        return Integer.parseInt(cleanValue);
    }

    private String normalizeNumber(String value) {
        if (value == null) {
            return "";
        }

        String cleanValue = value.replace(",", "").trim();
        return cleanValue.equals("-") ? "" : cleanValue;
    }

    private String cleanText(String value) {
        return value == null ? "" : value.trim();
    }

    private String getAreaBand(double area) {
        if (area <= 60) {
            return "60㎡ 이하";
        }

        if (area <= 85) {
            return "60~85㎡";
        }

        if (area <= 102) {
            return "85~102㎡";
        }

        return "102㎡ 초과";
    }

    private int getAreaBandOrder(String band) {
        return switch (band) {
            case "60㎡ 이하" -> 0;
            case "60~85㎡" -> 1;
            case "85~102㎡" -> 2;
            case "102㎡ 초과" -> 3;
            default -> 4;
        };
    }
}
