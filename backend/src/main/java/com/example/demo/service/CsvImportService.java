package com.example.demo.service;

import com.example.demo.entity.Transaction;
import com.example.demo.repository.TransactionRepository;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

@Service
@RequiredArgsConstructor
public class CsvImportService {
    private final TransactionRepository transactionRepository;

    @PostConstruct
    public void init() {
        try {
            ClassPathResource resource = new ClassPathResource("transactions.csv");
            BufferedReader reader = new BufferedReader(
                new InputStreamReader(resource.getInputStream(), StandardCharsets.UTF_8)
            );
            reader.readLine();
            String line;
            while ((line = reader.readLine()) != null) {
                String[] s = line.split(",");
                Transaction t = Transaction.builder()
                    .gu(s[0]).dong(s[1]).road(s[2]).houseType(s[3])
                    .totalArea(Double.parseDouble(s[4]))
                    .landArea(Double.parseDouble(s[5]))
                    .buildYear(Integer.parseInt(s[6]))
                    .tradeYear(Integer.parseInt(s[7]))
                    .tradeMonth(Integer.parseInt(s[8]))
                    .tradeDay(Integer.parseInt(s[9]))
                    .price(Long.parseLong(s[10]))
                    .build();
                transactionRepository.save(t);
            }
            System.out.println("✅ DB 적재 완료!");
        } catch (Exception e) { e.printStackTrace(); }
    }
}
