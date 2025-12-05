package com.sgtech.pos.model;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.util.ArrayList;
import java.util.List;

@Document(collection = "invoices")
public class Invoice {
    @Id
    private String id;
    private String createdAt;
    private Double totalWithTax;
    private List<InvoiceItem> items = new ArrayList<>();

    public Invoice() {}

    public Invoice(String createdAt) { this.createdAt = createdAt; }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    public Double getTotalWithTax() { return totalWithTax; }
    public void setTotalWithTax(Double totalWithTax) { this.totalWithTax = totalWithTax; }
    public List<InvoiceItem> getItems() { return items; }
    public void setItems(List<InvoiceItem> items) { this.items = items; }
}
