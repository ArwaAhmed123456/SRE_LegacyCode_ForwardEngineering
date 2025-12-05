package com.sgtech.pos.model;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

@Document(collection = "coupons")
public class Coupon {
    @Id
    private String id;
    private String code;
    private boolean used;

    public Coupon() {}

    public Coupon(String code, boolean used) {
        this.code = code;
        this.used = used;
    }

    // getters and setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getCode() { return code; }
    public void setCode(String code) { this.code = code; }
    public boolean isUsed() { return used; }
    public void setUsed(boolean used) { this.used = used; }
}
