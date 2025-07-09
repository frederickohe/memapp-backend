package com.lambdar.ystudia.features.courses.dto;

import lombok.Data;

@Data
public class CourseRequestDTO {
    private String title;
    private String description;
    private Long instructorId;
    private String category;
    private String difficultyLevel;
    private int duration;
}
