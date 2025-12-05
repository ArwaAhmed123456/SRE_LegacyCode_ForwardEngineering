package com.sgtech.pos.repository;

import com.sgtech.pos.model.UserRental;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;

public interface UserRentalRepository extends MongoRepository<UserRental, String> {
    List<UserRental> findByCustomerPhone(String customerPhone);
}
