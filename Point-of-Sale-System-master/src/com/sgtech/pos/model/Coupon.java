package com.sgtech.pos.model;

public class Coupon {
    private String code;
    private boolean used;
    public Coupon() {}
    public String getCode() { return code; }
    public void setCode(String code) { this.code = code; }
    public boolean isUsed() { return used; }
    public void setUsed(boolean used) { this.used = used; }
}
