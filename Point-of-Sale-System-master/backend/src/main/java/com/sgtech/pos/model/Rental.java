package com.sgtech.pos.model;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

@Document(collection = "rentals")
public class Rental {
    @Id
    private Integer rentalId;
    private String name;
    private double price;
    private int quantity;

    public Rental() {}

    public Rental(Integer rentalId, String name, double price, int quantity) {
        this.rentalId = rentalId;
        this.name = name;
        this.price = price;
        this.quantity = quantity;
    }

    // getters and setters
    public Integer getRentalId() { return rentalId; }
    public void setRentalId(Integer rentalId) { this.rentalId = rentalId; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; }
    public int getQuantity() { return quantity; }
    public void setQuantity(int quantity) { this.quantity = quantity; }
}
