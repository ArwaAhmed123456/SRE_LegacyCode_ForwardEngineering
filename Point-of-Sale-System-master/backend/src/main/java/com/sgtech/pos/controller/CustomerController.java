package com.sgtech.pos.controller;

import com.sgtech.pos.model.Customer;
import com.sgtech.pos.repository.CustomerRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/customers")
public class CustomerController {
    private final CustomerRepository repo;
    public CustomerController(CustomerRepository repo) { this.repo = repo; }

    @GetMapping
    public List<Customer> all() { return repo.findAll(); }

    @GetMapping("/{phone}")
    public Customer get(@PathVariable String phone) { return repo.findById(phone).orElse(null); }

    @PostMapping
    public Customer create(@RequestBody Customer c) { return repo.save(c); }

    @PutMapping("/{phone}")
    public Customer update(@PathVariable String phone, @RequestBody Customer c) { c.setPhone(phone); return repo.save(c); }

    @DeleteMapping("/{phone}")
    public void delete(@PathVariable String phone) { repo.deleteById(phone); }
}
