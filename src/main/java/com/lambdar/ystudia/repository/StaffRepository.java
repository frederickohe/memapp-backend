package com.lambdar.ystudia.repository;

import com.lambdar.ystudia.user.model.Staff;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.repository.CrudRepository;

public interface StaffRepository extends JpaRepository<Staff,Long> {
}
