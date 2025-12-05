package com.sgtech.pos.controller;

import com.sgtech.pos.model.UserRental;
import com.sgtech.pos.repository.UserRentalRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/user-rentals")
public class UserRentalController {
    private final UserRentalRepository repo;
    public UserRentalController(UserRentalRepository repo) { this.repo = repo; }

    @GetMapping
    public List<UserRental> all() { return repo.findAll(); }

    @GetMapping("/customer/{phone}")
    public List<UserRental> getByCustomer(@PathVariable String phone) { return repo.findByCustomerPhone(phone); }

    @PostMapping
    public UserRental create(@RequestBody UserRental ur) { return repo.save(ur); }

    @DeleteMapping("/{id}")
    public void delete(@PathVariable String id) { repo.deleteById(id); }
}
