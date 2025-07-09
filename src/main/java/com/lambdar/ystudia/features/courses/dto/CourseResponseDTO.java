package com.lambdar.ystudia.features.courses.dto;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class CourseResponseDTO {
    private Long id;
    private String title;
    private String description;
    private String instructorName;
    private String category;
    private String difficultyLevel;
    private int duration;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
