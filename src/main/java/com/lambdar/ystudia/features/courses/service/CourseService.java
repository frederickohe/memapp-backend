package com.lambdar.ystudia.features.courses.service;

import com.lambdar.ystudia.features.courses.dto.CourseRequestDTO;
import com.lambdar.ystudia.features.courses.dto.CourseResponseDTO;
import com.lambdar.ystudia.features.courses.model.Course;
import com.lambdar.ystudia.features.courses.repository.CourseRepository;
import com.lambdar.ystudia.features.courses.mapper.CourseMapper;
import com.lambdar.ystudia.user.model.User;
import com.lambdar.ystudia.user.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class CourseService {
    @Autowired
    private CourseRepository courseRepository;
    @Autowired
    private UserRepository userRepository;

    public CourseResponseDTO createCourse(CourseRequestDTO dto) {
        if (courseRepository.existsByTitle(dto.getTitle())) {
            throw new RuntimeException("Course title already exists");
        }
        User instructor = userRepository.findById(dto.getInstructorId())
                .orElseThrow(() -> new RuntimeException("Instructor not found"));
        Course course = Course.builder()
                .title(dto.getTitle())
                .description(dto.getDescription())
                .instructor(instructor)
                .category(dto.getCategory())
                .difficultyLevel(dto.getDifficultyLevel())
                .duration(dto.getDuration())
                .build();
        course = courseRepository.save(course);
        return CourseMapper.toDto(course);
    }

    public List<CourseResponseDTO> getAllCourses() {
        return courseRepository.findAll().stream()
                .map(CourseMapper::toDto)
                .collect(Collectors.toList());
    }

    public Optional<CourseResponseDTO> getCourseById(Long id) {
        return courseRepository.findById(id).map(CourseMapper::toDto);
    }

    public void deleteCourse(Long id) {
        courseRepository.deleteById(id);
    }

    public Optional<CourseResponseDTO> updateCourse(Long id, CourseRequestDTO dto) {
        return courseRepository.findById(id).map(course -> {
            course.setTitle(dto.getTitle());
            course.setDescription(dto.getDescription());
            course.setCategory(dto.getCategory());
            course.setDifficultyLevel(dto.getDifficultyLevel());
            course.setDuration(dto.getDuration());
            if (dto.getInstructorId() != null) {
                User instructor = userRepository.findById(dto.getInstructorId())
                        .orElseThrow(() -> new RuntimeException("Instructor not found"));
                course.setInstructor(instructor);
            }
            return CourseMapper.toDto(courseRepository.save(course));
        });
    }
}
