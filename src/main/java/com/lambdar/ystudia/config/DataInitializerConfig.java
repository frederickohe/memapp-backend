package com.lambdar.ystudia.config;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

import org.springframework.boot.CommandLineRunner;
import org.springframework.core.io.ClassPathResource;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import com.lambdar.ystudia.repository.UserRoleRepository;
import com.lambdar.ystudia.user.model.User;
import com.lambdar.ystudia.user.model.UserRole;
import com.lambdar.ystudia.user.repository.UserRepository;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Component
@RequiredArgsConstructor
@Slf4j
public class DataInitializerConfig implements CommandLineRunner {
    private final UserRoleRepository userRoleRepository;
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JdbcTemplate jdbcTemplate;

    @Override
    public void run(String... args) throws Exception {
        log.info("Starting data initialization...");
        initializeRoles();
        initializeAdminUser();
        //runMigrationSQL();
        log.info("Data initialization completed successfully!");
    }

    public void runMigrationSQL(){
        ClassPathResource resource = new ClassPathResource("migration.sql");
        try (InputStream inputStream = resource.getInputStream();
             BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream))) {

            String sql = reader.lines().collect(Collectors.joining("\n"));
            jdbcTemplate.execute(sql);
            log.info("Migration file run!");
        } catch (IOException ex) {
            log.error("Error reading migration file: {}", ex.getMessage());
        } catch (Exception ex) {
            log.error("Error executing migration: {}", ex.getMessage());
        }
    }

    private void initializeRoles() {
        log.info("Initializing user roles...");

        List<String> roleNames = Arrays.asList("ADMIN", "STUDENT", "FACILITATOR", "SUPERADMIN");

        for (String roleName : roleNames) {
            if (!userRoleRepository.existsByRoleName(roleName)) {
                UserRole role = UserRole.builder()
                        .roleName(roleName)
                        .description(getRoleDescription(roleName))
                        .build();

                userRoleRepository.save(role);
                log.info("Created role: {}", roleName);
            } else {
                log.info("Role {} already exists, skipping...", roleName);
            }
        }
    }

    private void initializeAdminUser() {
        log.info("Initializing admin user...");

        String adminEmail = "admin@nexus-assets.nexus";

        if (!userRepository.existsByEmail(adminEmail)) {
            UserRole adminRole = userRoleRepository.findByRoleName("ADMIN")
                    .orElseThrow(() -> new RuntimeException("ADMIN role not found"));

            User adminUser = User.builder()
                    .email(adminEmail)
                    .hashedPassword(passwordEncoder.encode("passwordAdmin@123"))
                    .firstName("System")
                    .lastName("Administrator")
                    .phone("+1234567890")
                    .userRole(adminRole)
                    .enabled(true)
                    .createdAt(LocalDateTime.now())
                    .profileImageUrl("")
                    .bio("Default system administrator account")
                    .build();

            userRepository.save(adminUser);
            log.info("Created admin user with email: {} and password: Admin@123", adminEmail);
            log.warn("IMPORTANT: Please change the default admin password after first login!");
        } else {
            log.info("Admin user already exists, skipping...");
        }
    }

    private String getRoleDescription(String roleName) {
        return switch (roleName) {
            case "ADMIN" -> "Administrator with full system access";
            case "STUDENT" -> "Student with access to learning resources";
            case "FACILITATOR" -> "Teacher with access to teaching resources";
            case "SUPERADMIN" -> "Super administrator with ultimate system control";
            default -> "User role";
        };
    }
}