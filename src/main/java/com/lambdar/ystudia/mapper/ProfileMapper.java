package com.lambdar.ystudia.mapper;

import com.lambdar.ystudia.user.dto.ProfileRole;
import com.lambdar.ystudia.user.dto.response.ProfileResponse;
import com.lambdar.ystudia.user.model.User;
import com.lambdar.ystudia.service.FileService;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class ProfileMapper {
    @Value("${app.base.url}")
    private String baseUrl;
    private final FileService fileService;
    public ProfileResponse mapToProfileResponseDto(User user) {
        return ProfileResponse.builder()
                .id(user.getId())
                .email(user.getEmail())
                .firstName(user.getFirstName())
                .lastName(user.getLastName())
                .phone(user.getPhone())
                .profileImageUrl(getProfileImg(user.getProfileImageUrl()))
                .bio(user.getBio())
                .city(user.getCity())
                .enrolledCourseId(user.getEnrolledCourseId() != null ? user.getEnrolledCourseId().toString() : null)
                .completedCourses(user.getCompletedCourses())
                .role(ProfileRole.builder()
                        .roleId(user.getUserRole().getRoleId())
                        .roleName(user.getUserRole().getRoleName())
                        .roleName(user.getUserRole().getDescription())
                        .build())
                .build();
    }
    private String getProfileImg(String dbUrl){
        if(dbUrl == null || dbUrl.isEmpty()){
            return String.format("%s/%s",baseUrl,"default/default-male.png");
        }
        return fileService.convertToSignUrl(dbUrl);
    }
}
