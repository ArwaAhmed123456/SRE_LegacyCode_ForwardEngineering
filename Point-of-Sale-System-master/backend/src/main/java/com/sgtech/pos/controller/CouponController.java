package com.sgtech.pos.controller;

import com.sgtech.pos.model.Coupon;
import com.sgtech.pos.repository.CouponRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/coupons")
public class CouponController {
    private final CouponRepository repo;
    public CouponController(CouponRepository repo) { this.repo = repo; }

    @GetMapping
    public List<Coupon> all() { return repo.findAll(); }

    @GetMapping("/code/{code}")
    public Coupon getByCode(@PathVariable String code) { return repo.findByCode(code); }

    @PostMapping
    public Coupon create(@RequestBody Coupon c) { return repo.save(c); }

    @PutMapping("/{id}")
    public Coupon update(@PathVariable String id, @RequestBody Coupon c) { c.setId(id); return repo.save(c); }

    @DeleteMapping("/{id}")
    public void delete(@PathVariable String id) { repo.deleteById(id); }
}
