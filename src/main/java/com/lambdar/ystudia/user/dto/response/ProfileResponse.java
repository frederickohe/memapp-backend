package com.lambdar.ystudia.user.dto.response;

import com.lambdar.ystudia.user.dto.ProfileRole;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

import com.lambdar.ystudia.features.courses.model.Course;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ProfileResponse {
    private Long id;
    private String email;
    private String firstName;
    private String lastName;
    private String phone;
    private String bio;
    private String city;
    private String enrolledCourseId;
    private String profileImageUrl;
    private List<Course> completedCourses;
    private ProfileRole role;
}