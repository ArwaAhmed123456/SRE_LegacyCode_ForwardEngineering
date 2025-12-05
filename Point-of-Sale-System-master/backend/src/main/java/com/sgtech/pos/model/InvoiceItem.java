package com.sgtech.pos.model;

public class InvoiceItem {
    private Integer itemId;
    private String itemName;
    private int quantity;
    private double price;

    public InvoiceItem() {}
    public InvoiceItem(Integer itemId, String itemName, int quantity, double price) {
        this.itemId = itemId; this.itemName = itemName; this.quantity = quantity; this.price = price;
    }
    public Integer getItemId() { return itemId; }
    public void setItemId(Integer itemId) { this.itemId = itemId; }
    public String getItemName() { return itemName; }
    public void setItemName(String itemName) { this.itemName = itemName; }
    public int getQuantity() { return quantity; }
    public void setQuantity(int quantity) { this.quantity = quantity; }
    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; }
}
