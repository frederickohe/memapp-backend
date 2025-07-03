package com.lambdar.ystudia.user.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.util.List;

@Data
public class RoleRequest {
    @NotBlank(message = "role name cannot be blank")
    private String roleName;
    private String description;
    @Size(min = 1)
    private List<Long> accessibleNavigations;
}
