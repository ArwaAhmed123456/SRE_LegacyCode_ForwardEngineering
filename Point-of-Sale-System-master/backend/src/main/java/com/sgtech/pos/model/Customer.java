package com.sgtech.pos.model;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

@Document(collection = "customers")
public class Customer {
    @Id
    private String phone;

    public Customer() {}

    public Customer(String phone) {
        this.phone = phone;
    }

    // getters and setters
    public String getPhone() { return phone; }
    public void setPhone(String phone) { this.phone = phone; }
}
