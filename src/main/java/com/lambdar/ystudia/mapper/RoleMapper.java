package com.lambdar.ystudia.mapper;

import com.lambdar.ystudia.user.dto.request.RoleRequest;
import com.lambdar.ystudia.user.dto.response.RoleResponse;
import com.lambdar.ystudia.user.model.UserRole;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class RoleMapper {
    public UserRole toUserRole(RoleRequest roleRequest){
        UserRole userRole = new UserRole();
        userRole.setRoleName(roleRequest.getRoleName());
        userRole.setDescription(roleRequest.getDescription());
        return UserRole.builder()
                .roleName(roleRequest.getRoleName())
                .description(roleRequest.getDescription())
                .build();
    }
    public RoleResponse toRoleResponse(UserRole userRole){
        return RoleResponse.builder()
                .roleId(userRole.getRoleId())
                .roleName(userRole.getRoleName())
                .description(userRole.getDescription())
                .build();
    }
}
