package com.sgtech.pos.model;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

@Document(collection = "employees")
public class Employee {
    @Id
    private String employeeId;
    private String role;
    private String firstName;
    private String lastName;
    private String password;

    public Employee() {}

    public Employee(String employeeId, String role, String firstName, String lastName, String password) {
        this.employeeId = employeeId;
        this.role = role;
        this.firstName = firstName;
        this.lastName = lastName;
        this.password = password;
    }

    // getters and setters
    public String getEmployeeId() { return employeeId; }
    public void setEmployeeId(String employeeId) { this.employeeId = employeeId; }
    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }
    public String getFirstName() { return firstName; }
    public void setFirstName(String firstName) { this.firstName = firstName; }
    public String getLastName() { return lastName; }
    public void setLastName(String lastName) { this.lastName = lastName; }
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
}
