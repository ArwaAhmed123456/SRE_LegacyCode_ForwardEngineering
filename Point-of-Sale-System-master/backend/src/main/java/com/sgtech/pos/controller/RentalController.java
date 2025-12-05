package com.sgtech.pos.controller;

import com.sgtech.pos.model.Rental;
import com.sgtech.pos.repository.RentalRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/rentals")
public class RentalController {
    private final RentalRepository repo;
    public RentalController(RentalRepository repo) { this.repo = repo; }

    @GetMapping
    public List<Rental> all() { return repo.findAll(); }

    @GetMapping("/{id}")
    public Rental get(@PathVariable Integer id) { return repo.findById(id).orElse(null); }

    @PostMapping
    public Rental create(@RequestBody Rental r) { return repo.save(r); }

    @PutMapping("/{id}")
    public Rental update(@PathVariable Integer id, @RequestBody Rental r) { r.setRentalId(id); return repo.save(r); }

    @DeleteMapping("/{id}")
    public void delete(@PathVariable Integer id) { repo.deleteById(id); }
}
