package com.sgtech.pos.repository;

import com.sgtech.pos.model.Rental;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface RentalRepository extends MongoRepository<Rental, Integer> {
}
