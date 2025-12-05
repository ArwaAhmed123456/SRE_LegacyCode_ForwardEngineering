package com.sgtech.pos.controller;

import com.sgtech.pos.model.Item;
import com.sgtech.pos.repository.ItemRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/items")
public class ItemController {
    private final ItemRepository repo;
    public ItemController(ItemRepository repo) { this.repo = repo; }

    @GetMapping
    public List<Item> all() { return repo.findAll(); }

    @PostMapping
    public Item create(@RequestBody Item item) { return repo.save(item); }

    @PutMapping("/{id}")
    public Item update(@PathVariable Integer id, @RequestBody Item item) { item.setItemId(id); return repo.save(item); }

    @DeleteMapping("/{id}")
    public void delete(@PathVariable Integer id) { repo.deleteById(id); }
}
