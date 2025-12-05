package com.sgtech.pos.repository;

import com.sgtech.pos.model.Product;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ProductRepository extends MongoRepository<Product, Long> {
    boolean existsByName(String name);
    List<Product> findByNameContainingIgnoreCase(String keyword);
}
