package com.lambdar.ystudia.repository;

import com.lambdar.ystudia.user.model.UserRole;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface UserRoleRepository extends JpaRepository<UserRole,Long> {
    boolean existsByRoleName(String roleName);
    boolean existsByRoleIdAndRoleName(Long roleId, String roleName);
    Optional<UserRole> findByRoleName(String roleName);
}
