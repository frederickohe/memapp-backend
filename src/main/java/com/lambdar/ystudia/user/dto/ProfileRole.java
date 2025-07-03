package com.lambdar.ystudia.user.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class ProfileRole {
    private Long roleId;
    private String roleName;
    private String description;
}
