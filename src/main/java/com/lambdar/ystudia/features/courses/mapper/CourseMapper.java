package com.lambdar.ystudia.features.courses.mapper;

import com.lambdar.ystudia.features.courses.model.Course;
import com.lambdar.ystudia.features.courses.dto.CourseResponseDTO;

public class CourseMapper {
    public static CourseResponseDTO toDto(Course course) {
        CourseResponseDTO dto = new CourseResponseDTO();
        dto.setId(course.getId());
        dto.setTitle(course.getTitle());
        dto.setDescription(course.getDescription());
        dto.setInstructorName(course.getInstructor() != null ? course.getInstructor().getFullName() : null);
        dto.setCategory(course.getCategory());
        dto.setDifficultyLevel(course.getDifficultyLevel());
        dto.setDuration(course.getDuration());
        dto.setCreatedAt(course.getCreatedAt());
        dto.setUpdatedAt(course.getUpdatedAt());
        return dto;
    }
}
