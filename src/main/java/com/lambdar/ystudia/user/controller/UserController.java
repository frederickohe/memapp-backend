package com.lambdar.ystudia.user.controller;

import java.time.LocalDateTime;
import java.util.List;

import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import com.lambdar.ystudia.dto.response.MessageResponse;
import com.lambdar.ystudia.user.dto.request.UserFilterRequest;
import com.lambdar.ystudia.user.dto.response.UserResponse;
import com.lambdar.ystudia.user.service.UserService;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("api/v1/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @GetMapping("/me")
    @ResponseStatus(HttpStatus.OK)
    public UserResponse getCurrentUser(@AuthenticationPrincipal UserDetails userDetails) {
        return userService.getUserByEmail(userDetails.getUsername());
    }

    @GetMapping("/me1")
    @ResponseStatus(HttpStatus.OK)
    public UserDetails getCurrentUser1(@AuthenticationPrincipal UserDetails userDetails) {
        return userDetails;
    }


    @GetMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    @ResponseStatus(HttpStatus.OK)
    public UserResponse getUserById(@PathVariable Long id) {
        return userService.getUserById(id);
    }

    @PutMapping("/{id}/status")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Void> updateUserStatus(@PathVariable Long id, @RequestParam boolean enabled) {
        userService.setUserEnabledStatus(id, enabled);
        return ResponseEntity.ok().build();
    }
    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        userService.deleteUser(id);
        return ResponseEntity.noContent().build();
    }

    @GetMapping
    @PreAuthorize("hasRole('ADMIN')")
    @ResponseStatus(HttpStatus.OK)
    public List<UserResponse> filterUsers(
            @RequestParam(required = false) List<String> roles,
            @RequestParam(required = false) List<Long> locationIds,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime createdAfter,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime createdBefore,
            @RequestParam(required = false) Boolean enabled
    ) {
        UserFilterRequest request = new UserFilterRequest();
        request.setRoles(roles);
        request.setLocationIds(locationIds);
        request.setCreatedAfter(createdAfter);
        request.setCreatedBefore(createdBefore);
        request.setEnabled(enabled);

        return userService.filterUsers(request);
    }
    @PutMapping("/{userId}/role/{roleId}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<MessageResponse> updateUserRole(@PathVariable Long userId, @PathVariable Long roleId) {
        MessageResponse response = userService.updateUserRole(userId, roleId);
        return ResponseEntity.ok(response);
    }

}
