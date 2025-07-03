package com.lambdar.ystudia.user.controller;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.lambdar.ystudia.user.dto.request.RoleRequest;
import com.lambdar.ystudia.dto.response.DataSaveMessage;
import com.lambdar.ystudia.dto.response.MessageResponse;
import com.lambdar.ystudia.user.dto.response.RoleResponse;
import com.lambdar.ystudia.user.service.RoleService;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("api/v1/role")
@RequiredArgsConstructor
public class RoleController {
    private final RoleService roleService;
    @PostMapping("/add")
    public ResponseEntity<DataSaveMessage<RoleResponse>> addRole(@Valid @RequestBody RoleRequest addRoleRequest){
        return ResponseEntity.ok(roleService.saveNavigationAlloc(addRoleRequest,null));
    }
    @GetMapping("/all")
    public ResponseEntity<List<RoleResponse>> getAllRole(){
        return ResponseEntity.ok(roleService.getAllRoles());
    }
    @GetMapping("/{roleId:\\d+}")
    public ResponseEntity<RoleResponse> getRole(@PathVariable Long roleId){
        return ResponseEntity.ok(roleService.getRole(roleId));
    }
    @PutMapping("/{roleId}")
    public ResponseEntity<DataSaveMessage<RoleResponse>> editRole(@Valid @RequestBody RoleRequest roleRequest,
                                                 @PathVariable Long roleId){
        return ResponseEntity.ok(roleService.saveNavigationAlloc(roleRequest, roleId));
    }
    @DeleteMapping("/{roleId}")
    public ResponseEntity<MessageResponse> deleteRole(@PathVariable Long roleId){
        return ResponseEntity.ok(roleService.deleteRole(roleId));
    }

}
