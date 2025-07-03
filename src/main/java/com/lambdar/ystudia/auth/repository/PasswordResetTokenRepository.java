package com.lambdar.ystudia.auth.repository;

import com.lambdar.ystudia.auth.model.PasswordResetToken;
import com.lambdar.ystudia.user.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface PasswordResetTokenRepository extends JpaRepository<PasswordResetToken, Long> {
    Optional<PasswordResetToken> findByToken(String token);
    @Modifying
    @Query("DELETE FROM PasswordResetToken r WHERE r.user = :user")
    void deleteByUser(User user);
}
