package com.lambdar.ystudia.user.service;

import com.lambdar.ystudia.user.dto.request.RoleRequest;
import com.lambdar.ystudia.dto.response.DataSaveMessage;
import com.lambdar.ystudia.dto.response.MessageResponse;
import com.lambdar.ystudia.user.dto.response.RoleResponse;
import com.lambdar.ystudia.exception.DuplicateResourceException;
import com.lambdar.ystudia.exception.ResourceNotFoundException;
import com.lambdar.ystudia.mapper.RoleMapper;
import com.lambdar.ystudia.user.model.UserRole;
import com.lambdar.ystudia.repository.UserRoleRepository;
import jakarta.annotation.Nullable;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;



import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
public class RoleService {
    private final UserRoleRepository userRoleRepository;
    private final RoleMapper roleMapper;
    public DataSaveMessage<RoleResponse> saveNavigationAlloc(RoleRequest roleRequest, @Nullable Long roleId){
        UserRole userRole = roleMapper.toUserRole(roleRequest);
        if(roleId!=null){
            if(!userRoleRepository.existsById(roleId)){
                throw new ResourceNotFoundException("RoleId does not exist!");
            }else if(!userRoleRepository.existsByRoleIdAndRoleName(roleId,roleRequest.getRoleName())
                    &&userRoleRepository.existsByRoleName(roleRequest.getRoleName())){
                throw new DuplicateResourceException("Role name already exists!");
            }else{
                userRole.setRoleId(roleId);
            }
        }else{
            if (userRoleRepository.existsByRoleName(roleRequest.getRoleName())){
                throw new DuplicateResourceException("Role name already exists!");
            }
        }
        userRoleRepository.save(userRole);
        return  DataSaveMessage.<RoleResponse>builder()
                .message(String.format("Role successfully %1$s!",
                        roleId==null?"saved":"edited"))
                .data(roleMapper.toRoleResponse(userRole))
                .build();
    }
    @Transactional
    public RoleResponse getRole(Long roleId){
        UserRole userRole = userRoleRepository.findById(roleId)
                .orElseThrow(()->new ResourceNotFoundException("Role not found"));
        return roleMapper.toRoleResponse(userRole);
    }
    public List<RoleResponse> getAllRoles(){
        List<RoleResponse> list = new ArrayList<>();
        userRoleRepository.findAll().forEach((userRole ->
            list.add(RoleResponse.builder()
                            .roleId(userRole.getRoleId())
                            .roleName(userRole.getRoleName())
                            .description(userRole.getDescription())
                            .build()
                    )));
        return list;
    }
    @Transactional
    public MessageResponse deleteRole(Long roleId){
        UserRole userRole = userRoleRepository.findById(roleId).orElseThrow(()->
                new ResourceNotFoundException("Role not found!"));
        userRoleRepository.delete(userRole);
        return MessageResponse.builder().message("Role successfully deleted!").build();
    }
}
