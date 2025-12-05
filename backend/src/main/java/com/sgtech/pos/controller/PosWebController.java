package com.sgtech.pos.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class PosWebController {

    @GetMapping("/")
    public String home(Model model) {
        model.addAttribute("title", "Point of Sale System");
        return "index";
    }

    @GetMapping("/login")
    public String login(Model model) {
        model.addAttribute("title", "Login");
        return "login";
    }

    @GetMapping("/cashier")
    public String cashier(Model model) {
        model.addAttribute("title", "Cashier Dashboard");
        return "cashier";
    }

    @GetMapping("/admin")
    public String admin(Model model) {
        model.addAttribute("title", "Admin Panel");
        return "admin";
    }
}
