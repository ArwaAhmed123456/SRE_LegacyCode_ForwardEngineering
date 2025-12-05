package com.sgtech.pos.controller;

import com.sgtech.pos.model.Employee;
import com.sgtech.pos.repository.EmployeeRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/employees")
public class EmployeeController {
    private final EmployeeRepository repo;
    public EmployeeController(EmployeeRepository repo) { this.repo = repo; }

    @GetMapping
    public List<Employee> all() { return repo.findAll(); }

    @GetMapping("/{id}")
    public Employee get(@PathVariable String id) { return repo.findById(id).orElse(null); }

    @PostMapping
    public Employee create(@RequestBody Employee e) { return repo.save(e); }

    @PutMapping("/{id}")
    public Employee update(@PathVariable String id, @RequestBody Employee e) { e.setEmployeeId(id); return repo.save(e); }

    @DeleteMapping("/{id}")
    public void delete(@PathVariable String id) { repo.deleteById(id); }
}
