package com.lambdar.ystudia.user.service;

import java.io.IOException;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import com.lambdar.ystudia.user.dto.request.ProfileUpdateRequest;
import com.lambdar.ystudia.auth.dto.request.ChangePasswordRequest;
import com.lambdar.ystudia.user.dto.response.ProfileResponse;
import com.lambdar.ystudia.mapper.ProfileMapper;
import com.lambdar.ystudia.service.FileService;
import com.lambdar.ystudia.user.model.User;
import com.lambdar.ystudia.user.repository.UserRepository;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class ProfileService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final ProfileMapper profileMapper;
    private final FileService fileService;

    public ProfileResponse getCurrentUserProfile() {
        User user = getCurrentUser();
        return profileMapper.mapToProfileResponseDto(user);
    }

    public ProfileResponse updateProfile(ProfileUpdateRequest request) {
        User user = getCurrentUser();

        user.setFirstName(request.getFirstName());
        user.setLastName(request.getLastName());
        user.setPhone(request.getPhone());
        user.setEmail(request.getEmail());
        user.setBio(request.getBio());

        User savedUser = userRepository.save(user);
        log.info("Profile updated for user: {}", user.getEmail());

        return profileMapper.mapToProfileResponseDto(savedUser);
    }

    public ProfileResponse uploadProfileImage(MultipartFile file) throws IOException {
        User user = getCurrentUser();

        // Validate file
        if (file.isEmpty()) {
            throw new IllegalArgumentException("File is empty");
        }

        if (!isValidImageFile(file)) {
            throw new IllegalArgumentException("Invalid file type. Only JPG, JPEG, PNG, and GIF are allowed");
        }

        if (file.getSize() > 5 * 1024 * 1024) { // 5MB limit
            throw new IllegalArgumentException("File size exceeds 5MB limit");
        }

        // Delete old profile image if exists
        if (user.getProfileImageUrl() != null) {
            fileService.deleteFile(user.getProfileImageUrl());
        }

        // Save file
        String newFilename = fileService.uploadFile(file.getInputStream(), FileService.GCSSubFolder.PROFILE
                ,file.getOriginalFilename());

        // Update user profile image URL
        user.setProfileImageUrl(newFilename);

        User savedUser = userRepository.save(user);
        log.info("Profile image updated for user: {}", user.getEmail());

        return profileMapper.mapToProfileResponseDto(savedUser);
    }

    public void deleteProfileImage() {
        User user = getCurrentUser();

        if (user.getProfileImageUrl() != null) {
            fileService.deleteFile(user.getProfileImageUrl());
            user.setProfileImageUrl(null);
            userRepository.save(user);
            log.info("Profile image deleted for user: {}", user.getEmail());
        }
    }

    public void changePassword(ChangePasswordRequest request) {
        User user = getCurrentUser();

        // Verify current password
        if (!passwordEncoder.matches(request.getCurrentPassword(), user.getHashedPassword())) {
            throw new IllegalArgumentException("Current password is incorrect");
        }

        // Verify new password confirmation
        if (!request.getNewPassword().equals(request.getConfirmPassword())) {
            throw new IllegalArgumentException("New password and confirmation do not match");
        }

        // Update password
        user.setHashedPassword(passwordEncoder.encode(request.getNewPassword()));
        userRepository.save(user);

        log.info("Password changed for user: {}", user.getEmail());
    }

    private User getCurrentUser() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String userEmail = authentication.getName();

        return userRepository.findByEmail(userEmail)
                .orElseThrow(() -> new RuntimeException("User not found"));
    }


    private boolean isValidImageFile(MultipartFile file) {
        String contentType = file.getContentType();
        return contentType != null && (
                contentType.equals("image/jpeg") ||
                        contentType.equals("image/jpg") ||
                        contentType.equals("image/png") ||
                        contentType.equals("image/gif")
        );
    }

}