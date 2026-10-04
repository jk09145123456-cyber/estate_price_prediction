package com.example.demo.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Transaction {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String gu;
    private String dong;
    private String road;
    private String houseType;
    private Double totalArea;
    private Double landArea;
    private Integer buildYear;
    private Integer tradeYear;
    private Integer tradeMonth;
    private Integer tradeDay;
    private Long price;
}
