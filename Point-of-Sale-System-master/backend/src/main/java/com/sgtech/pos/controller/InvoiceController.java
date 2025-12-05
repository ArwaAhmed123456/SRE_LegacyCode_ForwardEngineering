package com.sgtech.pos.controller;

import com.sgtech.pos.model.Invoice;
import com.sgtech.pos.repository.InvoiceRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/invoices")
public class InvoiceController {
    private final InvoiceRepository repo;
    public InvoiceController(InvoiceRepository repo) { this.repo = repo; }

    @GetMapping
    public List<Invoice> all() { return repo.findAll(); }

    @PostMapping
    public Invoice create(@RequestBody Invoice invoice) { return repo.save(invoice); }
}
