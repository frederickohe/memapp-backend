package com.lambdar.ystudia.util;

import com.lambdar.ystudia.user.model.User;
import com.lambdar.ystudia.user.model.UserRole;
import jakarta.persistence.criteria.Join;
import jakarta.persistence.criteria.Predicate;
import org.springframework.data.jpa.domain.Specification;  // <-- import this

import java.time.LocalDateTime;
import java.util.List;

public class UserSpecification {

    public static Specification<User> filterUsers(List<String> roles, List<Long> locationIds,
                                                  LocalDateTime createdAfter, LocalDateTime createdBefore,
                                                  Boolean enabled) {
        return (root, query, cb) -> {
            Predicate predicate = cb.conjunction();

            if (roles != null && !roles.isEmpty()) {
                Join<User, UserRole> roleJoin = root.join("userRole");
                predicate = cb.and(predicate, roleJoin.get("roleName").in(roles));
            }

            if (locationIds != null && !locationIds.isEmpty()) {
                Join<Object, Object> locationJoin = root.join("location");
                predicate = cb.and(predicate, locationJoin.get("locationId").in(locationIds));
            }

            if (createdAfter != null) {
                predicate = cb.and(predicate, cb.greaterThanOrEqualTo(root.get("createdAt"), createdAfter));
            }

            if (createdBefore != null) {
                predicate = cb.and(predicate, cb.lessThanOrEqualTo(root.get("createdAt"), createdBefore));
            }

            if (enabled != null) {
                predicate = cb.and(predicate, cb.equal(root.get("enabled"), enabled));
            }

            return predicate;
        };
    }
}
