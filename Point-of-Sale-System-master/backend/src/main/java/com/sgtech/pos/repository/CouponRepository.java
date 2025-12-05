package com.sgtech.pos.repository;

import com.sgtech.pos.model.Coupon;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface CouponRepository extends MongoRepository<Coupon, String> {
    Coupon findByCode(String code);
}
