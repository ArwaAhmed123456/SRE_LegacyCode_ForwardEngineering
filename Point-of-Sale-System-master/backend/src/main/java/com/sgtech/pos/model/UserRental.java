package com.sgtech.pos.model;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

@Document(collection = "user_rentals")
public class UserRental {
    @Id
    private String id;
    private String customerPhone;
    private Integer itemId;
    private String rentedDate;
    private boolean returned;

    public UserRental() {}

    public UserRental(String customerPhone, Integer itemId, String rentedDate, boolean returned) {
        this.customerPhone = customerPhone;
        this.itemId = itemId;
        this.rentedDate = rentedDate;
        this.returned = returned;
    }

    // getters and setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getCustomerPhone() { return customerPhone; }
    public void setCustomerPhone(String customerPhone) { this.customerPhone = customerPhone; }
    public Integer getItemId() { return itemId; }
    public void setItemId(Integer itemId) { this.itemId = itemId; }
    public String getRentedDate() { return rentedDate; }
    public void setRentedDate(String rentedDate) { this.rentedDate = rentedDate; }
    public boolean isReturned() { return returned; }
    public void setReturned(boolean returned) { this.returned = returned; }
}
