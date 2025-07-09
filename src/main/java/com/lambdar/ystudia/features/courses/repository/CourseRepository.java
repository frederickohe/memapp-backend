package com.lambdar.ystudia.features.courses.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.lambdar.ystudia.features.courses.model.Course;

public interface CourseRepository extends JpaRepository<Course, Long> {
    boolean existsByTitle(String title);
}
