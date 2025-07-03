package com.lambdar.ystudia.user.dto;

import lombok.Data;

@Data
public class CreateUserWithRoleDTO {
    private String userName;
    private String firstName;
    private String lastName;
    private String email;
    private String phone;
    private boolean isActive = true;
    private String hashedPassword;
    private String role;

    public CreateUserWithRoleDTO(String userName, String firstName, String lastName, String email, String phone,
            boolean isActive, String hashedPassword, String role) {
        this.userName = userName;
        this.firstName = firstName;
        this.lastName = lastName;
        this.email = email;
        this.phone = phone;
        this.isActive = isActive;
        this.hashedPassword = hashedPassword;
        this.role = role;
    }


}
