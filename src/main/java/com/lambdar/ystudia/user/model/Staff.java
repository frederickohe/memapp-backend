package com.lambdar.ystudia.user.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;

import com.lambdar.ystudia.user.model.UserRole;

@Data
@Entity
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class Staff {
    @Id
    private Long staffID;

    @NotBlank(message = "first name cannot be blank")
    @Pattern(regexp = "^[aA-zZ]+$",message = "first name must have at least one letter")
    private String firstName;

    @NotBlank(message = "last name cannot be blank")
    @Pattern(regexp = "^[aA-zZ]+$",message = "last name must have at least one letter")
    private String lastName;


    @JoinColumn(name = "user_role")
    @ManyToOne
    private UserRole userRole;

    @Column(name = "contact_no1")
    private String contactNo;
    @Column(name = "contact_no2")
    private String alternateContactNo;

    private String address;
    private String city;
    private String countryID;
    private String nationalID;

    @FutureOrPresent(message = "invalid date, date is future")
    private LocalDate dateOfBirth;
}
