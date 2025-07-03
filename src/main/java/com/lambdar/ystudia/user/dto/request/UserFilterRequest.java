package com.lambdar.ystudia.user.dto.request;

import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

@Data
public class UserFilterRequest {
    private List<String> roles;
    private List<Long> locationIds;
    private LocalDateTime createdAfter;
    private LocalDateTime createdBefore;
    private Boolean enabled;
}
