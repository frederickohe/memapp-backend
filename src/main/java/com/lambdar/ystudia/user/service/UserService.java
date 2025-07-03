package com.lambdar.ystudia.user.service;

import com.lambdar.ystudia.user.dto.request.UserFilterRequest;
import com.lambdar.ystudia.dto.response.MessageResponse;
import com.lambdar.ystudia.user.dto.response.UserResponse;
import com.lambdar.ystudia.exception.ResourceNotFoundException;
import com.lambdar.ystudia.exception.UnAuthenticatedException;
import com.lambdar.ystudia.mapper.UserMapper;
import com.lambdar.ystudia.user.repository.UserRepository;
import com.lambdar.ystudia.repository.UserRoleRepository;
import com.lambdar.ystudia.util.UserSpecification;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import com.lambdar.ystudia.user.model.User;
import com.lambdar.ystudia.user.model.UserRole;

import java.util.List;

import static com.lambdar.ystudia.util.Constants.USER_NOT_FOUND_WITH_ID;


@Service
@RequiredArgsConstructor
@Slf4j
public class UserService {

    private final UserRepository userRepository;
    private final UserMapper userMapper;
    private final UserRoleRepository userRoleRepository;


    public UserResponse getUserById(Long id) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException(USER_NOT_FOUND_WITH_ID + id));
        return userMapper.toUserResponse(user);
    }

    public UserResponse getUserByEmail(String email) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with email: " + email));
        return userMapper.toUserResponse(user);
    }


    public void setUserEnabledStatus(Long id, boolean enabled) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException(USER_NOT_FOUND_WITH_ID + id));

        try {
            user.setEnabled(enabled);
            userRepository.save(user);
            log.info("User {}: {}", (enabled ? "enabled" : "disabled"), user.getEmail());
        } catch (Exception e) {
            log.error("Failed to {} user with id: {}", (enabled ? "enable" : "disable"), id, e);
            throw new UnAuthenticatedException("Failed to " + (enabled ? "enable" : "disable") + " user: " + e.getMessage());
        }
    }


    public void deleteUser(Long id) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException(USER_NOT_FOUND_WITH_ID + id));
        try {
            userRepository.delete(user);
            log.info("User deleted: {}", user.getEmail());
        } catch (Exception e) {
            log.error("Failed to delete user with id: {}", id, e);
            throw new RuntimeException("Failed to delete user: " + e.getMessage());
        }
    }

    @Transactional
    public MessageResponse updateUserRole(Long userId, Long roleId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + userId));

        UserRole newRole = userRoleRepository.findById(roleId)
                .orElseThrow(() -> new ResourceNotFoundException("Role not found with id: " + roleId));

        user.setUserRole(newRole);
        userRepository.save(user);

        return MessageResponse.builder()
                .message(String.format("User role updated to '%s' successfully", newRole.getRoleName()))
                .build();
    }


    public List<UserResponse> filterUsers(UserFilterRequest request) {
        List<User> users = userRepository.findAll(
                UserSpecification.filterUsers(
                        request.getRoles(),
                        request.getLocationIds(),
                        request.getCreatedAfter(),
                        request.getCreatedBefore(),
                        request.getEnabled()
                )
        );
        return users.stream()
                .map(userMapper::toUserResponse)
                .toList();
    }


}
