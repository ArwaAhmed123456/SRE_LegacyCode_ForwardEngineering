package com.sgtech.pos.model;

import java.util.ArrayList;
import java.util.List;

public class Invoice {
    private String id;
    private String createdAt;
    private Double totalWithTax;
    private List<InvoiceItem> items = new ArrayList<>();

    public Invoice() {}
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    public Double getTotalWithTax() { return totalWithTax; }
    public void setTotalWithTax(Double totalWithTax) { this.totalWithTax = totalWithTax; }
    public List<InvoiceItem> getItems() { return items; }
    public void setItems(List<InvoiceItem> items) { this.items = items; }
}
