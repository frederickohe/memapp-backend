package com.lambdar.ystudia.user.dto.response;

import com.lambdar.ystudia.user.model.UserRole;
import lombok.Builder;
import lombok.Data;

import java.time.LocalDate;

@Data
@Builder
public class StaffResponse {

    private String staffID;

    private String firstName;


    private String lastName;

    private UserRole userRole;

    private String contactNo;

    private String alternateContactNo;

    private String address;
    private String city;
    private String countryID;
    private String nationalID;

    private LocalDate dateOfBirth;
}
